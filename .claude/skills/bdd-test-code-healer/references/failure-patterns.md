# Failure Patterns Guide

Comprehensive guide to the 15+ common test failure patterns the BDD Test Code Healer recognizes and how it fixes each one.

---

## Pattern Recognition System

Each pattern has:
- **Match criteria** - How to identify this pattern from error output
- **Root cause analysis** - What typically causes this
- **Fix strategies** - How to resolve (multiple approaches)
- **Confidence level** - How certain we are about the fix
- **Examples** - Real error messages and fixes

---

## Pattern 1: Locator Not Found

### Match Criteria
```python
error_type in ["TimeoutError", "ElementNotFoundError"]
AND "Element not found" in error_message
OR "No element matches selector" in error_message
```

### Error Examples
```
playwright.async_api.TimeoutError: Element not found: button:has-text("Create")
ElementNotFoundError: No element matches selector 'button[data-test="submit"]'
```

### Root Causes
1. **UI text changed** - Button says "Create Task" instead of "Create"
2. **Selector changed** - `data-test` attribute renamed or removed
3. **Element not rendered** - Conditional rendering based on permissions/state
4. **Wrong page** - Test navigated to wrong page, element doesn't exist there

### Fix Strategies

#### Strategy 1: Use More Stable Selector (Preferred)
```python
# Before (text-based, fragile):
CREATE_BUTTON = 'button:has-text("Create")'

# After (data-test attribute, stable):
CREATE_BUTTON = 'button[data-test="create-task-button"]'
```

**When to use**: Text-based locators or generic CSS selectors

**Confidence**: High

#### Strategy 2: Update Text
```python
# Before:
CREATE_BUTTON = 'button:has-text("Create")'

# After (if UI text changed):
CREATE_BUTTON = 'button:has-text("Create Task")'
```

**When to use**: When inspecting UI confirms text changed

**Confidence**: Medium (text may change again)

#### Strategy 3: Use Role-based Selector
```python
# Before:
CREATE_BUTTON = 'button:has-text("Create")'

# After:
CREATE_BUTTON = 'button[aria-label="Create task"]'
```

**When to use**: Element has proper ARIA attributes

**Confidence**: High

### Verification
After fix, check:
- ✅ Element is found
- ✅ Element is the correct one (not a different button with same locator)

---

## Pattern 2: Element Not Visible

### Match Criteria
```python
"not visible" in error_message.lower()
OR "element is hidden" in error_message.lower()
```

### Error Examples
```
AssertionError: Element is not visible: button[data-test="submit"]
TimeoutError: Element not visible within timeout: .modal-dialog
```

### Root Causes
1. **Timing issue** - Element loads after test tries to interact
2. **Scroll needed** - Element exists but not in viewport
3. **CSS display:none** - Element hidden by CSS
4. **Modal/overlay** - Element behind modal/overlay
5. **Animation** - Element transitioning, not yet visible

### Fix Strategies

#### Strategy 1: Add Explicit Wait for Visibility
```python
# Before:
async def click_submit(self):
    return await self.click_element(self.locators.SUBMIT_BUTTON)


# After:
async def click_submit(self):
    # Wait for element to be visible
    await self.page.wait_for_selector(self.locators.SUBMIT_BUTTON, state="visible", timeout=5000)
    return await self.click_element(self.locators.SUBMIT_BUTTON)
```

**Confidence**: High

#### Strategy 2: Scroll Into View
```python
# Before:
async def click_submit(self):
    return await self.click_element(self.locators.SUBMIT_BUTTON)


# After:
async def click_submit(self):
    element = await self.page.query_selector(self.locators.SUBMIT_BUTTON)
    await element.scroll_into_view_if_needed()
    await self.page.wait_for_timeout(300)  # Wait for scroll animation
    return await self.click_element(self.locators.SUBMIT_BUTTON)
```

**Confidence**: Medium

#### Strategy 3: Wait for Page Load State
```python
# Before:
await page["tasks"].list.click_create_button()

# After:
await page["raw_page"].wait_for_load_state("networkidle")
await page["tasks"].list.click_create_button()
```

**Confidence**: Medium

---

## Pattern 3: Element Not Clickable

### Match Criteria
```python
"not clickable" in error_message.lower()
OR "click intercepted" in error_message.lower()
OR "ElementClickInterceptedException" in error_type
```

### Error Examples
```
ElementClickInterceptedException: Element is not clickable at point (x, y). Other element would receive the click
TimeoutError: Element not clickable: button[data-test="submit"]
```

### Root Causes
1. **Overlay blocking** - Modal, dropdown, or notification on top
2. **Loading spinner** - Spinner overlay during page load
3. **Animation in progress** - Element animating, click hits wrong position
4. **Element disabled** - Button disabled but test tries to click

### Fix Strategies

#### Strategy 1: Wait for Clickable State
```python
# Before:
async def click_submit(self):
    return await self.click_element(self.locators.SUBMIT_BUTTON)


# After:
async def click_submit(self):
    # Wait for element to be clickable (visible + enabled)
    await self.page.wait_for_selector(self.locators.SUBMIT_BUTTON, state="visible")
    # Wait a bit for any overlays to clear
    await self.page.wait_for_timeout(500)
    return await self.click_element(self.locators.SUBMIT_BUTTON)
```

#### Strategy 2: Force Click
```python
# Before:
async def click_submit(self):
    return await self.click_element(self.locators.SUBMIT_BUTTON)


# After:
async def click_submit(self):
    # Force click (bypasses actionability checks)
    await self.page.click(self.locators.SUBMIT_BUTTON, force=True)
    return True
```

**Warning**: Use only when you're sure element should be clickable

---

## Pattern 4: Timeout Waiting for Element

### Match Criteria
```python
"TimeoutError" in error_type
AND "waiting for selector" in error_message.lower()
```

### Error Examples
```
TimeoutError: Timeout 30000ms exceeded while waiting for selector ".task-row"
```

### Root Causes
1. **Slow page load** - Page/element takes longer than default timeout
2. **Data load delay** - API call slow, data doesn't populate
3. **Wrong selector** - Element never appears because selector is wrong

### Fix Strategies

#### Strategy 1: Increase Timeout
```python
# Before (uses default 30s timeout):
async def verify_task_in_list(self, task_name: str):
    locator = self.locators.TASK_ROW.format(task_name=task_name)
    return await self.is_visible(locator)


# After:
async def verify_task_in_list(self, task_name: str):
    locator = self.locators.TASK_ROW.format(task_name=task_name)
    return await self.is_visible(locator, timeout=60000)  # 60s
```

#### Strategy 2: Wait for Network Idle
```python
# Before:
await page["tasks"].create.click_create()

# After:
await page["tasks"].create.click_create()
await page["raw_page"].wait_for_load_state("networkidle", timeout=60000)
```

---

## Pattern 5: Stale Element Reference

### Match Criteria
```python
"StaleElementReferenceException" in error_type
OR "stale element" in error_message.lower()
```

### Error Examples
```
StaleElementReferenceException: Element is no longer attached to the DOM
```

### Root Causes
1. **DOM refresh** - Page refreshed between finding element and interacting
2. **React re-render** - Component re-rendered, old element reference invalid
3. **Dynamic content** - Element removed and re-added

### Fix Strategies

#### Strategy 1: Re-query Element
```python
# Before:
async def click_task_row(self, task_name: str):
    row = await self.page.query_selector(f'tr:has-text("{task_name}")')
    await row.click()


# After:
async def click_task_row(self, task_name: str):
    # Use locator (auto-retries on stale element)
    locator = f'tr:has-text("{task_name}")'
    await self.page.click(locator)
```

#### Strategy 2: Add Retry Logic
```python
# Before:
async def get_task_status(self, task_name: str):
    row = await self.page.query_selector(f'tr:has-text("{task_name}")')
    status_cell = await row.query_selector(".status-cell")
    return await status_cell.text_content()


# After:
async def get_task_status(self, task_name: str):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            row = await self.page.query_selector(f'tr:has-text("{task_name}")')
            status_cell = await row.query_selector(".status-cell")
            return await status_cell.text_content()
        except StaleElementReferenceException:
            if attempt == max_retries - 1:
                raise
            await self.page.wait_for_timeout(500)
```

---

## Pattern 6: Assertion Failed (Value Mismatch)

### Match Criteria
```python
"AssertionError" in error_type
AND ("expected" in error_message.lower() OR "actual" in error_message.lower())
```

### Error Examples
```
AssertionError: Expected task name 'my-task' but got 'my-task-2'
AssertionError: assert 'Running' == 'Succeeded'
```

### Root Causes
1. **Test data mismatch** - YAML file has different name than expected
2. **Timing issue** - Checked status before it updated
3. **UI display change** - UI shows value differently
4. **Logic error** - Test expectation is wrong

### Fix Strategies

#### Strategy 1: Update Test Data
```python
# Test expects: task name = "my-task"
# YAML has: name: "my-task-2"

# Fix: Update YAML file
# Before:
metadata:
  name: my-task-2

# After:
metadata:
  name: my-task
```

#### Strategy 2: Update Assertion
```python
# Before (expects exact match):
assert status == "Succeeded"

# After (allows multiple valid states):
assert status in ["Succeeded", "Complete"]
```

#### Strategy 3: Add Wait for Expected State
```python
# Before:
status = await page["pipelinerun"].details.get_status()
assert status == "Succeeded"

# After:
# Wait for status to update (async operation)
for _ in range(10):  # Retry up to 10 times
    status = await page["pipelinerun"].details.get_status()
    if status == "Succeeded":
        break
    await page["raw_page"].wait_for_timeout(2000)
else:
    raise AssertionError(f"Status never reached 'Succeeded', last value: {status}")
```

---

## Pattern 7: File Not Found (Test Data)

### Match Criteria
```python
"FileNotFoundError" in error_type
OR "No such file or directory" in error_message
```

### Error Examples
```
FileNotFoundError: [Errno 2] No such file or directory: 'framework/resources/test_data/tasks/simple_task.yaml'
```

### Root Causes
1. **File renamed** - YAML file renamed but test not updated
2. **File moved** - File in different directory
3. **File deleted** - File removed from repo
4. **Path error** - Incorrect path in step definition

### Fix Strategies

#### Strategy 1: Fix Path
```python
# Before (incorrect path):
yaml_path = Path("framework/resources/test_data/simple_task.yaml")

# After (correct path):
yaml_path = Path("framework/resources/test_data/tasks/simple_task.yaml")
```

#### Strategy 2: Update Filename Reference
```gherkin
# Before (in feature file):
Examples:
  | yaml_file        |
  | simple_task.yaml |

# After (file was renamed):
Examples:
  | yaml_file                |
  | simple_task_updated.yaml |
```

---

## Pattern 8: YAML Parsing Error

### Match Criteria
```python
"YAMLError" in error_type
OR "yaml.scanner.ScannerError" in error_type
OR "Invalid YAML" in error_message
```

### Error Examples
```
yaml.scanner.ScannerError: while scanning a simple key, line 5, column 1
Invalid YAML syntax in file: task.yaml
```

### Root Causes
1. **Indentation error** - YAML requires 2-space indentation
2. **Invalid character** - Tab used instead of spaces
3. **Missing colon** - Key without value
4. **Unquoted special characters** - Colon in string not quoted

### Fix Strategies

#### Strategy 1: Fix Indentation
```yaml
# Before (incorrect indentation):
spec:
  steps:
  - name: build
      image: node:16

# After:
spec:
  steps:
    - name: build
      image: node:16
```

#### Strategy 2: Quote Special Characters
```yaml
# Before (unquoted colon):
- name: deploy
  script: echo Deploy to: production

# After:
- name: deploy
  script: "echo Deploy to: production"
```

---

## Pattern 9: Authentication Failure

### Match Criteria
```python
"authentication" in error_message.lower()
OR "login failed" in error_message.lower()
OR "401 Unauthorized" in error_message
```

### Error Examples
```
RuntimeError: Login with credentials failed. Check CONSOLE_USERNAME and CONSOLE_PASSWORD
AssertionError: Login form still visible after login attempt
```

### Root Causes
1. **Expired credentials** - Password changed, token expired
2. **Wrong credentials** - `.env` file has incorrect values
3. **Environment not set** - `.env` file not loaded
4. **Cluster inaccessible** - OpenShift cluster down

### Fix Strategies

#### Strategy 1: Update Credentials
```bash
# Check .env file
cat .env

# Update if needed
CONSOLE_USERNAME=kubeadmin
CONSOLE_PASSWORD=<new-password>
```

#### Strategy 2: Refresh Token
```bash
# For token-based auth
oc login --token=<new-token> --server=https://api.cluster.example.com:6443

# Update .env
OC_TOKEN=<new-token>
```

**Note**: This fix often requires manual intervention. Skill will detect and recommend user action.

---

## Pattern 10: Project Creation Failure

### Match Criteria
```python
"RuntimeError: Failed to create test project" in error_message
OR "oc new-project failed" in error_message
```

### Error Examples
```
RuntimeError: Failed to create test project: release-ui-test-abc123
Error: Project 'release-ui-test-xyz' already exists
```

### Root Causes
1. **Cluster quota exceeded** - Too many projects
2. **Permission denied** - User can't create projects
3. **Name conflict** - Project name already exists (rare, random suffix)

### Fix Strategies

#### Strategy 1: Clean Up Old Projects
```bash
# List test projects
oc get projects | grep release-ui-test

# Delete old ones
oc delete project release-ui-test-old123
```

#### Strategy 2: Use Different Namespace
```python
# Before (in test fixture):
project_name = openshift_cli.generate_random_project_name()

# After (longer random suffix):
import random
import string

suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
project_name = f"release-ui-test-{suffix}"
```

**Note**: This is a test infrastructure issue, skill will recommend manual cleanup.

---

## Pattern 11: Navigation Failure

### Match Criteria
```python
"NavigationError" in error_type
OR "Failed to navigate" in error_message
OR "Page did not load" in error_message
```

### Error Examples
```
AssertionError: Failed to navigate to Tasks page - page not loaded
TimeoutError: Page did not load within timeout: /tasks/ns/test-project
```

### Root Causes
1. **Wrong URL** - URL pattern changed
2. **Page structure changed** - Navigation links moved
3. **Permission issue** - User can't access page
4. **Slow network** - Page loads very slowly

### Fix Strategies

#### Strategy 1: Update URL Pattern
```python
# Before:
TASKS_URL = re.compile(r"pipelines/ns/[^/?#]+/tasks")

# After (URL structure changed):
TASKS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Task")
```

#### Strategy 2: Update Navigation Method
```python
# Before:
async def navigate_to_tasks(self):
    await self.page.click('a:has-text("Tasks")')


# After (link selector changed):
async def navigate_to_tasks(self):
    await self.page.click('[data-test="nav-item-tasks"]')
```

---

## Pattern 12: Step Definition Not Found

### Match Criteria
```python
"StepDefinitionNotFoundError" in error_type
OR "No step definition found" in error_message
```

### Error Examples
```
StepDefinitionNotFoundError: No step definition for: When the user creates a pipeline from YAML
```

### Root Causes
1. **Step renamed** - Step definition function name changed
2. **Step pattern changed** - Regex pattern doesn't match
3. **Import missing** - Step file not imported in `__init__.py`
4. **Typo in feature file** - Step text doesn't match pattern

### Fix Strategies

#### Strategy 1: Fix Feature File
```gherkin
# Before (typo):
When the user create a task from YAML

# After:
When the user creates a task from YAML
```

#### Strategy 2: Update Step Pattern
```python
# Before (too specific):
@when(parsers.parse('the user creates a task from YAML file "{yaml_file}"'))

# After (more flexible):
@when(parsers.parse('the user creates a task from {file_type} file "{yaml_file}"'))
```

---

## Pattern 13: Import Error

### Match Criteria
```python
"ImportError" in error_type
OR "ModuleNotFoundError" in error_type
```

### Error Examples
```
ImportError: cannot import name 'YamlLoader' from 'framework.helpers.yaml_loader'
ModuleNotFoundError: No module named 'pytest_bdd'
```

### Root Causes
1. **Missing dependency** - Package not installed
2. **Module renamed** - Import path changed
3. **Circular import** - Two modules importing each other
4. **Python path issue** - Module not in PYTHONPATH

### Fix Strategies

#### Strategy 1: Install Missing Dependency
```bash
pip install pytest-bdd playwright
```

#### Strategy 2: Update Import Path
```python
# Before:
from framework.helpers.yaml_loader import YamlLoader

# After (module renamed):
from framework.helpers.yaml_utils import YamlLoader
```

**Note**: Import errors often need manual intervention. Skill will detect and recommend user action.

---

## Pattern 14: Attribute Error (Method Not Found)

### Match Criteria
```python
"AttributeError" in error_type
AND "has no attribute" in error_message
```

### Error Examples
```
AttributeError: 'TasksPage' object has no attribute 'click_create_button'
```

### Root Causes
1. **Method renamed** - POM method name changed
2. **Method removed** - Method deleted from class
3. **Wrong page object** - Using wrong page instance
4. **Typo** - Method name misspelled

### Fix Strategies

#### Strategy 1: Update Method Call
```python
# Before:
await page["tasks"].list.click_create_button()

# After (method renamed):
await page["tasks"].list.click_create()
```

#### Strategy 2: Add Missing Method
```python
# Add to TasksPage class:
async def click_create_button(self):
    """Click the Create button to open resource creation dropdown."""
    return await self.click_element(self.locators.CREATE_BUTTON)
```

---

## Pattern 15: Type Error (Parameter Mismatch)

### Match Criteria
```python
"TypeError" in error_type
AND ("takes" in error_message OR "got" in error_message)
```

### Error Examples
```
TypeError: create_task_from_yaml() takes 3 positional arguments but 4 were given
TypeError: verify_task_in_list() missing 1 required positional argument: 'task_name'
```

### Root Causes
1. **Method signature changed** - Parameters added/removed
2. **Missing parameter** - Required parameter not passed
3. **Extra parameter** - Passing too many arguments

### Fix Strategies

#### Strategy 1: Update Method Signature
```python
# Before:
def create_task_from_yaml(page, yaml_file):
    pass


# After (added missing parameter):
def create_task_from_yaml(page, yaml_file, playwright_event_loop):
    pass
```

#### Strategy 2: Update Method Call
```python
# Before:
create_task_from_yaml(page, "task.yaml")

# After (added missing argument):
create_task_from_yaml(page, "task.yaml", event_loop)
```

---

## Pattern Matching Priority

When multiple patterns could match, use this priority order:

1. **Specific error types first** - StaleElementReferenceException, FileNotFoundError
2. **Context-specific patterns** - Authentication, Navigation, Project creation
3. **Generic patterns last** - TimeoutError, AssertionError

**Example**:
- If error is `TimeoutError: Element not found: button...`
  - Could match Pattern 1 (Locator Not Found) OR Pattern 4 (Timeout)
  - Choose Pattern 1 (more specific - knows it's a locator issue)

---

## Summary

The skill recognizes **15 common patterns** covering:
- **Locators**: Not found, not visible, not clickable
- **Timing**: Timeouts, stale elements, waits needed
- **Test data**: File not found, YAML parsing errors
- **Infrastructure**: Authentication, project creation, navigation
- **Code issues**: Step definitions, imports, attributes, types

Each pattern has **multiple fix strategies** that are tried in order of confidence level. The skill learns from failed attempts and adjusts approach for subsequent attempts.
