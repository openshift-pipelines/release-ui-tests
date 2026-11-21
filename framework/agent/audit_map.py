"""Check that every page-map entry points at the page its locator class describes.

A class mapped to the wrong URL is worse than one not mapped at all: the sweep probes
a real page, finds the locators genuinely absent, and reports correct selectors as
drift. Acting on that report then breaks working tests. This happened once with
OverViewPageLocators, which was mapped to /pipelines-overview because the names looked
alike when it actually describes the console home page.

The page object itself is the source of truth - it declares the URL it verifies, via
`_verify_page("suffix")` or a named pattern from console_url_patterns.

Usage:
    python -m framework.agent.audit_map
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from framework.ui_components import console_url_patterns as patterns

MAP_PATH = Path(__file__).resolve().parents[2] / ".agent" / "sweep" / "page_map.yaml"
POM_ROOT = Path(__file__).resolve().parents[1] / "ui_components"

LOCATOR_CLASS_RE = re.compile(r"=\s*(\w+Locators)\(\)")
VERIFY_SUFFIX_RE = re.compile(r"""_verify_page\(\s*["']([^"']+)["']""")
WAIT_SUFFIX_RE = re.compile(r"""wait_for_url_to_endwith\(\s*["']([^"']+)["']""")
VERIFY_REGEX_RE = re.compile(r"_verify_page_regex\(\s*(\w+)")


def pom_expectations() -> Dict[str, List[Tuple[str, str]]]:
    """Map each locator class to the URL expectations of the page objects that use it."""
    out: Dict[str, List[Tuple[str, str]]] = {}
    for path in POM_ROOT.rglob("*.py"):
        src = path.read_text()
        classes = set(LOCATOR_CLASS_RE.findall(src))
        if not classes:
            continue
        expectations: List[Tuple[str, str]] = []
        for suffix in set(VERIFY_SUFFIX_RE.findall(src)) | set(WAIT_SUFFIX_RE.findall(src)):
            expectations.append(("suffix", suffix))
        for name in set(VERIFY_REGEX_RE.findall(src)):
            expectations.append(("pattern", name))
        if expectations:
            for cls in classes:
                out.setdefault(cls, []).extend(expectations)
    return out


def satisfies(url: str, kind: str, value: str) -> Optional[bool]:
    """Does the mapped URL meet this expectation? None when it cannot be evaluated."""
    if kind == "suffix":
        return url.rstrip("/").endswith(value.rstrip("/"))
    compiled = getattr(patterns, value, None)
    if compiled is None:
        return None
    return bool(compiled.search(url.replace("{ns}", "placeholder-ns")))


def audit(map_path: Path = MAP_PATH) -> int:
    page_map = yaml.safe_load(map_path.read_text())
    expectations = pom_expectations()

    problems: List[str] = []
    unchecked: List[str] = []
    checked = 0

    for entry in page_map["pages"]:
        cls = entry["locators"].split(":")[-1]
        exp = expectations.get(cls)
        if not exp:
            unchecked.append(f"{entry['key']:<34} {cls} (its page object declares no URL)")
            continue
        # A base class is shared by sibling pages, so any one match is enough.
        verdicts = [satisfies(entry["url"], kind, value) for kind, value in exp]
        if all(v is None for v in verdicts):
            unchecked.append(f"{entry['key']:<34} {cls} (expectations not resolvable)")
            continue
        checked += 1
        if not any(v for v in verdicts if v is not None):
            shown = ", ".join(v for _, v in exp)
            problems.append(
                f"  {entry['key']:<30} {cls}\n"
                f"      mapped to {entry['url']}\n"
                f"      but its page object verifies: {shown}"
            )

    print(f"Audited {checked} page-map entries against their page objects.\n")
    if problems:
        print(f"MISMATCHED ({len(problems)}) - the sweep would report correct locators as drift:\n")
        print("\n".join(problems))
    else:
        print("All mappings agree with the page objects.")
    if unchecked:
        print(f"\nNot checkable ({len(unchecked)}) - no URL assertion to compare against:")
        for line in unchecked:
            print(f"  {line}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(audit())
