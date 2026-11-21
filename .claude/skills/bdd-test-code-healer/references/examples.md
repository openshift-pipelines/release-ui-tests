# Examples

## Example 1: Locator Changed

**Input**:
```bash
/bdd-test-code-healer task_crud_operations.feature
```

**Test Output**:
```
FAILED: Element not found: button:has-text("Create")
```

**Analysis Report**:
```markdown
## Healing Analysis Report - Attempt 1/3

### Test Results
- **Feature**: task_crud_operations.feature
- **Failed**: 1 scenario
- **Error Type**: Locator not found

### Root Cause
Button locator `button:has-text("Create")` not found on page.

**Likely cause**: UI text changed from "Create" to "Create Task" or button structure changed.

### Proposed Fix
**File**: `framework/locators/tasks.py`

**Change**:
```python
# Before:
CREATE_BUTTON = 'button:has-text("Create")'

# After:
CREATE_BUTTON = 'button[data-test="create-task-button"]'
```

**Why**: Using data-test attribute is more stable than text matching.

**Approve fix? (yes/no)**
```

**User**: `yes`

**Outcome**: Fix applied, test re-runs, passes ✅

---

## Example 2: Timing Issue (Needs 2 Attempts)

**Attempt 1**: Added `wait_for_timeout(1000)` → Still fails
**Attempt 2**: Increased to `wait_for_timeout(3000)` + added explicit `wait_for_selector` → Passes ✅

---

## Example 3: Multiple Files

**Input**:
```bash
/bdd-test-code-healer task_crud.feature,pipeline_workflow.feature,trigger_tests.feature
```

**Results**:
- `task_crud.feature` - ✅ All pass, no healing needed
- `pipeline_workflow.feature` - ❌ Failed, healed successfully on attempt 1
- `trigger_tests.feature` - ❌ Failed, healed successfully on attempt 2
