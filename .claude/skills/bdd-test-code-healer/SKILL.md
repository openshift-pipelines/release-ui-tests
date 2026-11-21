---
name: bdd-test-code-healer
description: Diagnoses and fixes failing BDD tests. Use when tests fail and you need the root cause and a fix. Re-probes the failing selector against the live page first, so "the locator is broken" is proven rather than guessed - which also tells you when NOT to touch the locator. Falls back to pattern analysis for timing, data and navigation issues. Proposes fixes with an approval gate, verifies with the sanity suite, retries up to 3 times.
---

# BDD Test Code Healer

Automatically diagnose and fix failing BDD tests with intelligent analysis and iterative repair.

## Quick Reference

📖 **[Examples](references/examples.md)** - 3 healing scenarios with before/after
📖 **[Best Practices](references/best-practices.md)** - 5 practices for effective healing
📖 **[Testing](references/testing.md)** - How to verify skill works
📖 **[Error Handling](references/error-handling.md)** - 5 error scenarios and solutions
📖 **[Failure Patterns Guide](references/failure-patterns.md)** - 15 failure patterns with fixes
🔬 **`python -m framework.agent.diagnose`** - grounded verdict; run this before anything else
📖 **[Implementation Guide](references/implementation-guide.md)** - All 3 phases detailed steps
🛡️ **`python -m framework.agent.guardrails`** - `scope` and `stability` gates (Phase 2)

---

## What It Does

Takes failing BDD tests → Runs tests → **Re-probes the failing selector against the live page** →
Identifies root causes (locators, timing, data) → Proposes fixes → Applies after approval →
Verifies with `pytest -m sanity` → Retries up to 3 times

**Use when**: Previously passing tests now fail, need quick diagnosis, UI changes broke locators, timing/flaky tests, data updates needed, want automated debugging
**Don't use**: New tests never worked (use `/bdd-test-code-generator`), writing new scenarios, legitimate application bugs

**Features**: Live re-probe of the failing selector, verdict-gated actions, scope and
stability guardrails, iterative repair (3 attempts max), approval gate for everything
except proven-absent locators, multiple feature support, headed mode

---

## Configuration

Tests run in **headed mode** (`--headed`) with **stop-on-first-failure** (`-x`) for better visibility, faster healing, and avoiding cascade failures. All analysis reports use emojis, tables, and clear sections.

---

## Quick Start

```bash
# Fix single feature file
/bdd-test-code-healer task_crud_operations.feature

# Fix multiple feature files
/bdd-test-code-healer task_crud_operations.feature,pipeline_workflow.feature

# Or with full path
/bdd-test-code-healer tests/features/task_crud_operations.feature
```

---

## Healing Workflow

**Phase 0** (Diagnose first - do not skip): run the grounded classifier before reading
any traceback or pattern guide.

```bash
python -m framework.agent.diagnose <pytest node id>
```

It re-navigates to the URL the test died on and re-probes the failing selector against
the live page, so "the locator is broken" becomes a verified fact instead of a guess.
**Its verdict decides what you are allowed to do:**

| Verdict | What it proved | Allowed action |
|---|---|---|
| `locator_absent` | selector matched nothing on the live page | fix the locator - the only auto-fixable case |
| `locator_present` | selector matched **and was visible** | **do NOT touch the locator.** Investigate waits, navigation, test data |
| `locator_hidden` | selector matched but is invisible | element needs an interaction first, or points at the wrong node. Not a selector swap |
| `data` | test data missing or malformed | fix the YAML under `framework/resources/test_data/` |
| `assertion` | assertion failed, nothing to re-probe | read it. **May be a real product bug - escalate rather than mask** |
| `timing_unverified` | could not re-probe | establish the page's ready signal before concluding anything |

Changing a locator that `diagnose` reports as `locator_present` is how a correct
selector gets replaced with a worse one and a real failure gets buried.

**Fix the first selector listed, not every one.** A run collects every selector that timed
out, and some are incidental - the "Skip tour" popup is absent on every healthy page.
The evidence is ordered by proximity to the failure: the one named in the assertion, then
Playwright's call log, then logged timeouts latest-first. Treat entries after the first as
context unless you can show otherwise.

**Phase 1** (Analysis): Use the verdict to target the diagnosis. Consult
[Failure Patterns Guide](references/failure-patterns.md) for everything the verdict does
not cover - Monaco editor behaviour, project-switch timing, navigation and data issues.
Propose a fix → **🛑 STOP** - Wait for approval

**Phase 2** (Apply & verify). Apply the fix, then run both gates - a fix is not finished
until both pass:

```bash
python -m framework.agent.guardrails scope                 # only healable files changed?
python -m framework.agent.guardrails stability --runs 3    # passes every time, not just once?
```

`scope` fails if the edit reached fixtures, config, CI or the agent's own tooling. Those
change what a passing test *means* rather than fixing the failure, so revert them and
raise it instead.

`stability` fails on a flaky result. One green run proves nothing about a timing fix -
the failure it was meant to cure is intermittent by definition. **A heal that produces a
flaky test is not a fix, it is a hidden failure.** Verify with `pytest -m sanity`, not the
single test you were fixing: locators are shared across page objects, so a change that
fixes one test can break its neighbour.

**Phase 3** (Iterate, max 3 attempts). Re-run `diagnose` and repeat. Who decides depends
entirely on the verdict:

- **`locator_absent`, and the edit stays inside `framework/locators/`** - proceed without
  asking. The selector has been proven absent against the live page and the replacement is
  proven present, so there is no judgement left to confirm.
- **Every other verdict** - stop and ask, as before. `locator_present`, `locator_hidden`,
  `assertion`, `data` and `timing_unverified` all mean the locator is not the problem, and
  the right fix needs a human view of intent.

After 3 attempts, stop and escalate with: each verdict seen, what was changed, what the
gates said, and what you would try next. Three failed attempts usually means the
diagnosis is wrong, not that a fourth edit will land.

---

## Input Formats

| Format | Example | Result |
|--------|---------|--------|
| **Single file** | `/bdd-test-code-healer task_crud.feature` | Runs and heals one feature |
| **Multiple files** | `/bdd-test-code-healer file1.feature,file2.feature` | Runs all, heals each that fails |
| **Full path** | `/bdd-test-code-healer tests/features/task_crud.feature` | Accepts absolute or relative paths |

---

## Prerequisites

pytest + pytest-bdd installed, Tests have run before, Environment configured (`.env`), OpenShift cluster accessible, Test data exists (`framework/resources/test_data/`), POM framework (`framework/ui_components/`)

---

## Common Failure Patterns Detected

`diagnose` (Phase 0) settles the locator question with evidence. The pattern guide covers
everything it cannot: StaleElementReference, authentication, project creation, navigation,
Monaco editor behaviour, step-definition lookup, import/attribute/type errors, and the
timing and data patterns behind a `locator_present` or `assertion` verdict.

Use the verdict first, the patterns second. See [Failure Patterns Guide](references/failure-patterns.md)

---

## Approval Gate Details

**The gate stands for every verdict except one.** A `locator_absent` fix confined to
`framework/locators/` is applied without asking: the old selector was proven absent on the
live page and the new one proven present, so there is nothing left to approve. Everything
else still stops for you.

Each report shows: Test failure details, Root cause analysis, Proposed fix (before/after), Affected files, Rationale

**Your options**: "yes" (apply), "no" (skip), "show me the error" (full trace), "try X instead" (suggest alternative)

---

## Iterative Repair Strategy

**Attempt 1**: Most common fix for pattern
**Attempt 2**: Same error → Adjust (longer timeout, different locator); Different error → Address new cause
**Attempt 3**: Fallback approach
**After 3**: Report tries, recommend manual investigation

---

## Limitations

UI-only test fixes, Cannot fix app bugs, Requires runnable tests, No interactive debugging, Max 3 attempts.

`diagnose` can only re-probe when the page is in `.agent/sweep/page_map.yaml` and the
failure URL was recorded; otherwise it returns `timing_unverified` and you are back to
pattern matching. It also reports what is true *now* - a failure caused by transient
state may no longer reproduce when re-probed.

---

## Related Skills

- **`/bdd-test-code-generator`** - Generate new tests from plain English
- **`/multi-page-pom`** - Regenerate page objects if UI changed significantly

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2026-05-02
