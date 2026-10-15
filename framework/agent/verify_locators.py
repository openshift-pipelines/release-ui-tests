"""Verify candidate locators against a live cluster before they reach generated code.

Every selector is resolved with the same Playwright engine the tests run on, so a
selector that passes here cannot be a hallucination: it matched a real element.

Usage:
    python -m framework.agent.verify_locators candidates.json [--headed] [--no-save]

Input file:
    {
      "page_key": "tasks.list",
      "url": "/tasks/ns/test",
      "candidates": {
        "CREATE_BUTTON": "[data-test=\\"item-create\\"]",
        "TASK_ROW_BY_NAME": {
          "selector": "tr:has-text(\\"{task_name}\\")",
          "sample": {"task_name": "hello"}
        }
      }
    }
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from playwright.async_api import Page, async_playwright

from framework.agent import locator_registry as registry
from framework.config.config import Config
from framework.ui_components.commons.login_page import LoginPage

PROBE_TIMEOUT_MS = 5000

# The console renders nothing for 10s+ on a cold load. Probing before it is ready
# reports every locator as "matched nothing", which is the exact false negative
# this tool exists to prevent. There is deliberately no default `ready` selector:
# every weak one tried here (an h1, a bare textarea, an empty-state body) also
# exists on a half-rendered page or a 404, and silently produced phantom drift.
READY_TIMEOUT_MS = 90000

# Every miss is re-probed once after a settle, and only a locator that misses twice is
# reported absent. Each probe already waits PROBE_TIMEOUT_MS, so a slow page tends to
# produce a few phantom misses rather than an obvious cliff - there is no ratio that
# separates that from real drift, which is why thresholds were abandoned here.
RECHECK_SETTLE_MS = 8000


def detect_version() -> str:
    """Build a composite OCP+OSP version key.

    Console chrome locators track the OCP version while Tekton page locators come
    from the OSP console plugin, so a change in either must invalidate the cache.
    """
    return f"ocp{_oc_version('clusterversion/version', '{.status.desired.version}')}-osp{_osp_version()}"


def _oc_version(resource: str, jsonpath: str) -> str:
    try:
        out = subprocess.run(
            ["oc", "get", resource, "-o", f"jsonpath={jsonpath}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _osp_version() -> str:
    try:
        out = subprocess.run(
            [
                "oc",
                "get",
                "csv",
                "-n",
                "openshift-operators",
                "-o",
                "jsonpath={.items[?(@.spec.displayName=='Red Hat OpenShift Pipelines')].spec.version}",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return out.stdout.strip().split()[0] if out.stdout.strip() else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def resolve_candidate(raw: Union[str, Dict[str, Any]]) -> Tuple[str, str, bool]:
    """Normalise a candidate into (stored_selector, probe_selector, expect_many).

    Templated selectors are stored with their {placeholder} intact but probed with
    a sample value substituted, since the placeholder itself matches nothing.
    """
    if isinstance(raw, str):
        return raw, raw, False
    selector = raw["selector"]
    sample = raw.get("sample") or {}
    expect_many = raw.get("expect") == "many"
    return selector, selector.format(**sample) if sample else selector, expect_many


class PageNotReady(RuntimeError):
    """The page never rendered, so any probe result would be a false negative."""


async def await_ready(page: Page, ready_selector: str) -> None:
    try:
        await page.locator(ready_selector).first.wait_for(state="attached", timeout=READY_TIMEOUT_MS)
    except Exception as exc:  # noqa: BLE001 - surfaced as a hard stop below
        raise PageNotReady(
            f"page did not render within {READY_TIMEOUT_MS}ms (waiting for {ready_selector!r}). "
            "Verification aborted rather than reporting every locator as missing."
        ) from exc


async def count_visible(page: Page, selector: str) -> int:
    """How many matches are actually visible.

    An element can be attached but hidden, which passes a naive existence check yet
    fails any real click, so the two counts are reported separately.
    """
    try:
        return await page.locator(selector).locator("visible=true").count()
    except Exception:  # noqa: BLE001 - not all selectors support chaining
        return -1


async def probe(page: Page, selector: str) -> Tuple[int, int, str]:
    """Return (attached_count, visible_count, error_message)."""
    try:
        locator = page.locator(selector)
        await locator.first.wait_for(state="attached", timeout=PROBE_TIMEOUT_MS)
        return await locator.count(), await count_visible(page, selector), ""
    except Exception as exc:  # noqa: BLE001 - any resolution failure means "did not match"
        message = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        try:
            return await page.locator(selector).count(), 0, message
        except Exception:  # noqa: BLE001 - malformed selector
            return 0, 0, message


def _same_page(current: str, target: str) -> bool:
    return current.split("?")[0].rstrip("/") == target.split("?")[0].rstrip("/")


async def verify_one(page: Page, spec: Dict[str, Any], base_url: str) -> Tuple[Dict[str, Any], List[str]]:
    """Navigate to one page and probe its candidates. Assumes the session is logged in.

    Returns (results, recovered) where `recovered` names locators that only appeared
    on the second read - a signal that this page's `ready` selector is too weak.
    """
    url = spec["url"]
    target = url if url.startswith("http") else f"{base_url}{url}"

    # Several locator classes describe the same page. Re-issuing goto() for a URL
    # already loaded makes this SPA remount and sometimes never re-render, so reuse
    # what is on screen instead.
    ready = spec.get("ready")
    if not ready:
        raise PageNotReady(
            f"{spec['page_key']}: no 'ready' selector. Name the element the probes "
            "depend on (the table for a list, `dl` for a detail page, `.monaco-editor` "
            "for YAML) so a half-rendered page cannot be mistaken for missing locators."
        )

    if not _same_page(page.url, target):
        await page.goto(target)
        # The console holds websockets open, so "networkidle" never fires here.
        await page.wait_for_load_state("domcontentloaded")

    await await_ready(page, ready)

    results: Dict[str, Dict[str, Any]] = {}
    for name, raw in spec["candidates"].items():
        stored, probed, expect_many = resolve_candidate(raw)
        count, visible, error = await probe(page, probed)
        results[name] = _result(stored, probed, count, visible, expect_many, error)

    recovered = await recheck_missing(page, spec, results)
    return results, recovered


def _result(stored: str, probed: str, count: int, visible: int, expect_many: bool, error: str) -> Dict[str, Any]:
    confidence = registry.score(stored, count, expect_many)
    return {
        "selector": stored,
        "probed_selector": probed if probed != stored else None,
        "match_count": count,
        "visible_count": visible,
        "confidence": confidence,
        "strategy": registry.classify_strategy(stored),
        "templated": registry.is_templated(stored),
        "expect_many": expect_many,
        "usable": confidence >= registry.MIN_USABLE_CONFIDENCE,
        "error": error or None,
    }


async def recheck_missing(page: Page, spec: Dict[str, Any], results: Dict[str, Dict[str, Any]]) -> List[str]:
    """Re-probe everything that missed; return the names that appeared second time.

    A locator is only reported absent if it misses twice with a settle in between.
    Anything that recovers proves the page was still painting, so the second read is
    kept and the caller is told the page's `ready` selector is too weak.
    """
    missing = [n for n, r in results.items() if r["match_count"] == 0]
    if not missing:
        return []

    await page.wait_for_timeout(RECHECK_SETTLE_MS)
    recovered = []
    for name in missing:
        stored, probed, expect_many = resolve_candidate(spec["candidates"][name])
        count, visible, error = await probe(page, probed)
        if count > 0:
            recovered.append(name)
            results[name] = _result(stored, probed, count, visible, expect_many, error)
    return sorted(recovered)


async def verify_pages(
    specs: List[Dict[str, Any]],
    headed: bool,
    on_page: Optional[Callable[[str, Dict[str, Any], Optional[str]], None]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Verify many pages in one logged-in session.

    Logging in costs ~30s, so a sweep over dozens of pages must not repeat it.
    A page that never renders is recorded as an error and the sweep continues.
    """
    config = Config()
    out: Dict[str, Dict[str, Any]] = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=not headed)
        context = await browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = await context.new_page()
        page.set_default_timeout(config.timeout_ms)
        try:
            login = LoginPage(page, config)
            await login.goto()
            await login.perform_login(config.auth_type)

            for spec in specs:
                key = spec["page_key"]
                try:
                    results, recovered = await verify_one(page, spec, config.base_url)
                    error = None
                except PageNotReady as exc:
                    results, recovered, error = {}, [], str(exc)
                out[key] = {
                    "results": results,
                    "error": error,
                    "url": spec["url"],
                    "recovered_on_recheck": recovered,
                }
                if on_page:
                    on_page(key, results, error)
        finally:
            await context.close()
            await browser.close()

    return out


async def verify(spec: Dict[str, Any], headed: bool) -> Dict[str, Any]:
    out = await verify_pages([spec], headed)
    entry = out[spec["page_key"]]
    if entry["error"]:
        raise PageNotReady(entry["error"])
    if entry["recovered_on_recheck"]:
        print(
            f"WARNING: {len(entry['recovered_on_recheck'])} locator(s) only matched on a "
            f"second read ({', '.join(entry['recovered_on_recheck'][:4])}). "
            f"The 'ready' selector {spec.get('ready')!r} fires before this page is populated.",
            file=sys.stderr,
        )
    return entry["results"]


def report(page_key: str, version: str, results: Dict[str, Dict[str, Any]]) -> int:
    usable = {n: r for n, r in results.items() if r["usable"]}
    rejected = {n: r for n, r in results.items() if not r["usable"]}

    print(f"\nPage:    {page_key}")
    print(f"Version: {version}")
    print(f"Result:  {len(usable)}/{len(results)} locators verified\n")

    hidden = []
    for name, r in results.items():
        mark = "PASS" if r["usable"] else "FAIL"
        scoped = " (scoped)" if r["expect_many"] else ""
        vis = ""
        if r["usable"] and r["visible_count"] == 0:
            vis = " HIDDEN"
            hidden.append(name)
        print(
            f"  [{mark}] {name:<32} matches={r['match_count']}{scoped}"
            f" visible={r['visible_count']} confidence={r['confidence']:.2f}{vis}"
        )
        print(f"         {r['selector']}")

    if hidden:
        print(
            f"\n{len(hidden)} locator(s) exist but are not visible: {', '.join(hidden)}."
            "\nFine for elements revealed by an interaction (menu items); a click on anything"
            "\nelse will time out waiting for visibility."
        )

    if rejected:
        print(f"\n{len(rejected)} locator(s) rejected. Do not use these in generated code.")
        for name, r in rejected.items():
            if r["match_count"] == 0:
                reason = "matched nothing"
            else:
                reason = (
                    f"ambiguous ({r['match_count']} matches) - scope it, "
                    'or declare "expect": "many" if callers always scope it to a row'
                )
            print(f"  - {name}: {reason}")

    return 0 if not rejected else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", type=Path, help="JSON file describing the page and candidate locators")
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not record verified locators. Saving is the default - a verification thrown away has to be repeated.",
    )
    parser.add_argument("--headed", action="store_true", help="Show the browser while verifying")
    parser.add_argument("--version", help="Override the detected product version key")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results on stdout")
    args = parser.parse_args()

    spec = json.loads(args.candidates.read_text())
    version = args.version or detect_version()
    try:
        results = asyncio.run(verify(spec, args.headed))
    except PageNotReady as exc:
        print(f"ABORTED: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"page_key": spec["page_key"], "version": version, "results": results}, indent=2))
        exit_code = 0 if all(r["usable"] for r in results.values()) else 1
    else:
        exit_code = report(spec["page_key"], version, results)

    if not args.no_save:
        verified = {n: r for n, r in results.items() if r["usable"]}
        if verified:
            registry.record(spec["page_key"], version, spec["url"], verified)
            if not args.json:
                print(f"\nSaved {len(verified)} verified locator(s) to {registry.REGISTRY_PATH}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
