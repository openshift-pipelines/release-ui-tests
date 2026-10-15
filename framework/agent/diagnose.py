"""Turn a failing test into a structured, evidence-backed verdict.

The question that matters when a UI test fails is whether the locator is genuinely
wrong or the page simply had not painted. Guessing "wrong" rewrites a correct
locator; guessing "timing" leaves a real break in place. This module answers it as
a fact: it re-navigates to the URL the test died on and probes the failing selector
with the same engine the test used.

Usage:
    python -m framework.agent.diagnose                     # the sanity suite (default)
    python -m framework.agent.diagnose <pytest-target>     # one node id, to reproduce a failure
"""

import argparse
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from framework.agent import locator_registry as registry
from framework.agent import outcomes
from framework.agent.verify_locators import PageNotReady, detect_version, verify_pages
from framework.config.config import Config

PAGE_MAP = Path(__file__).resolve().parents[2] / ".agent" / "sweep" / "page_map.yaml"

# Playwright reports the selector it was waiting on in the call log.
CALLLOG_SELECTOR_RE = re.compile(r"""waiting for locator\((["'])(.+?)\1\)""")
# BasePage swallows Playwright timeouts into a bool, so most failures never show a call
# log. These two carry the selector instead: an explicit marker it logs on timeout, and
# the assertion text _verify_page raises.
MARKER_SELECTOR_RE = re.compile(r"\[locator-timeout\]\s+(.+?)\s*$", re.MULTILINE)
HEADER_SELECTOR_RE = re.compile(r"Header element \((.+?)\) is not visible")
EXC_RE = re.compile(r"^E\s+([\w.]+(?:Error|Exception)):\s*(.*)$", re.MULTILINE)
# Two shapes appear in pytest output: the short-summary line "FAILED path::test" and
# the progress line "path::test FAILED [ 5%]". Requiring "::" keeps the progress line's
# trailing "[" from being mistaken for a node id.
NODEID_SUMMARY_RE = re.compile(r"^(?:FAILED|ERROR)\s+(\S+::\S+)", re.MULTILINE)
NODEID_PROGRESS_RE = re.compile(r"^(\S+::\S+)\s+(?:FAILED|ERROR)", re.MULTILINE)

# Seeded fixture names vary per run; treat them as wildcards when matching a failure
# URL back to the page map.
FIXTURE_SEGMENT = re.compile(r"^(probe|uniq)-")


def run_pytest(target: Optional[str], extra: List[str]) -> Tuple[int, str]:
    """Run the sanity suite by default; a narrower target only to reproduce one failure."""
    selection = [target] if target else ["tests/", "-m", "sanity"]
    cmd = [sys.executable, "-m", "pytest", *selection, "-p", "no:randomly", "-x", "--tb=long", *extra]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout + proc.stderr


def parse_failure(output: str) -> Dict[str, Any]:
    """Pull the failing test, exception and awaited selector out of pytest output."""
    m = NODEID_SUMMARY_RE.search(output) or NODEID_PROGRESS_RE.search(output)
    nodeid = m.group(1) if m else None

    exc_type = exc_msg = None
    exc = EXC_RE.search(output)
    if exc:
        exc_type, exc_msg = exc.group(1).split(".")[-1], exc.group(2).strip()

    # Playwright escapes the inner quotes when it echoes the selector into the call
    # log; probing the escaped form would fail as a malformed selector, not a missing one.
    # Order matters: the consumer acts on the first entry. A run collects every selector
    # that timed out, including incidental ones (the "Skip tour" popup is absent on every
    # healthy page), so the most proximate cause must come first:
    #   1. named in the assertion the test died on
    #   2. in Playwright's call log for the raising call
    #   3. logged timeouts, latest first - the last wait before the failure
    selectors = HEADER_SELECTOR_RE.findall(output)
    selectors += [m.group(2) for m in CALLLOG_SELECTOR_RE.finditer(output)]
    selectors += list(reversed(MARKER_SELECTOR_RE.findall(output)))
    # Playwright escapes inner quotes when echoing a selector; probing the escaped form
    # would fail as malformed rather than missing.
    selectors = [s.replace('\\"', '"').replace("\\'", "'").strip() for s in selectors]
    return {
        "nodeid": nodeid,
        "exception": exc_type,
        "message": exc_msg,
        "selectors": list(dict.fromkeys(selectors)),
    }


def load_failure_context(config: Config, nodeid: Optional[str]) -> Optional[Dict[str, Any]]:
    """Read the URL the test died on, recorded by the conftest failure hook."""
    failures = Path(config.artifacts_dir) / "failures"
    if not failures.is_dir():
        return None
    if nodeid:
        safe = nodeid.replace("/", "_").replace("::", "__").replace(" ", "_")
        exact = failures / f"{safe}.json"
        if exact.exists():
            return json.loads(exact.read_text())
    recent = sorted(failures.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return json.loads(recent[0].read_text()) if recent else None


def url_to_regex(template: str) -> re.Pattern:
    parts = []
    for seg in template.strip("/").split("/"):
        parts.append("[^/]+" if seg == "{ns}" or FIXTURE_SEGMENT.match(seg) else re.escape(seg))
    return re.compile("^/" + "/".join(parts) + "/?$")


def resolve_ready(path: str) -> Tuple[Optional[str], Optional[str]]:
    """Find the page-map entry whose URL shape matches, and return its ready selector.

    Returns (ready, page_key). Both None when the URL is not in the page map, in
    which case the selector must not be probed - without a correct ready signal a
    present locator can read as absent, which is the failure mode this tool exists
    to rule out.
    """
    if not PAGE_MAP.exists():
        return None, None
    page_map = yaml.safe_load(PAGE_MAP.read_text())
    profiles = page_map["ready_profiles"]
    for entry in page_map["pages"]:
        if url_to_regex(entry["url"]).match(path):
            return profiles[entry["ready"]], entry["key"]
    return None, None


async def probe_selectors(url: str, ready: str, selectors: List[str]) -> Dict[str, Any]:
    spec = {
        "page_key": "diagnose",
        "url": url,
        "ready": ready,
        "candidates": {f"S{i}": s for i, s in enumerate(selectors)},
    }
    out = await verify_pages([spec], headed=False)
    return out["diagnose"]


def classify(failure: Dict[str, Any], probe: Optional[Dict[str, Any]], note: str) -> Dict[str, Any]:
    """Decide what actually went wrong, and say what evidence supports it."""
    exc = failure["exception"] or ""
    selectors = failure["selectors"]

    if exc in {"FileNotFoundError", "YAMLError", "ScannerError", "ParserError"}:
        return _verdict("data", "Test data file missing or malformed.", "fix the test data", failure)

    if selectors and probe is not None:
        results = probe["results"]
        absent = [r["selector"] for r in results.values() if r["match_count"] == 0]
        present = [r["selector"] for r in results.values() if r["match_count"] > 0]
        if absent and not present:
            return _verdict(
                "locator_absent",
                f"Re-probed on the live page: {len(absent)} selector(s) matched nothing. "
                "The locator is genuinely wrong.",
                "re-extract the locator, then update framework/locators",
                failure,
                evidence={"absent": absent},
            )
        if present:
            hidden = [r["selector"] for r in results.values() if r["match_count"] > 0 and r["visible_count"] == 0]
            if hidden:
                return _verdict(
                    "locator_hidden",
                    f"Re-probed on the live page: {len(hidden)} selector(s) exist in the DOM but "
                    "are not visible. Playwright waits for visibility, so the element is there "
                    "and still unusable.",
                    "the element is probably revealed by an interaction, or the selector matches "
                    "the wrong (offscreen) element - do not just swap the selector",
                    failure,
                    evidence={"hidden": hidden, "absent": absent},
                )
            return _verdict(
                "locator_present",
                f"Re-probed on the live page: {len(present)} selector(s) matched and were visible. "
                "The locator is correct, so the failure is timing or page state.",
                "do NOT change the locator - investigate waits, navigation or test data",
                failure,
                evidence={"present": present, "absent": absent},
            )

    if exc == "AssertionError":
        return _verdict(
            "assertion",
            "An assertion failed with no locator to re-probe. This may be a real product bug.",
            "read the assertion before changing anything; escalate if the product looks wrong",
            failure,
        )

    if "Timeout" in exc:
        return _verdict(
            "timing_unverified",
            f"Timed out, but the selector could not be re-probed. {note}",
            "establish the page's ready signal before concluding anything",
            failure,
        )

    return _verdict("unknown", f"Unrecognised failure. {note}".strip(), "needs a human", failure)


def _verdict(
    kind: str,
    reason: str,
    action: str,
    failure: Dict[str, Any],
    evidence: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "verdict": kind,
        "reason": reason,
        "recommended_action": action,
        "failure": failure,
        "evidence": evidence or {},
    }


def diagnose(target: Optional[str], extra: List[str]) -> Dict[str, Any]:
    code, output = run_pytest(target, extra)
    if code == 0:
        outcomes.record("diagnose", verdict="passed", target=target or "sanity")
        return {
            "verdict": "passed",
            "reason": "Test passed.",
            "recommended_action": "none",
            "failure": {},
            "evidence": {},
        }

    failure = parse_failure(output)
    config = Config()
    context = load_failure_context(config, failure["nodeid"])
    note = ""
    probe = None
    page_key = None

    if not context:
        note = "No failure context was recorded, so the failing URL is unknown."
    elif not failure["selectors"]:
        note = "No awaited selector appeared in the traceback."
    else:
        path = context["url"].replace(config.base_url, "") or "/"
        ready, page_key = resolve_ready(path)
        if not ready:
            note = f"{path} is not in the page map, so there is no trustworthy ready signal for it."
        else:
            try:
                probe = asyncio.run(probe_selectors(context["url"], ready, failure["selectors"]))
                if probe["error"]:
                    probe, note = None, f"Re-probe aborted: {probe['error']}"
                elif probe["recovered_on_recheck"]:
                    note = (
                        "Selector only matched on a second read, so the page was still painting "
                        f"({page_key} ready selector is too weak)."
                    )
            except PageNotReady as exc:
                note = f"Re-probe aborted: {exc}"

    result = classify(failure, probe, note)
    result["failure_url"] = context["url"] if context else None
    result["note"] = note

    if probe and page_key:
        _bank_proven_locators(page_key, context["url"], probe["results"])
    outcomes.record(
        "diagnose",
        verdict=result["verdict"],
        nodeid=failure["nodeid"],
        page=page_key,
        selectors=failure["selectors"][:3],
    )
    return result


def _bank_proven_locators(page_key: str, url: str, results: Dict[str, Dict[str, Any]]) -> None:
    """Keep what the re-probe established, so the next failure does not re-litigate it.

    Diagnosis already paid the cost of loading the page and resolving these selectors;
    discarding that is why the registry stayed almost empty.
    """
    proven = {
        name: result
        for name, result in results.items()
        if result["usable"] and not registry.is_templated(result["selector"])
    }
    if proven:
        registry.record(page_key, detect_version(), url, proven)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        nargs="?",
        help="pytest node id to reproduce one failure. Omit to run the sanity suite (`-m sanity`), "
        "which is how changes are verified in this project.",
    )
    parser.add_argument("--json", type=Path, help="Write the verdict here")
    parser.add_argument("--pytest-arg", action="append", default=[], help="Extra arg passed to pytest")
    args = parser.parse_args()

    result = diagnose(args.target, args.pytest_arg)

    print(f"\nVERDICT  {result['verdict']}")
    print(f"  {result['reason']}")
    print(f"  action: {result['recommended_action']}")
    if result.get("failure", {}).get("nodeid"):
        print(f"  test:   {result['failure']['nodeid']}")
    if result.get("failure_url"):
        print(f"  url:    {result['failure_url']}")
    for key, vals in (result.get("evidence") or {}).items():
        for v in vals:
            print(f"  {key}: {v}")
    if result.get("note"):
        print(f"  note:   {result['note']}")

    if args.json:
        args.json.write_text(json.dumps(result, indent=2))

    return 0 if result["verdict"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
