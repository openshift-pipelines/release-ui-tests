# Known Issues and Skipped Tests

This document tracks known bugs and issues that cause test scenarios to be skipped in the automated test suite.

## Active Skipped Tests

### 1. TaskRun Delete Operation Failure

**Status**: 🔴 **ACTIVE** - Test Skipped
**Severity**: Medium
**Affected Test**: `tests/features/taskrun_crud_operations.feature::Delete TaskRun and verify removal`
**Tags**: `@skip @known_bug`

**Description**:
The TaskRun delete operation fails in the OpenShift Console UI. The delete confirmation modal either does not appear or the deletion fails silently after confirmation.

**Impact**:
- Users cannot delete TaskRuns via the UI
- Test coverage gap for delete functionality
- 1 scenario skipped in taskrun_crud_operations.feature

**Environment**:
- Affects: OCP 4.18.x (release-v4.18 branch)
- First Observed: 2026-06-14
- Last Verified: 2026-06-14

**Root Cause**:
UI regression in delete confirmation flow. Possible causes:
- Modal component not rendering
- Event handlers not firing
- API call failing silently
- RBAC/permissions issue

**Tracking**:
- Jira Issue: [Create issue and link here - e.g., OCPBUGS-XXXXX]
- GitHub Issue: [If applicable]
- Related PRs: [If any fixes in progress]

**Workaround**:
Use CLI deletion instead:
```bash
oc delete taskrun <taskrun-name> -n <namespace>
```

**Next Steps**:
1. [ ] Create Jira issue with detailed reproduction steps
2. [ ] Investigate UI console logs for errors
3. [ ] Check API network calls during delete operation
4. [ ] Verify RBAC permissions for delete operation
5. [ ] Test on OCP 4.19 when available
6. [ ] Re-enable test once bug is fixed and verified

**How to Re-enable**:
Once the bug is fixed:
1. Remove `@skip @known_bug` tags from the scenario
2. Verify the test passes: `pytest tests/features/taskrun_crud_operations.feature -k "Delete TaskRun"`
3. Update this document to mark issue as RESOLVED
4. Consider adding regression test

---

## Resolved Issues

*No resolved issues yet*

---

## How to Skip a Test

When you discover a new bug that blocks a test:

### 1. Tag the Scenario in Feature File

```gherkin
@skip @known_bug
# KNOWN BUG: Brief description
# Issue: Detailed description of the bug
# Affects: Which environments/versions
# Tracking: Link to Jira/GitHub issue
# Workaround: How to perform the action manually
Scenario: Your scenario name
  # ... test steps ...
```

### 2. Add Entry to This Document

Copy the template above and fill in all fields.

### 3. Create Tracking Issue

Create a Jira/GitHub issue with:
- Detailed reproduction steps
- Screenshots/logs if available
- Expected vs actual behavior
- Link to the skipped test scenario

### 4. Monitor and Re-enable

- Periodically check if the bug is fixed
- Re-run the test on new releases
- Remove @skip tag when verified fixed
- Update this document

---

## Test Execution

### Run All Tests (Skipped Tests Will Show)

```bash
pytest tests/features/ -v
```

Output will show skipped tests:
```
tests/features/taskrun_crud_operations.feature::test_delete_taskrun SKIPPED (known bug)
```

### Run Only Skipped Tests (For Verification)

```bash
pytest tests/features/ -m "skip or known_bug" -v
```

### Run Everything Except Skipped Tests

```bash
pytest tests/features/ -m "not skip and not known_bug" -v
```

### Force Run Skipped Tests (Override Skip)

```bash
pytest tests/features/ --runxfail -v
```

---

## Statistics

- **Total Skipped Tests**: 1
- **Last Updated**: 2026-06-14
- **Oldest Skipped Test**: Delete TaskRun (2026-06-14)

---

## Maintenance

This document should be reviewed:
- ✅ Before each release
- ✅ When new OCP versions are available
- ✅ Monthly during sprint planning
- ✅ When tests start failing unexpectedly
