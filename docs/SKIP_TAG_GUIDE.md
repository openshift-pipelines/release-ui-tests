# @skip Tag Implementation Guide

This guide explains how to skip test scenarios with known bugs using the `@skip` tag pattern.

## Quick Reference

```gherkin
@skip @known_bug
# KNOWN BUG: Brief description
# Issue: Detailed description
# Tracking: Jira/GitHub issue link
Scenario: Your failing scenario
  # ... test steps ...
```

The test will automatically be skipped when pytest runs.

---

## Implementation Complete ✅

### What Was Done

1. ✅ **Feature File Updated** - Added `@skip @known_bug` tag with detailed comments
2. ✅ **pytest.ini Updated** - Registered `skip` and `known_bug` markers
3. ✅ **conftest.py Updated** - Auto-skip hook implemented
4. ✅ **KNOWN_ISSUES.md Created** - Bug tracking documentation
5. ✅ **Verified Working** - Test successfully skipped

### Current State

**Skipped Test**: `Delete TaskRun and verify removal` in `taskrun_crud_operations.feature`

**Test Results**:
```
tests/steps/test_taskrun_crud_steps.py::test_delete_taskrun_and_verify_removal SKIPPED [100%]
```

---

## How It Works

### 1. Feature File with @skip Tag

**Location**: `tests/features/taskrun_crud_operations.feature`

```gherkin
@skip @known_bug
# KNOWN BUG: TaskRun delete operation fails in OpenShift Console
# Issue: Delete confirmation modal does not appear or deletion fails silently
# Affects: OCP 4.18.x (release-v4.18 branch)
# Root Cause: UI regression in delete confirmation flow
# Tracking: Create/link Jira issue here (e.g., OCPBUGS-XXXXX)
# Expected Fix: OCP 4.19 or upstream console fix
# Workaround: Use CLI deletion via `oc delete taskrun <name>`
# Last Verified: 2026-06-14
# TODO: Re-enable this test once bug is fixed and verified
Scenario Outline: Delete TaskRun and verify removal
  When the user navigates to TaskRuns tab
  And the user deletes the taskrun "<taskrun_name>"
  And the user navigates to the Tasks page
  And the user navigates to TaskRuns tab
  Then the taskrun "<taskrun_name>" should not appear in the taskruns list

  Examples:
    | taskrun_name      |
    | simple-taskrun-   |
```

**Tag Meaning**:
- `@skip` - Primary marker telling pytest to skip this scenario
- `@known_bug` - Additional context that this is a known bug (also triggers skip)

**Comment Fields** (all recommended):
- `KNOWN BUG:` - One-line summary
- `Issue:` - Detailed description
- `Affects:` - Which environments/versions
- `Root Cause:` - Why it's failing (if known)
- `Tracking:` - Link to Jira/GitHub issue
- `Expected Fix:` - When it will be fixed
- `Workaround:` - How to do it manually
- `Last Verified:` - When you last checked the bug still exists
- `TODO:` - Next action items

### 2. pytest.ini Configuration

**Location**: `pytest.ini`

```ini
[pytest]
markers =
    smoke
    e2e
    sanity
    integration
    regression
    skip: Skip test due to known issue or bug (see feature file for details)
    known_bug: Test skipped due to known bug in the application
```

This registers the markers so pytest recognizes them.

### 3. conftest.py Auto-Skip Hook

**Location**: `tests/conftest.py`

```python
import pytest


def pytest_collection_modifyitems(config, items):
    """
    Automatically skip test scenarios tagged with @skip or @known_bug.
    """
    for item in items:
        if "skip" in item.keywords:
            item.add_marker(
                pytest.mark.skip(reason="Scenario skipped - see feature file comments for known bug details")
            )
        elif "known_bug" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="Known bug - see feature file comments for tracking information"))
```

This hook runs after test collection and automatically adds `pytest.mark.skip` to any scenario with the `@skip` or `@known_bug` tag.

### 4. Bug Tracking Documentation

**Location**: `KNOWN_ISSUES.md`

Tracks all skipped tests with:
- Status and severity
- Detailed description
- Environment information
- Root cause analysis
- Tracking links
- Workarounds
- Re-enable steps

---

## Usage Guide

### Running Tests

#### Run All Tests (Shows Skipped)

```bash
pytest tests/steps/test_taskrun_crud_steps.py -v
```

**Output**:
```
test_create_taskrun... FAILED
test_verify_taskrun... FAILED
test_delete_taskrun... SKIPPED [100%]  ← Skipped test
```

#### Run Only Skipped Tests

```bash
pytest tests/ -m "skip or known_bug" -v
```

Useful for verifying which tests are currently skipped.

#### Run Everything Except Skipped

```bash
pytest tests/ -m "not skip and not known_bug" -v
```

Excludes all skipped tests from the run.

#### Show Skip Reasons

```bash
pytest tests/steps/test_taskrun_crud_steps.py -v -rs
```

The `-rs` flag shows reasons for skipped tests:
```
SKIPPED [1] scenario.py:296: Scenario skipped - see feature file comments
```

#### Force Run Skipped Tests (Override)

```bash
pytest tests/steps/test_taskrun_crud_steps.py --runxfail
```

⚠️ **Warning**: This will run the skipped test and it will likely fail.

### When to Skip a Test

Skip a test when:
- ✅ Known bug in the application (not the test)
- ✅ Bug is tracked in Jira/GitHub
- ✅ Bug will be fixed in future release
- ✅ Test worked before, broke due to app regression
- ✅ Multiple people have verified the bug

**Do NOT skip** when:
- ❌ Test is flaky (fix the test instead)
- ❌ Test data is wrong (fix the data)
- ❌ Locators changed (update the locators)
- ❌ You're not sure why it's failing (investigate first)

### Adding a New Skipped Test

**Step 1**: Tag the scenario in feature file

```gherkin
@skip @known_bug
# KNOWN BUG: [Brief description]
# Issue: [Detailed description]
# Tracking: [Jira link]
# Workaround: [Manual steps]
Scenario: Your scenario
  # ... steps ...
```

**Step 2**: Create tracking issue

Create Jira/GitHub issue with:
- Reproduction steps
- Expected vs actual behavior
- Screenshots/logs
- Link to the skipped test

**Step 3**: Update KNOWN_ISSUES.md

Add entry with all tracking information.

**Step 4**: Verify skip works

```bash
pytest tests/your_feature.feature -v
```

Should show scenario as SKIPPED.

### Re-enabling a Fixed Test

**Step 1**: Verify bug is fixed

Test manually in the application.

**Step 2**: Remove skip tags

```gherkin
# Remove these lines:
# @skip @known_bug
# KNOWN BUG: ...

Scenario: Your scenario  ← Keep this
  # ... steps ...
```

**Step 3**: Run test to verify

```bash
pytest tests/your_feature.feature -k "your scenario" -v
```

Should PASS now.

**Step 4**: Update documentation

- Move issue from "Active" to "Resolved" in KNOWN_ISSUES.md
- Add resolution date and version
- Close Jira/GitHub issue

---

## Best Practices

### Documentation Standards

**Minimum Required**:
```gherkin
@skip @known_bug
# KNOWN BUG: Brief description
# Tracking: Jira link
Scenario: ...
```

**Recommended**:
```gherkin
@skip @known_bug
# KNOWN BUG: Brief description
# Issue: Detailed explanation
# Affects: OCP 4.18.x
# Tracking: OCPBUGS-12345
# Workaround: Use CLI instead
# Last Verified: 2026-06-14
Scenario: ...
```

### Marker Usage

Use **both tags** for clarity:
```gherkin
@skip @known_bug  ← Both provide context
```

Either tag alone will work, but using both is clearer.

### Comment Format

Use consistent field names:
- `KNOWN BUG:` (not "BUG:" or "ISSUE:")
- `Issue:` (detailed description)
- `Tracking:` (not "Jira:" or "Link:")
- `Workaround:` (not "Alternative:")

### Periodic Review

Review skipped tests:
- **Before each release** - Check if bugs are fixed
- **Monthly** - Verify tracking info is current
- **When OCP versions change** - Test on new versions

---

## Troubleshooting

### Test Still Runs Despite @skip Tag

**Check**:
1. Verify tag is correctly formatted (no typos)
2. Run with `-v` to see if scenario is collected
3. Check `conftest.py` hook is loaded
4. Try explicit skip: `pytest -m "not skip"`

### Skip Reason Not Showing

Use `-rs` flag:
```bash
pytest tests/ -v -rs
```

### Want to Temporarily Run Skipped Test

```bash
# Option 1: Remove @skip from feature file
# Option 2: Use --runxfail flag
pytest tests/ --runxfail -k "delete"
```

### Multiple Tests Need to Skip

Add `@skip @known_bug` to each scenario individually:

```gherkin
@skip @known_bug
Scenario: First failing test
  # ...

@skip @known_bug
Scenario: Second failing test
  # ...
```

Or use a tag on the Feature level (skips ALL scenarios):
```gherkin
@skip @known_bug
Feature: Entire feature is broken
  # All scenarios will be skipped
```

---

## Statistics

**Current Status**:
- Total Skipped Tests: **1**
- Location: `taskrun_crud_operations.feature`
- Scenario: "Delete TaskRun and verify removal"
- Tagged: `@skip @known_bug`
- Status: Active (bug not fixed yet)

---

## File Locations

- **Feature Files**: `tests/features/*.feature`
- **Step Definitions**: `tests/steps/test_*_steps.py`
- **Configuration**: `pytest.ini`
- **Hook Implementation**: `tests/conftest.py`
- **Bug Tracking**: `KNOWN_ISSUES.md`
- **This Guide**: `docs/SKIP_TAG_GUIDE.md`

---

## Additional Resources

- [pytest skip documentation](https://docs.pytest.org/en/latest/how-to/skipping.html)
- [pytest-bdd markers](https://pytest-bdd.readthedocs.io/en/stable/#organizing-your-scenarios)
- Project KNOWN_ISSUES.md for active bug list

---

**Last Updated**: 2026-06-14
**Maintained By**: QE Team
**Status**: ✅ Active Implementation
