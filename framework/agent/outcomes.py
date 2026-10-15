"""Append-only record of what the agent tooling did, so quality can be measured.

Without this the loop has no memory of its own behaviour: every sweep, diagnosis and
stability check is forgotten the moment it prints. That makes the obvious questions
unanswerable - is locator drift growing, are heals getting it right, is a test flaky or
was it a one-off.

One JSON object per line, appended, never rewritten. Recording must never be able to
break the thing it is observing, so every failure here is swallowed.

    python -m framework.agent.outcomes          # trends
    python -m framework.agent.outcomes --tail 20
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG_PATH = Path(__file__).resolve().parents[2] / ".agent" / "memory" / "outcomes.jsonl"


def record(kind: str, path: Path = LOG_PATH, **fields: object) -> None:
    """Append one event. Never raises - observation must not break the observed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        event = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "kind": kind, **fields}
        with path.open("a") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")
    except Exception:  # noqa: BLE001 - telemetry is never worth a crash
        pass


def load(path: Path = LOG_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a partial write should not poison the history
    return events


def _sweeps(events: List[Dict[str, Any]]) -> None:
    sweeps = [e for e in events if e["kind"] == "sweep"]
    if not sweeps:
        return
    print(f"\nSWEEPS ({len(sweeps)}) - locator drift over time")
    print(f"  {'when':<26} {'version':<24} {'probed':>7} {'drifted':>8} {'clean %':>8}")
    for e in sweeps[-10:]:
        probed, drifted = e.get("probed", 0), e.get("drifted", 0)
        pct = f"{100 * (probed - drifted) / probed:.0f}%" if probed else "-"
        print(f"  {e['at']:<26} {e.get('version', '?'):<24} {probed:>7} {drifted:>8} {pct:>8}")
    first, last = sweeps[0], sweeps[-1]
    if first is not last and first.get("probed") and last.get("probed"):
        delta = last["drifted"] - first["drifted"]
        direction = "worse" if delta > 0 else ("better" if delta < 0 else "unchanged")
        print(f"  trend: drift {first['drifted']} -> {last['drifted']} ({direction})")


def _diagnoses(events: List[Dict[str, Any]]) -> None:
    diags = [e for e in events if e["kind"] == "diagnose"]
    if not diags:
        return
    counts = Counter(e.get("verdict", "?") for e in diags)
    print(f"\nDIAGNOSES ({len(diags)}) - what failures actually were")
    for verdict, n in counts.most_common():
        print(f"  {verdict:<22} {n:>4}  {100 * n / len(diags):>4.0f}%")
    locator_real = counts.get("locator_absent", 0)
    locator_blamed = locator_real + counts.get("locator_present", 0) + counts.get("locator_hidden", 0)
    if locator_blamed:
        print(
            f"  of {locator_blamed} failures involving a locator, {locator_real} were genuinely "
            f"the locator - the rest would have been mis-fixed by editing the selector"
        )


def _stability(events: List[Dict[str, Any]]) -> None:
    runs = [e for e in events if e["kind"] == "stability"]
    if not runs:
        return
    flaky = [e for e in runs if 0 < e.get("passed", 0) < e.get("runs", 0)]
    clean = [e for e in runs if e.get("passed") == e.get("runs")]
    print(f"\nSTABILITY GATES ({len(runs)})")
    print(f"  fully passing : {len(clean)}")
    print(f"  flaky         : {len(flaky)}")
    print(f"  failing       : {len(runs) - len(clean) - len(flaky)}")
    for e in flaky[-5:]:
        print(f"    FLAKY {e['at']}  {e.get('passed')}/{e.get('runs')}  {e.get('target', '')[:54]}")


def summarise(path: Path = LOG_PATH, tail: Optional[int] = None) -> int:
    events = load(path)
    if not events:
        print(f"No outcomes recorded yet ({path}).")
        return 0

    if tail:
        print(f"Last {tail} event(s):")
        for e in events[-tail:]:
            extra = {k: v for k, v in e.items() if k not in ("at", "kind")}
            print(f"  {e['at']}  {e['kind']:<10} {extra}")
        return 0

    print(f"{len(events)} event(s) recorded since {events[0]['at']}")
    _sweeps(events)
    _diagnoses(events)
    _stability(events)
    return 0


def main() -> int:
    tail = None
    if "--tail" in sys.argv:
        tail = int(sys.argv[sys.argv.index("--tail") + 1])
    return summarise(tail=tail)


if __name__ == "__main__":
    sys.exit(main())
