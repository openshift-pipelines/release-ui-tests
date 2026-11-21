# Implementation Guide

Detailed step-by-step implementation for all three phases of the BDD Test Code Healer skill.

---

## Overview

The skill operates in a loop with maximum 3 attempts:

```
Attempt 1: Run → Analyze → Fix → Verify → (Pass? Exit : Continue)
Attempt 2: Run → Analyze → Fix → Verify → (Pass? Exit : Continue)
Attempt 3: Run → Analyze → Fix → Verify → (Pass? Exit : Report Failure)
```

---

## Phase 1: Test Execution & Analysis

### Step 1: Parse Input

**Goal**: Extract feature file names from input.

**Input formats**:
```bash
# Single file (basename only)
task_crud_operations.feature

# Single file (full path)
tests/features/task_crud_operations.feature

# Multiple files (comma-separated)
task_crud.feature,pipeline_workflow.feature,trigger_tests.feature

# Multiple files (with paths)
tests/features/task_crud.feature,tests/features/pipeline_workflow.feature
```

**Actions**:
1. Split input by comma if present
2. Strip whitespace from each filename
3. Normalize paths (if relative, prepend `tests/features/`)
4. Verify files exist
5. Store as array for processing

**Output**:
```python
feature_files = ["tests/features/task_crud_operations.feature", "tests/features/pipeline_workflow.feature"]
```

---

### Step 2: Run Tests

**Goal**: Execute pytest and capture all output.

**IMPORTANT**: Show progress updates to the user during test execution.

**Before running tests, output**:
```markdown
## Running Tests in Headed Mode

**Feature**: {feature_file}
**Attempt**: {attempt_number}/3
**Mode**: Headed (visible browser for debugging)
**Strategy**: Stop on first failure (scenarios are dependent)

Executing: `pytest tests/steps/{step_file}.py -v --tb=short --headed -x`

⏳ Test execution in progress... (this may take 2-5 minutes)
```

**Command**:
```bash
pytest tests/steps/{step_file}.py -v --tb=short --headed -x 2>&1
```

**NOTE**: Use step definition file path (tests/steps/*.py) NOT feature file path (tests/features/*.feature) to ensure pytest can collect tests properly.

**Flags explained**:
- `-v` - Verbose output (shows test names)
- `--tb=short` - Short traceback format (easier to parse)
- `--headed` - Run browser in headed mode (visible for debugging)
- `-x` / `--exitfirst` - **CRITICAL: Stop on first failure** (scenarios have dependencies)
- `2>&1` - Capture both stdout and stderr

**Why `-x` flag?**
- **Scenario dependencies**: Test scenarios in BDD suites are often dependent (e.g., Create → Edit → Delete)
- **Cascade failures**: If "Create" fails, all subsequent scenarios will also fail (can't edit/delete something that wasn't created)
- **Faster feedback**: Stop immediately on first failure to start healing faster
- **Resource efficiency**: Don't waste time running scenarios that will definitely fail due to missing prerequisites

**Why headed mode?**
- Better visibility of UI interactions during test execution
- Easier to spot locator issues, timing problems, and navigation failures
- Can see exactly what's happening when tests fail

**Capture**:
- Exit code (0 = all passed, non-zero = failures)
- Full output (stdout + stderr)
- Duration

**Actions**:
```python
# Run in background to avoid blocking
exit_code, output, _ = await run_command_background(
    ["pytest", step_file, "-v", "--tb=short", "--headed"],
    check=False,  # Don't raise on non-zero exit
)

# While running, show periodic updates
# Poll output file every 30 seconds and show progress
```

**After test completion, output**:
```markdown
✅ Test execution complete ({duration}s)
```

---

### Step 3: Parse Test Results

**Goal**: Extract structured data from pytest output.

**Parse for**:
- Total tests run
- Tests passed
- Tests failed
- Failed test names
- Error messages per failed test
- Stack traces per failed test

**Parsing strategy**:

```python
# Example pytest output:
"""
tests/features/task_crud.feature::test_scenario[example1] FAILED
tests/features/task_crud.feature::test_scenario[example2] PASSED

================================= FAILURES =================================
_______ test_scenario[example1] _______

    @when(parsers.parse('the user clicks create button'))
    def click_create(page):
>       await page["tasks"].list.click_create_button()
E       playwright.async_api.TimeoutError: Element not found: button:has-text("Create")

framework/ui_components/tasks/tasks_page.py:45: TimeoutError
"""

# Parse into:
{
    "total": 2,
    "passed": 1,
    "failed": 1,
    "failures": [
        {
            "test_name": "test_scenario[example1]",
            "error_type": "playwright.async_api.TimeoutError",
            "error_message": 'Element not found: button:has-text("Create")',
            "file": "framework/ui_components/tasks/tasks_page.py",
            "line": 45,
            "stack_trace": "...",
        }
    ],
}
```

**Regex patterns**:
```python
# Extract failed test names
FAILED_PATTERN = re.compile(r"(.+?) FAILED")

# Extract error type
ERROR_TYPE_PATTERN = re.compile(r"E\s+(\w+(?:\.\w+)*Error):")

# Extract error message
ERROR_MSG_PATTERN = re.compile(r"E\s+\w+Error:\s+(.+)")

# Extract file and line
FILE_LINE_PATTERN = re.compile(r"(\S+\.py):(\d+):")
```

---

### Step 4: Check Results

**Goal**: Determine if healing is needed.

**Decision tree**:

```
Exit code == 0?
├─ YES → All tests passed → Report success, exit (no healing needed)
└─ NO  → Has failures → Continue to analysis
```

**For each feature file** (if multiple):
- Check if it has failures
- If all pass: skip healing for this file
- If any fail: add to healing queue

**Output**:
```python
healing_queue = [
    {
        "feature_file": "tests/features/task_crud.feature",
        "failures": [...],  # Parsed failure data
    },
    # Other files with failures
]
```

---

### Step 5: Analyze Failures (Core Logic)

**Goal**: Match failures to known patterns and identify root cause.

**For each failure**:

1. **Extract key details**:
   - Error type (e.g., `TimeoutError`, `AssertionError`)
   - Error message (e.g., `"Element not found: button:has-text('Create')"`)
   - File and line where error occurred
   - Stack trace

2. **Match to pattern**:

   Check against known patterns (in order of specificity):

   ```python
   patterns = [
       # Pattern 1: Locator not found
       {
           "name": "locator_not_found",
           "match": lambda err: "Element not found" in err["error_message"] or "TimeoutError" in err["error_type"],
           "analysis": analyze_locator_not_found,
           "fix_generator": generate_locator_fix,
       },
       # Pattern 2: Element not visible
       {
           "name": "element_not_visible",
           "match": lambda err: "not visible" in err["error_message"],
           "analysis": analyze_visibility_issue,
           "fix_generator": generate_visibility_fix,
       },
       # Pattern 3: Stale element
       {
           "name": "stale_element",
           "match": lambda err: "StaleElementReferenceException" in err["error_type"],
           "analysis": analyze_stale_element,
           "fix_generator": generate_stale_element_fix,
       },
       # ... more patterns (see failure-patterns.md)
   ]
   ```

3. **Run pattern analysis**:

   For matched pattern, call its `analysis` function:

   ```python
   def analyze_locator_not_found(failure_data):
       """
       Analyze why locator wasn't found.

       Returns:
           {
               "root_cause": "Button text changed in UI",
               "evidence": "Locator: button:has-text('Create')",
               "likely_fix": "Update locator to use data-test attribute or new text",
               "confidence": "high"
           }
       """
       # Extract locator from error message
       locator_match = re.search(r"Element not found: (.+)", failure_data["error_message"])
       locator = locator_match.group(1) if locator_match else "unknown"

       # Determine if text-based locator
       is_text_based = "has-text" in locator

       if is_text_based:
           return {
               "root_cause": "Button text likely changed in UI update",
               "evidence": f"Text-based locator: {locator}",
               "likely_fix": "Use data-test attribute or inspect UI for new text",
               "confidence": "high",
           }
       else:
           return {
               "root_cause": "Element structure changed or locator incorrect",
               "evidence": f"Locator: {locator}",
               "likely_fix": "Inspect page and update locator",
               "confidence": "medium",
           }
   ```

4. **Generate fix proposal**:

   Call pattern's `fix_generator` function:

   ```python
   def generate_locator_fix(failure_data, analysis):
       """
       Generate code changes to fix locator issue.

       Returns:
           {
               "file": "framework/locators/tasks.py",
               "changes": [
                   {
                       "old": 'CREATE_BUTTON = \'button:has-text("Create")\'',
                       "new": 'CREATE_BUTTON = \'button[data-test="create-task-button"]\'',
                       "line": 45
                   }
               ],
               "rationale": "Using data-test attribute is more stable than text matching"
           }
       """
       # Parse which locator failed from stack trace
       # Look up locator definition in codebase
       # Propose more stable alternative

       return {"file": "framework/locators/tasks.py", "changes": [...], "rationale": "..."}
   ```

---

### Step 6: Present Analysis Report

**CRITICAL**: Present complete analysis and STOP. Wait for explicit user approval.

**Report format** (use clear visual hierarchy with emojis and sections):

````markdown
## 🔍 Healing Analysis Report - Attempt {N}/3

---

### 📊 Test Execution Results

| Metric | Value |
|--------|-------|
| **Feature File** | {feature_file} |
| **Total Scenarios** | {total} |
| **✅ Passed** | {passed} |
| **❌ Failed** | {failed} |
| **Duration** | {duration}s |

---

### ❌ Failed Scenario Details

#### Scenario: "{scenario_name}"

**Error Type**: `{error_type}`

**Error Message**:
```
{error_message}
```

**Location**: `{file}:{line}`

**Stack Trace** (key frames):
```
{relevant_stack_trace_frames}
```

---

### 🔎 Root Cause Analysis

#### Pattern Detected
🏷️ **{pattern_name}**

#### What Went Wrong
{detailed_root_cause_explanation}

#### Evidence
- 📌 **{evidence_point_1}**
- 📌 **{evidence_point_2}**
- 📌 **{evidence_point_3}**

#### Confidence Level
{high|medium|low} - {confidence_reasoning}

---

### 🛠️ Proposed Fix

#### Files to Modify: {file_count}

##### Fix #{fix_number}: {file_name}

**File**: `{full_file_path}`
**Line**: {line_number}

**Current Code**:
```python
{old_code}
```

**Proposed Change**:
```python
{new_code}
```

**Rationale**: {detailed_explanation_of_why_this_fixes_the_issue}

---

### 📋 Fix Summary

- 🔧 {change_summary_1}
- 🔧 {change_summary_2}
- 🔧 {change_summary_3}

---

## 🛑 APPROVAL REQUIRED

**Do you approve this fix?**

- Reply **"yes"** to apply the fix and re-run tests
- Reply **"no"** to skip this fix
- Reply **"show me the error"** to see full stack trace
- Reply **"try X instead"** to suggest alternative approach

````

**Wait for user response** - DO NOT proceed to Phase 2 without approval.

---

## Phase 2: Fix Application & Verification

**IMPORTANT**: Only execute after user replies "yes" to approve the fix.

---

### Step 7: Apply Fixes

**Goal**: Modify code files as proposed in the fix.

**For each file change**:

1. **Read current file**:
   ```python
   current_content = await read_file(file_path)
   ```

2. **Apply change using Edit tool**:
   ```python
   await edit_file(file_path=file_path, old_string=change["old"], new_string=change["new"])
   ```

3. **Verify change applied**:
   ```python
   updated_content = await read_file(file_path)
   assert change["new"] in updated_content
   ```

**Error handling**:
- If Edit fails (old_string not found), try alternative strategies:
  - Read file, locate by line number, replace
  - If locator class, search for class definition and update
- If all strategies fail, report to user with manual fix instructions

**Report**:
```markdown
## Applying Fixes...

✅ Modified: framework/locators/tasks.py (line 45)
✅ Modified: framework/ui_components/tasks/tasks_page.py (line 78)

Fixes applied successfully.
```

---

### Step 8: Verify Fix (Re-run Tests)

**Goal**: Confirm tests now pass after applying fixes.

**IMPORTANT**: Show progress updates during verification.

**Before re-running, output**:
```markdown
## 🔄 Verifying Fix - Re-running Tests

**Attempt**: {attempt_number}/3
**Fixes Applied**: {number_of_fixes}
**Strategy**: Stop on first failure (scenarios are dependent)

Re-executing tests in headed mode to verify fix...

⏳ Running: `pytest tests/steps/{step_file}.py -v --tb=short --headed -x`

(Test execution in progress - typically 2-5 minutes)
```

**Actions**:

1. **Re-run same pytest command in headed mode with -x flag**:
   ```bash
   pytest tests/steps/{step_file}.py -v --tb=short --headed -x 2>&1
   ```

2. **While tests run, show periodic progress**:
   - If possible, tail the output file and show scenario completion status
   - Example: "✅ Scenario 1/5 completed..." every 30-60 seconds

3. **Parse results** (same as Step 3)

4. **Compare with previous run**:
   - Did same test pass this time?
   - Are there new failures?
   - Are failures different?

**After test completion, output**:
```markdown
✅ Verification complete ({duration}s)

Analyzing results...
```

---

### Step 9: Check Verification Results

**Decision tree**:

```
All tests pass?
├─ YES → Report success, exit (healing complete) ✅
└─ NO  → Check attempt count
         ├─ Attempt < 3 → Continue to Phase 3 (Iterative Repair) 🔄
         └─ Attempt >= 3 → Report failure, recommend manual investigation ❌
```

**Success outcome**:
```markdown
## ✅ Healing Complete - All Tests Passing!

---

### 📊 Summary

| Metric | Value |
|--------|-------|
| **Feature File** | task_crud_operations.feature |
| **Attempt** | 1/3 |
| **Result** | ✅ All tests now pass |
| **Duration** | 12.45s |

---

### 🛠️ Fixes Applied

✅ **Fix #1**: Updated CREATE_BUTTON locator to use data-test attribute
- **File**: `framework/locators/tasks.py:45`
- **Change**: Text-based selector → data-test attribute
- **Reason**: More stable and resilient to UI text changes

---

### ✅ Test Results (After Fix)

| Scenario | Status | Duration |
|----------|--------|----------|
| test_scenario[example1] | ✅ PASSED | 6.2s |
| test_scenario[example2] | ✅ PASSED | 6.25s |

**Total**: 2 passed in 12.45s

---

### 💡 Recommendation

Commit these fixes to version control:

```bash
git add framework/locators/tasks.py
git commit -m "Fix: Updated CREATE_BUTTON locator to use data-test attribute

- Changed from text-based selector to data-test attribute
- More resilient to UI text changes
- Fixed via /bdd-test-code-healer"
```
```

**Failure outcome** (< 3 attempts):
```markdown
## ⚠️ Tests Still Failing - Preparing Next Attempt

---

### 📊 Current Status

| Metric | Value |
|--------|-------|
| **Feature File** | task_crud_operations.feature |
| **Attempt** | 1/3 |
| **Result** | ❌ {N} test(s) still failing |

---

### ❌ New Error Detected

**Error Type**: `{error_type}`

**Error Message**:
```
{error_message}
```

**Location**: `{file}:{line}`

---

### 🔄 Next Steps

Analyzing new failure pattern and preparing Fix #2...
```

→ Continue to Phase 3

**Failure outcome** (>= 3 attempts):
```markdown
## ❌ Healing Failed - Manual Investigation Required

---

### 📊 Final Status

| Metric | Value |
|--------|-------|
| **Feature File** | task_crud_operations.feature |
| **Attempts** | 3/3 (Maximum reached) |
| **Result** | ❌ {N} test(s) still failing |

---

### 🔄 Fixes Attempted

| Attempt | Fix Applied | Outcome |
|---------|------------|---------|
| **1** | Updated CREATE_BUTTON locator | ❌ Still failed (same error) |
| **2** | Added explicit wait before click | ❌ Still failed (different error: element not clickable) |
| **3** | Added scroll into view + increased wait | ❌ Still failed |

---

### ❌ Final Error

**Error Type**: `{error_type}`

**Error Message**:
```
{final_error_message}
```

**Location**: `{file}:{line}`

**Stack Trace**:
```
{key_stack_frames}
```

---

### 💡 Manual Investigation Required

This issue requires deeper investigation beyond automated healing. Here's what to check:

#### 🔍 Debugging Steps

1. **Inspect UI Manually**
   - Open the page in browser and verify element exists
   - Check if there are overlays or modals blocking the element
   - Verify the element is not disabled by application logic

2. **Check Element State**
   - Is the element visible in the DOM?
   - Does it have the expected attributes?
   - Is it within the viewport?

3. **Review Application Logic**
   - Check if there are permission restrictions
   - Verify if there are loading states or async operations
   - Look for JavaScript errors in console

4. **Screenshot Analysis**
   - Add screenshot on failure to see page state
   - Compare with expected UI state

5. **Run with Headed Mode** (if not already)
   - Watch the browser interaction in real-time
   - Observe timing and element states

---

### 🛠️ Manual Debugging Commands

```bash
# Run single test in headed mode with verbose output
pytest tests/steps/test_task_crud_steps.py::test_scenario_name -v --headed --tb=long

# Run with Playwright debug mode
PWDEBUG=1 pytest tests/steps/test_task_crud_steps.py::test_scenario_name -v --headed

# Generate screenshot on failure
pytest tests/steps/test_task_crud_steps.py --screenshot=on -v --headed
```

---

### 📝 Next Steps

Consider these alternatives:

- **Update test approach**: Different interaction pattern may be needed
- **Add wait conditions**: More sophisticated wait strategies
- **Fix application bug**: Issue may be in the application, not the test
- **Update POM structure**: Page object may need refactoring
```

---

## Phase 3: Iterative Repair

**Trigger**: Tests still fail after applying fix (attempt < 3)

---

### Step 10: Analyze New Failure

**Goal**: Understand what changed after applying previous fix.

**Compare with previous failure**:
- Is it the **same error**? → Previous fix didn't work, need different approach
- Is it a **different error**? → Previous fix partially worked, revealed new issue

**Decision tree**:

```
Same error as before?
├─ YES → Previous fix strategy failed
│        → Try alternative fix for same pattern
│        → Example: If locator change didn't work, try adding wait
└─ NO  → Previous fix revealed new issue
         → Analyze new error as new pattern
         → Example: Fixed locator, now hitting "element not clickable"
```

---

### Step 11: Adjust Fix Strategy

**Goal**: Generate different fix based on what was learned.

**Strategy adjustment patterns**:

#### Same Error - Adjust Approach

```python
# Attempt 1 fix:
CREATE_BUTTON = 'button[data-test="create-button"]'

# Still fails with "Element not found"
# Attempt 2 fix: Maybe attribute name is different
CREATE_BUTTON = 'button[data-testid="create-button"]'

# Still fails
# Attempt 3 fix: Fallback to broader selector
CREATE_BUTTON = 'button.pf-c-button:has-text("Create")'
```

#### Different Error - Address New Issue

```python
# Attempt 1: Fixed locator
# Now failing with "Element not clickable"

# Attempt 2: Add wait + scroll into view
async def click_create_button(self):
    # Wait for element to be attached to DOM
    await self.page.wait_for_selector(self.locators.CREATE_BUTTON)
    # Scroll into view
    element = await self.page.query_selector(self.locators.CREATE_BUTTON)
    await element.scroll_into_view_if_needed()
    # Wait a bit for any animations
    await self.page.wait_for_timeout(500)
    # Now click
    return await self.click_element(self.locators.CREATE_BUTTON)
```

---

### Step 12: Present Updated Analysis Report

**Format** (same as Step 6, but with attempt history):

````markdown
## Healing Analysis Report - Attempt {N}/3

### Previous Attempts
**Attempt 1**: Updated locator → Still failed (same error)
**Attempt 2**: {what_was_tried} → {outcome}

### Current Failure Analysis

**Pattern detected**: {pattern_name}

**Root cause**: {updated_root_cause_analysis}

**Why previous fix didn't work**: {explanation}

### Proposed Fix (Attempt {N})

**Strategy**: {what_different_this_time}

**Files to modify**: {file_count}

#### Fix: {file_name}

**Change**:
```python
# Previous fix (didn't work):
{previous_attempted_code}

# New approach:
{new_code}
```

**Why this should work**: {rationale_based_on_learning}

---

## 🛑 APPROVAL REQUIRED

**Do you approve this fix?**

- Reply **"yes"** to apply and verify
- Reply **"no"** to stop healing and investigate manually
- Reply **"show history"** to see all attempts and their outcomes

````

**Wait for user response** - Loop back to Step 7 (Apply Fixes) if approved.

---

## Multiple Feature Files Handling

When input includes multiple feature files:

```python
for feature_file in feature_files:
    # Run test for this feature
    exit_code, output = run_test(feature_file)

    if exit_code == 0:
        # All passed, skip healing
        report_success(feature_file)
        continue

    # Has failures, needs healing
    attempt = 1
    max_attempts = 3

    while attempt <= max_attempts:
        # Phase 1: Analyze
        failures = parse_failures(output)
        analysis = analyze_failures(failures)
        fix_proposal = generate_fix(analysis)

        # Present and wait for approval
        present_report(feature_file, attempt, analysis, fix_proposal)
        approval = await get_user_approval()

        if approval != "yes":
            break  # User rejected, skip to next feature

        # Phase 2: Apply and verify
        apply_fixes(fix_proposal)
        exit_code, output = run_test(feature_file)

        if exit_code == 0:
            report_healing_success(feature_file, attempt)
            break  # Tests pass, done with this feature

        # Phase 3: Still failing
        if attempt >= max_attempts:
            report_healing_failure(feature_file, all_attempts)
            break  # Max attempts reached

        attempt += 1
        # Loop continues with new analysis

# After all features processed
print_summary(all_features, successes, failures, skipped)
```

---

## Edge Cases

### No Failures Detected

```markdown
## ✅ All Tests Passing

**Feature**: task_crud_operations.feature
**Total scenarios**: 5
**Result**: All passed

No healing needed.
```

### Cannot Parse Failures

```markdown
## ⚠️ Analysis Failed

**Feature**: task_crud_operations.feature
**Issue**: Could not parse test output

**Raw output**:
```
{full_pytest_output}
```

**Recommendation**: Review output manually and run with `-vv` flag for more details.
```

### Fix Application Fails

```markdown
## ❌ Fix Application Failed

**Attempt**: 1/3
**Issue**: Could not apply fix to framework/locators/tasks.py

**Error**: Old string not found in file

**What was attempted**:
```python
# Tried to replace:
CREATE_BUTTON = 'button:has-text("Create")'

# With:
CREATE_BUTTON = 'button[data-test="create-button"]'
```

**Recommendation**:
File may have changed since analysis. Please apply fix manually or re-run healing.

**Manual fix**:
Edit `framework/locators/tasks.py` line 45 and update CREATE_BUTTON locator.
```

---

## Summary

The healing workflow is:

1. **Run tests** → Capture failures
2. **Analyze** → Match to patterns, identify root cause
3. **Propose fix** → Generate code changes
4. **Wait for approval** → Present report, get user consent
5. **Apply fix** → Modify code files
6. **Verify** → Re-run tests
7. **Check result** → Pass? Success. Fail? Attempt < 3? Loop. Attempt >= 3? Give up.

**Key principles**:
- Never apply fixes without approval
- Learn from previous attempts
- Maximum 3 attempts per feature
- Process multiple features independently
- Provide manual investigation guidance if automated healing fails
