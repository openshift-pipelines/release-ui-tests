"""Deterministic checks that bound an automated heal.

Two things go wrong when a fix loop is left to judgement alone: it declares victory on
a run that only passed by luck, and it edits files well outside the blame radius of the
failure. Both are mechanical questions, so they are answered here rather than in prose.

    python -m framework.agent.guardrails stability [--runs 3]
    python -m framework.agent.guardrails scope
"""

import argparse
import json
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from framework.agent import outcomes

# A heal may touch the test, the selectors it uses, and the data it feeds in. Anything
# else - fixtures, config, the agent's own tooling, CI - changes the meaning of a pass
# rather than fixing the failure, so it must be a deliberate human edit.
ALLOWED = (
    "tests/features/*",
    "tests/steps/*",
    "framework/locators/*",
    "framework/ui_components/*",
    "framework/resources/test_data/*",
)
DENIED = (
    "tests/conftest.py",
    "framework/agent/*",
    "framework/config/*",
    "framework/fixtures/*",
    "pytest.ini",
    ".env*",
    ".github/*",
)

DEFAULT_RUNS = 3


def changed_files() -> List[str]:
    out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=False).stdout
    return [line[3:].strip() for line in out.splitlines() if line.strip()]


def classify_paths(paths: Sequence[str]) -> Tuple[List[str], List[str]]:
    """Split changed paths into (permitted, violations)."""
    permitted, violations = [], []
    for path in paths:
        if any(fnmatch(path, pattern) for pattern in DENIED):
            violations.append(path)
        elif any(fnmatch(path, pattern) for pattern in ALLOWED):
            permitted.append(path)
        else:
            violations.append(path)
    return permitted, violations


def check_scope(baseline: Optional[Path] = None) -> int:
    paths = changed_files()
    if baseline and baseline.exists():
        # Heals usually start from a tree that already has unrelated edits. Only judge
        # what this heal touched, or the guard blocks every run on a dirty tree.
        already = set(json.loads(baseline.read_text()))
        skipped = [p for p in paths if p in already]
        paths = [p for p in paths if p not in already]
        if skipped:
            print(f"Ignoring {len(skipped)} file(s) already modified before the heal started.\n")
    if not paths:
        print("No new changes in the working tree.")
        return 0
    permitted, violations = classify_paths(paths)

    print(f"Changed files: {len(paths)}\n")
    for path in permitted:
        print(f"  ok       {path}")
    for path in violations:
        print(f"  BLOCKED  {path}")

    if violations:
        print(
            f"\n{len(violations)} file(s) are outside what a heal may touch. Fixtures, config "
            "and tooling change what a passing test means, so revert them or make the edit "
            "deliberately yourself."
        )
        return 1
    print("\nAll changes are within the healable surface.")
    return 0


def run_once(target: Sequence[str]) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *target, "-p", "no:randomly", "-q"],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def stability(target: Sequence[str], runs: int) -> int:
    """Pass only if every run passes.

    One green run proves nothing about a timing fix - the failure it was meant to cure
    is intermittent by definition. A heal is finished when the test passes repeatedly.
    """
    results = []
    for i in range(1, runs + 1):
        ok = run_once(target)
        results.append(ok)
        print(f"  run {i}/{runs}: {'pass' if ok else 'FAIL'}", flush=True)

    passed = sum(results)
    outcomes.record("stability", runs=runs, passed=passed, target=" ".join(target))
    print(f"\n{passed}/{runs} runs passed.")
    if passed == runs:
        print("Stable.")
        return 0
    if passed == 0:
        print("Consistently failing - the fix did not work.")
        return 1
    print("FLAKY - passed sometimes. A heal that produces a flaky test is not a fix; it hides the failure.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    stab = sub.add_parser("stability", help="Run the suite repeatedly; pass only if every run passes")
    stab.add_argument("target", nargs="*", default=None, help="pytest target (default: the sanity suite)")
    stab.add_argument("--runs", type=int, default=DEFAULT_RUNS)

    scope = sub.add_parser("scope", help="Check the working tree only touches files a heal may change")
    scope.add_argument("--baseline", type=Path, help="Ignore files already changed before the heal")

    base = sub.add_parser("baseline", help="Snapshot currently-changed files, to compare against later")
    base.add_argument("path", type=Path)

    args = parser.parse_args()
    if args.command == "baseline":
        args.path.write_text(json.dumps(changed_files(), indent=2))
        print(f"Baseline of {len(changed_files())} changed file(s) written to {args.path}")
        return 0
    if args.command == "scope":
        return check_scope(args.baseline)

    target = args.target or ["tests/", "-m", "sanity"]
    print(f"Stability gate: {' '.join(target)} x{args.runs}\n")
    return stability(target, args.runs)


if __name__ == "__main__":
    sys.exit(main())
