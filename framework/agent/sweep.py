"""Verify every committed locator class against a live cluster in one pass.

Locator drift is silent: a selector that stopped matching only surfaces when some
test finally exercises it, which may be never. This sweep probes all of them on
demand, so a console or operator upgrade produces a drift report instead of a
surprise months later.

Seed the fixtures first - detail pages render nothing without a resource, and list
toolbars do not render in the empty state:

    oc apply -f .agent/sweep/seed.yaml

Usage:
    python -m framework.agent.sweep [--map PATH] [--only SUBSTR] [--headed] [--json OUT]
"""

import argparse
import asyncio
import importlib
import json
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import yaml

from framework.agent import locator_registry as registry
from framework.agent import outcomes
from framework.agent.audit_map import audit
from framework.agent.verify_locators import detect_version, verify_pages

MAP_PATH = Path(__file__).resolve().parents[2] / ".agent" / "sweep" / "page_map.yaml"


def load_class(path: str) -> type:
    module_name, class_name = path.split(":")
    return getattr(importlib.import_module(module_name), class_name)


def constants(cls: type) -> Dict[str, str]:
    """The locator constants on a class: public upper-case string attributes.

    Leading-underscore names are selector fragments meant to be composed into another
    selector, not probed on their own - one such fragment is a bare `:not(...)` chain
    that matches every element on the page.
    """
    return {
        n: getattr(cls, n)
        for n in dir(cls)
        if n.isupper() and not n.startswith("_") and isinstance(getattr(cls, n), str)
    }


def is_skipped(name: str, patterns: List[str]) -> bool:
    return any(fnmatch(name, p) for p in patterns)


def build_specs(
    page_map: Dict[str, Any], only: Optional[str], namespace: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
    namespace = namespace or page_map["namespace"]
    profiles = page_map["ready_profiles"]
    global_skip = page_map.get("always_skip") or []
    specs: List[Dict[str, Any]] = []
    skipped: Dict[str, List[str]] = {}

    for entry in page_map["pages"]:
        key = entry["key"]
        if only and only not in key:
            continue
        cls = load_class(entry["locators"])
        patterns = global_skip + list(entry.get("skip") or [])
        many = set(entry.get("many") or [])
        samples = entry.get("samples") or {}

        candidates: Dict[str, Any] = {}
        skip: List[str] = []
        for name, selector in constants(cls).items():
            if is_skipped(name, patterns):
                skip.append(name)
                continue
            if name in samples or name in many:
                candidates[name] = {"selector": selector}
                if name in samples:
                    candidates[name]["sample"] = samples[name]
                if name in many:
                    candidates[name]["expect"] = "many"
            else:
                candidates[name] = selector

        if skip:
            skipped[key] = sorted(skip)
        specs.append(
            {
                "page_key": key,
                "locator_class": entry["locators"],
                "url": entry["url"].format(ns=namespace),
                "ready": profiles[entry["ready"]],
                "conditional": sorted(set(entry.get("conditional") or [])),
                "candidates": candidates,
            }
        )
    return specs, skipped


def classify(
    results: Dict[str, Dict[str, Any]],
    conditional: Optional[Set[str]] = None,
) -> Tuple[List[str], List[str], List[str]]:
    """Split results into (missing, ambiguous, hidden) problem buckets.

    A `conditional` locator depends on runtime state this sweep does not control - a
    "Running" badge on a finished run, an empty-state message on a populated list. Its
    absence proves nothing, so it is never counted as drift.
    """
    cond = conditional or set()
    missing = [n for n, r in results.items() if r["match_count"] == 0 and n not in cond]
    ambiguous = [n for n, r in results.items() if r["match_count"] > 1 and not r["expect_many"]]
    hidden = [n for n, r in results.items() if r["usable"] and r["visible_count"] == 0]
    return missing, ambiguous, hidden


def make_printer(
    conditional_by_key: Dict[str, Set[str]],
) -> Callable[[str, Dict[str, Dict[str, Any]], Optional[str]], None]:
    def print_page(key: str, results: Dict[str, Dict[str, Any]], error: Optional[str]) -> None:
        _print_page(key, results, error, conditional_by_key.get(key, set()))

    return print_page


def _print_page(key: str, results: Dict[str, Dict[str, Any]], error: Optional[str], conditional: Set[str]) -> None:
    if error:
        print(f"  {key:<34} UNREACHABLE  {error.split('(')[0].strip()}")
        return
    missing, ambiguous, hidden = classify(results, conditional)
    ok = len(results) - len(missing) - len(ambiguous)
    flag = "OK  " if not (missing or ambiguous) else "DRIFT"
    note = ""
    if missing:
        note += f"  missing={len(missing)}"
    if ambiguous:
        note += f"  ambiguous={len(ambiguous)}"
    if hidden:
        note += f"  hidden={len(hidden)}"
    print(f"  {flag} {key:<34} {ok}/{len(results)}{note}")


def summarise(
    pages: Dict[str, Dict[str, Any]],
    specs: List[Dict[str, Any]],
    skipped: Dict[str, List[str]],
    version: str,
) -> int:
    by_key = {s["page_key"]: s for s in specs}
    total = broken = 0
    drifted: List[Tuple[str, str, str, str]] = []
    unreachable: List[str] = []
    weak_ready: List[Tuple[str, List[str]]] = []
    hidden_only: List[Tuple[str, List[str]]] = []

    for key, entry in pages.items():
        if entry["error"]:
            unreachable.append(key)
            continue
        if entry.get("recovered_on_recheck"):
            weak_ready.append((key, entry["recovered_on_recheck"]))
        results = entry["results"]
        total += len(results)
        conditional = set(by_key[key]["conditional"])
        missing, ambiguous, hidden = classify(results, conditional)
        unexpected_hidden = [n for n in hidden if n not in conditional]
        if unexpected_hidden:
            hidden_only.append((key, unexpected_hidden))
        cls = by_key[key]["locator_class"].split(":")[-1]
        for name in missing:
            drifted.append((cls, name, results[name]["selector"], "matches nothing"))
        for name in ambiguous:
            drifted.append((cls, name, results[name]["selector"], f"{results[name]['match_count']} matches"))
        broken += len(missing) + len(ambiguous)

    print(f"\n{'=' * 78}")
    print(f"SWEEP SUMMARY   version={version}")
    print(f"{'=' * 78}")
    print(f"  pages swept     {len(pages) - len(unreachable)}/{len(pages)}")
    print(f"  locators probed {total}")
    print(f"  drifted         {broken}")
    print(f"  skipped         {sum(len(v) for v in skipped.values())} (need an interaction first)")

    _print_weak_ready(weak_ready)
    _print_hidden(hidden_only)
    _print_unreachable(unreachable, by_key)
    _print_drifted(drifted)

    return 1 if (drifted or unreachable or weak_ready) else 0


def _print_weak_ready(weak_ready: List[Tuple[str, List[str]]]) -> None:
    if not weak_ready:
        return
    print(f"\nWEAK ready SELECTOR ({len(weak_ready)} page(s)) - these locators only matched")
    print("on a second read, so the page was still painting when first probed. Fix the")
    print("page map: point `ready` at the element the probes actually need.")
    for key, names in weak_ready:
        print(f"  {key:<34} {', '.join(names[:5])}{' ...' if len(names) > 5 else ''}")


def _print_hidden(hidden_only: List[Tuple[str, List[str]]]) -> None:
    if not hidden_only:
        return
    total = sum(len(v) for _, v in hidden_only)
    print(f"\nPRESENT BUT NOT VISIBLE ({total}) - these resolve, so they are not drift, but any")
    print("click or visibility assertion on them will fail. Mark them conditional if that is")
    print("expected, otherwise the locator is pointing at the wrong element.")
    for key, names in hidden_only:
        print(f"  {key:<34} {', '.join(names[:5])}{' ...' if len(names) > 5 else ''}")


def _print_unreachable(unreachable: List[str], by_key: Dict[str, Dict[str, Any]]) -> None:
    if not unreachable:
        return
    print(f"\nUNREACHABLE PAGES ({len(unreachable)}) - seed missing, or the route changed:")
    for key in unreachable:
        print(f"  {key:<34} {by_key[key]['url']}")


def _print_drifted(drifted: List[Tuple[str, str, str, str]]) -> None:
    if not drifted:
        print("\nNo drift found.")
        return
    print(f"\nDRIFTED LOCATORS ({len(drifted)}):")
    current = ""
    for cls, name, selector, reason in drifted:
        if cls != current:
            print(f"\n  {cls}")
            current = cls
        print(f"    {name:<36} {reason}")
        print(f"      {selector}")


def drifted_count(pages: Dict[str, Dict[str, Any]], specs: List[Dict[str, Any]]) -> int:
    by_key = {s_["page_key"]: s_ for s_ in specs}
    total = 0
    for key, entry in pages.items():
        if entry["error"]:
            continue
        missing, ambiguous, _ = classify(entry["results"], set(by_key[key]["conditional"]))
        total += len(missing) + len(ambiguous)
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=MAP_PATH, help="Page map YAML")
    parser.add_argument("--only", help="Only sweep pages whose key contains this substring")
    parser.add_argument(
        "--namespace",
        help=(
            "Override the seeded namespace. Use a fresh name if this one was recently "
            "torn down: after a delete/recreate under the same name the console serves "
            "stale watch entries and lists resources that no longer exist."
        ),
    )
    parser.add_argument("--headed", action="store_true", help="Show the browser")
    parser.add_argument("--skip-audit", action="store_true", help="Sweep even if the page map fails its audit")
    parser.add_argument("--json", type=Path, help="Write the full result set here")
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not record passing locators. Saving is the default: a verification that is "
        "thrown away has to be repeated, so the registry never accumulates.",
    )
    args = parser.parse_args()

    if not args.skip_audit and audit(args.map) != 0:
        print(
            "\nRefusing to sweep: a page-map entry points at the wrong page, so correct "
            "locators would be reported as drift.\nFix the mapping, or pass --skip-audit.",
            file=sys.stderr,
        )
        return 2

    page_map = yaml.safe_load(args.map.read_text())
    specs, skipped = build_specs(page_map, args.only, args.namespace)
    version = detect_version()

    print(f"Sweeping {len(specs)} pages against {version} ...\n")
    conditional_by_key = {s_["page_key"]: set(s_["conditional"]) for s_ in specs}
    pages = asyncio.run(verify_pages(specs, args.headed, on_page=make_printer(conditional_by_key)))

    exit_code = summarise(pages, specs, skipped, version)

    if args.json:
        args.json.write_text(json.dumps({"version": version, "pages": pages, "skipped": skipped}, indent=2))
        print(f"\nFull results written to {args.json}")

    if not args.no_save:
        by_key = {s["page_key"]: s for s in specs}
        saved = 0
        for key, entry in pages.items():
            good = {n: r for n, r in entry["results"].items() if r["usable"]}
            if good:
                registry.record(key, version, by_key[key]["url"], good)
                saved += len(good)
        print(f"Recorded {saved} verified locator(s) in {registry.REGISTRY_PATH}")

    probed = sum(len(e["results"]) for e in pages.values())
    outcomes.record(
        "sweep",
        version=version,
        pages=len(pages),
        probed=probed,
        drifted=drifted_count(pages, specs),
        unreachable=sum(1 for e in pages.values() if e["error"]),
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
