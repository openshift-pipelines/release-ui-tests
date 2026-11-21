"""Persistent store of UI locators that have been verified against a live cluster.

Locators are keyed by page and product version, so a locator verified on 4.22 is
never silently reused on a cluster running a different version.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

REGISTRY_PATH = Path(__file__).resolve().parents[2] / ".agent" / "memory" / "locator_registry.json"

SCHEMA_VERSION = 1

# A locator is only trusted in generated code at or above this confidence.
MIN_USABLE_CONFIDENCE = 0.7

_STRATEGY_CONFIDENCE = {
    "data-test": 0.95,
    "id": 0.95,
    "role": 0.90,
    "aria": 0.90,
    "text": 0.80,
    "css": 0.75,
}

_TEMPLATE_FIELD = re.compile(r"\{[a-z_][a-z0-9_]*\}")


def is_templated(selector: str) -> bool:
    """True when the selector contains a {placeholder} that must be formatted before use."""
    return bool(_TEMPLATE_FIELD.search(selector))


def classify_strategy(selector: str) -> str:
    """Infer which locator strategy a selector uses, for confidence scoring."""
    if "data-test" in selector or "data-ouia" in selector:
        return "data-test"
    if selector.startswith("role=") or "role=" in selector:
        return "role"
    if "aria-label" in selector:
        return "aria"
    if re.search(r"\[id=|^#", selector):
        return "id"
    if ":has-text(" in selector or selector.startswith("text="):
        return "text"
    return "css"


def score(selector: str, match_count: int, expect_many: bool = False) -> float:
    """Score a selector from 0.0 (unusable) to 0.95 (verified unique and stable).

    A selector matching nothing is worthless; one matching many elements is
    ambiguous and will break as soon as the list it points into changes - unless
    it is declared `expect_many`, meaning callers always scope it to a row or
    container first (e.g. a per-row Actions button).
    """
    if match_count == 0:
        return 0.0
    if match_count > 1 and not expect_many:
        return 0.4
    return _STRATEGY_CONFIDENCE[classify_strategy(selector)]


def load(path: Path = REGISTRY_PATH) -> Dict[str, Any]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "entries": {}}
    with path.open() as fh:
        return json.load(fh)


def save(registry: Dict[str, Any], path: Path = REGISTRY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(registry, fh, indent=2, sort_keys=True)
        fh.write("\n")


def get_page(
    page_key: str,
    version: str,
    registry: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return the verified locators recorded for a page on a given product version."""
    reg = registry if registry is not None else load()
    return reg["entries"].get(page_key, {}).get("versions", {}).get(version, {}).get("locators", {})


def record(
    page_key: str,
    version: str,
    url: str,
    locators: Dict[str, Dict[str, Any]],
    path: Path = REGISTRY_PATH,
) -> Dict[str, Any]:
    """Merge verification results for one page/version into the registry and persist."""
    reg = load(path)
    entry = reg["entries"].setdefault(page_key, {"url": url, "versions": {}})
    entry["url"] = url
    version_entry = entry["versions"].setdefault(version, {"locators": {}})
    version_entry["verified_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    version_entry["locators"].update(locators)
    save(reg, path)
    return reg
