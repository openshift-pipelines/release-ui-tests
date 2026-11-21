# Learnings from PipelineRun CRUD Generation

This document captures all issues encountered and fixes applied when generating `tests/features/pipelinerun_crud_operations.feature` using `/bdd-test-code-generator`, and subsequent fixes via `/bdd-test-code-healer` and direct prompts.

**Purpose**: Ensure future code generation produces working code from the start by incorporating these learnings.

---

## Summary of Issues

| # | Issue | Root Cause | Fix | Learning |
|---|-------|------------|-----|----------|
| 1 | Wrong navigation pattern | Didn't detect PipelineRuns is a tab | Navigate to Pipelines page first | Detect tab vs standalone page |
| 2 | Created wrong step definition | Didn't check existing steps | Used existing navigation step | Check for existing steps first |
| 3 | Wrong fixture access (`pipelines.base`) | Misunderstood POM hierarchy | Changed to `pipelines.list` | Understand fixture hierarchy |
| 4 | Split Create button action | Didn't check for combo methods | Used `click_create_pipeline_run()` | Look for combo methods |
| 5 | Form doesn't submit | Monaco editor handling | (Ongoing investigation) | Verify Monaco content before submit |
| 6 | Missing `get_pipelinerun_status()` | Didn't mirror TaskRuns pattern | Created matching method | Mirror existing patterns |
| 7 | No polling in status check | Immediate check instead of retry | Added retry loop with logging | Status needs polling for async |
| 8 | PipelineRunsPage in wrong dir | Inconsistent structure | Moved to `pipelineruns/` | Match TaskRuns structure |
| 9 | Missing logger initialization | Didn't add logger to classes | Added `self.logger = logging.getLogger(__name__)` | Initialize logger when used |
| 10 | Project selector flakiness | No retry logic | Added retry, waits, verification | Critical nav needs retries |
| 11 | Skip tour button errors | No error handling for optional UI | Wrapped in try-except | Optional UI needs defensive code |
| 12 | CLI login repeated | No session-level tracking | Added `_cli_logged_in` flag | One-time ops need session flags |

---

## Detailed Issues and Fixes

### Issue 1: Wrong Navigation Pattern

**Generated Code (Wrong):**
```gherkin
Background:
  Given the user is logged into openshift console
  When the user expands Pipelines in left navigation bar
  And the user navigates to the PipelineRuns page    # ❌ Wrong
  And user switches to current project
```

**Fixed Code:**
```gherkin
Background:
  Given the user is logged into openshift console
  When the user expands Pipelines in left navigation bar
  And the user navigates to the Pipelines page      # ✅ Correct
  And user switches to current project

Scenario:
  When the user navigates to PipelineRuns tab       # ✅ Navigate to tab in scenario
```

**Root Cause**: Generator didn't understand that PipelineRuns is a **tab** on the Pipelines page, not a standalone page.

**Learning**:
- **Detect tab-based navigation**: Check if the target is a tab (PipelineRuns tab, TaskRuns tab) or standalone page (Tasks page, Pipelines page)
- **Background navigation**: Navigate to the **parent page** in Background
- **Scenario navigation**: Navigate to specific **tabs** within scenarios
- **Check existing steps**: Look for "the user navigates to {Resource}Runs tab" steps before creating new ones

**How to Detect Tabs**:
- URL pattern: `/pipelines/ns/...` = Pipelines page with tabs (Pipelines tab, PipelineRuns tab, Repositories tab)
- URL pattern: `/tasks/ns/...` = Tasks page with tabs (Tasks tab, TaskRuns tab)
- If resource name ends with "Runs" and has a parent resource (PipelineRuns → Pipelines, TaskRuns → Tasks), it's likely a tab

---

### Issue 2: Created Wrong Step Definition

**Generated Code (Wrong):**
```python
# tests/steps/test_navigation_steps.py
@when("the user navigates to the PipelineRuns page")
def user_navigates_to_pipelineruns_page(...):
    await page["nav"].navigate_to_pipelineruns()  # ❌ Method doesn't exist
```

**Fixed Code:**
```python
# Use existing step from test_navigation_steps.py
@when("the user navigates to PipelineRuns tab")
def user_navigates_to_pipeline_runs_tab(...):
    await page["pipelines"].list.navigate_to_pipeline_runs_tab()  # ✅ Correct
```

**Root Cause**: Generator created a new step without checking if an existing step already handled this navigation.

**Learning**:
- **Check existing navigation steps FIRST**: Before generating new navigation steps, grep for existing ones:
  ```bash
  grep -r "navigates to.*PipelineRuns" tests/steps/test_navigation_steps.py
  ```
- **Reuse existing steps**: If a step exists, use it in the feature file instead of creating a duplicate
- **Understand step patterns**:
  - `"the user navigates to {Page} page"` → Standalone pages
  - `"the user navigates to {Tab} tab"` → Tabs within a page

**Implementation Checklist**:
1. Parse intent to identify navigation target (e.g., "PipelineRuns")
2. Check if target is a tab or standalone page
3. Search existing steps for matching pattern
4. If exists: Use it
5. If not: Generate new step with correct pattern

---

### Issue 3: Wrong Fixture Access

**Generated Code (Wrong):**
```python
# tests/steps/test_pipelinerun_crud_steps.py
await page["pipelines"].base.click_create_button()  # ❌ Wrong
```

**Fixed Code:**
```python
await page["pipelines"].list.click_create_button()  # ✅ Correct
```

**Root Cause**: Generator used `base` (which refers to the base class) instead of `list` (the fixture key for the Pipelines list page).

**Learning**:
- **Understand fixture hierarchy**: Read `framework/fixtures/ui_fixtures.py` to understand the structure:
  ```python
  page["pipelines"] = PipelinesPages container:
      .list = PipelinesPage (Pipelines list page)
      .runs = PipelineRunsPage (PipelineRuns tab)
      .pipeline = PipelinePages container (details, yaml, etc.)
      .pipelinerun = PipelineRunPages container (details, yaml, etc.)
  ```
- **Never use `.base`** as a fixture accessor - it's not a valid key
- **Use the correct page**:
  - List page actions: `page["pipelines"].list.*`
  - Tab page actions: `page["pipelines"].runs.*`
  - Details page actions: `page["pipelines"].pipeline.details.*`

**How to Determine Correct Fixture Access**:
1. Identify the page type from URL:
   - `/pipelines/ns/...` → `page["pipelines"].list`
   - `/pipelines/ns/.../pipeline-runs` → `page["pipelines"].runs` (PipelineRuns tab)
   - `/k8s/ns/.../tekton.dev~v1~Pipeline/my-pipeline` → `page["pipelines"].pipeline.details`
2. Read ui_fixtures.py docstring to confirm structure
3. Use the correct accessor in generated code

---

### Issue 4: Split Create Button Action

**Generated Code (Wrong):**
```python
# Two-step approach
await page["pipelines"].list.click_create_button()
await page["raw_page"].wait_for_timeout(500)
await page["pipelines"].list.click_create_pipeline_run_menu_item()
```

**Fixed Code:**
```python
# Single combo method
await page["pipelines"].list.click_create_pipeline_run()  # ✅ Does both steps
```

**Root Cause**: Generator split a composite action into two steps without checking if a combo method existed.

**Learning**:
- **Check for combo methods**: Many base pages have combo methods that combine dropdown + menu item clicks:
  - `click_create_pipeline_run()` = `click_create_button()` + `click_create_pipeline_run_menu_item()`
  - `click_create_task_run()` = `click_create_button()` + `click_create_task_run_menu_item()`
- **Prefer combo methods**: They handle timing, waits, and proper sequencing automatically
- **Where to look**: Check base page classes (e.g., `PipelinesBasePage`, `TasksBasePage`) for combo methods

**Pattern**:
```python
# ❌ Don't split:
await page[resource].list.click_create_button()
await page[resource].list.click_create_{resource_type}_menu_item()

# ✅ Use combo:
await page[resource].list.click_create_{resource_type}()
```

---

### Issue 5: Monaco Editor Content Not Set (Ongoing)

**Observed Behavior**:
- YAML editor fills correctly
- Create button clicked
- URL stays at `/~new` (doesn't redirect)
- Error: Page title still "Create PipelineRun"

**Suspected Root Cause**: Monaco editor content not properly set or validated before clicking Create.

**Learning** (Preliminary):
- **Use MonacoEditor component**: Access via `page[resource].create_run.monaco_editor.set_content(yaml_content)`
- **Verify content set**: Check return value or verify content before submitting
- **Wait for editor ready**: Ensure Monaco editor is fully loaded before setting content
- **Validation errors**: Check for inline validation errors in the YAML editor

**Recommended Pattern**:
```python
# Wait for editor ready
editor_ready = await page[resource].create_run.monaco_editor.wait_for_editor_ready()
assert editor_ready, "Monaco editor not ready"

# Set content
yaml_filled = await page[resource].create_run.monaco_editor.set_content(yaml_content)
assert yaml_filled, f"Failed to fill YAML editor"

# Verify content was set (future: add verification method)
# content = await page[resource].create_run.monaco_editor.get_content()
# assert content == yaml_content, "Content mismatch"

# Wait for validation
await page["raw_page"].wait_for_timeout(1000)

# Click Create
create_clicked = await page[resource].create_run.click_create()
assert create_clicked, "Failed to click Create button"
```

---

### Issue 6: Missing `get_pipelinerun_status()` Method

**Problem**: Generated step used `page["pipelines"].runs.get_pipelinerun_status()` but method didn't exist.

**Generated Code Had**:
```python
# framework/ui_components/pipelines/pipeline_runs_page.py
async def verify_pipelinerun_status(self, pipelinerun_name: str, expected_status: str) -> bool:
    # Returns boolean, not status string
```

**Needed**:
```python
# framework/ui_components/pipelineruns/pipeline_runs_page.py
async def get_pipelinerun_status(self, pipelinerun_name: str) -> str:
    # Returns status string: 'Succeeded', 'Failed', 'Running'
```

**Root Cause**: Generator didn't look at the TaskRuns pattern and mirror the implementation.

**Learning**:
- **Mirror existing patterns**: If generating for PipelineRun, look at TaskRun as reference
  - TaskRunsPage location: `framework/ui_components/taskruns/task_runs_page.py`
  - PipelineRunsPage location: `framework/ui_components/pipelineruns/pipeline_runs_page.py` (not `pipelines/`)
- **Match method signatures**:
  - `get_{resource}_status(name: str) -> str` returns status text
  - `verify_{resource}_status(name: str, expected: str) -> bool` returns match boolean
- **Status retrieval pattern**:
  ```python
  async def get_{resource}_status(self, {resource}_name: str) -> str:
      row_locator = self.locators.{RESOURCE}_ROW_BY_NAME.format({resource}_name={resource}_name)
      await self.page.wait_for_selector(row_locator, timeout=5000)
      status_locator = f"{row_locator} >> [data-test='status-text']"
      # ... get status text
      return status_text.strip()
  ```

**Mirroring Checklist**:
1. Identify the similar resource (TaskRun → PipelineRun)
2. Read the reference file (taskruns/task_runs_page.py)
3. Copy method signatures and implementation patterns
4. Adapt variable names to new resource
5. Place in parallel directory structure

---

### Issue 7: No Polling in Status Verification

**Generated Code (Wrong):**
```python
# tests/steps/test_pipelinerun_crud_steps.py
async def verify_pipelinerun_status(...):
    # Immediate check, no retry
    status_matches = await page["pipelines"].runs.verify_pipelinerun_status(
        pipelinerun_name, pipelinerun_status
    )
    assert status_matches, f"Status doesn't match"
```

**Fixed Code:**
```python
async def verify_pipelinerun_status(...):
    max_wait_seconds = 60
    retry_interval_seconds = 20
    max_attempts = (max_wait_seconds // retry_interval_seconds) + 1

    for attempt in range(1, max_attempts + 1):
        # Wait for data load
        data_loaded = await page["pipelines"].runs.verify_pipeline_runs_tab_data_load()
        assert data_loaded

        # Get status
        actual_status = await page["pipelines"].runs.get_pipelinerun_status(pipelinerun_name)
        logger.info(f"Attempt {attempt}/{max_attempts}: status is '{actual_status}'")

        # Check match
        if actual_status.lower() == pipelinerun_status.lower():
            return  # Success

        # Wait before retry
        if attempt < max_attempts:
            await asyncio.sleep(retry_interval_seconds)

    # All attempts exhausted
    assert False, f"Status '{actual_status}' after {max_wait_seconds}s, expected '{pipelinerun_status}'"
```

**Root Cause**: Generator didn't implement polling/retry logic for asynchronous resource status checks.

**Learning**:
- **Async resources need polling**: PipelineRuns, TaskRuns take time to execute - status changes asynchronously
- **Retry pattern**:
  - Max wait time: 60s for runs (120s for slower resources)
  - Retry interval: 20s (balance between responsiveness and load)
  - Max attempts: `(max_wait / interval) + 1`
- **Logging**: Log each attempt with attempt number and current status
- **Early return**: Return immediately on success (don't wait full time)
- **Data load verification**: Reload list data before each status check

**Pattern**:
```python
# For status verification of async resources
max_wait_seconds = 60  # Or 120 for slower resources
retry_interval_seconds = 20
max_attempts = (max_wait_seconds // retry_interval_seconds) + 1

for attempt in range(1, max_attempts + 1):
    # Reload data
    await page[resource].runs.verify_{resource}_runs_tab_data_load()

    # Get current status
    actual_status = await page[resource].runs.get_{resource}_status(name)
    logger.info(f"Attempt {attempt}/{max_attempts}: '{name}' status='{actual_status}'")

    # Check if matches
    if actual_status.lower() == expected_status.lower():
        logger.info(f"'{name}' reached expected status '{expected_status}'")
        return

    # Wait before retry (not on last attempt)
    if attempt < max_attempts:
        logger.info(f"Waiting {retry_interval_seconds}s before retry...")
        await asyncio.sleep(retry_interval_seconds)

# Timeout
assert False, f"'{name}' has status '{actual_status}' after {max_wait_seconds}s, expected '{expected_status}'"
```

---

### Issue 8: PipelineRunsPage in Wrong Directory

**Generated Structure (Wrong):**
```
framework/ui_components/
  pipelines/
    pipeline_runs_page.py  # ❌ Wrong location
  taskruns/
    task_runs_page.py      # ✅ Correct location
```

**Fixed Structure:**
```
framework/ui_components/
  pipelineruns/
    pipeline_runs_page.py  # ✅ Moved here
  taskruns/
    task_runs_page.py      # ✅ Parallel structure
```

**Root Cause**: Inconsistent directory structure - list pages should be in resource-specific directories.

**Learning**:
- **List pages directory pattern**: `{resource}s/{resource}_page.py` for the list page
  - `taskruns/task_runs_page.py` - TaskRuns list page
  - `pipelineruns/pipeline_runs_page.py` - PipelineRuns list page
  - `tasks/tasks_page.py` - Tasks list page
  - `pipelines/pipelines_page.py` - Pipelines list page
- **Detail pages directory pattern**: `{resource}s/{resource}_details_page.py`
  - `taskruns/taskrun_details_page.py`
  - `pipelineruns/pipelinerun_details_page.py`
- **Tab pages**: Same as list pages (they ARE list pages, just on a tab)

**Structure Verification**:
1. Check existing structure for the reference resource (e.g., TaskRuns)
2. Create parallel structure for the new resource (e.g., PipelineRuns)
3. Update imports in `page_containers.py` to use correct path
4. Remove old file if it exists in wrong location

---

### Issue 9: Missing Logger Initialization

**Generated Code (Wrong):**
```python
# framework/ui_components/pipelineruns/pipeline_runs_page.py
from playwright.async_api import Page


class PipelineRunsPage(PipelinesBasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = PipelineRunsPageLocators()
        # ❌ No logger initialization

    async def get_pipelinerun_status(self, pipelinerun_name: str) -> str:
        try:
            # ...
            self.logger.warning(f"Status element not found")  # ❌ AttributeError
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")  # ❌ AttributeError
```

**Fixed Code:**
```python
import logging  # ✅ Add import
from playwright.async_api import Page


class PipelineRunsPage(PipelinesBasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = PipelineRunsPageLocators()
        self.logger = logging.getLogger(__name__)  # ✅ Initialize logger

    async def get_pipelinerun_status(self, pipelinerun_name: str) -> str:
        try:
            # ...
            self.logger.warning(f"Status element not found")  # ✅ Works
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")  # ✅ Works
```

**Root Cause**: Generator added logging calls but didn't initialize the logger in `__init__`.

**Learning**:
- **Logger pattern**: Any class that uses `self.logger.*` must initialize it in `__init__`:
  ```python
  import logging  # At top of file

  def __init__(self, page: Page, config: Config) -> None:
      super().__init__(page, config)
      self.locators = {ClassName}Locators()
      self.logger = logging.getLogger(__name__)  # Add this
  ```
- **When to add logger**:
  - Class has error handling with `try/except`
  - Class logs info/warnings (status checks, debugging)
  - Class inherits from BasePage but adds logging
- **BasePage doesn't have logger**: Don't assume it's inherited - must add explicitly

**Detection**:
```bash
# Find classes using self.logger without initialization
grep -l "self\.logger\." framework/ui_components/**/*.py | \
  xargs grep -L "self\.logger = logging\.getLogger"
```

---

### Issue 10: Project Selector Flakiness

**Original Code:**
```python
# framework/ui_components/commons/project_selector.py
async def select_project(self, project_name: str) -> bool:
    await self.click_project_selector()
    await self.page.wait_for_timeout(1000)
    project_locator = self.locators.PROJECT_MENU_ITEM.format(project_name=project_name)
    await self.click_element(project_locator)
    await self.page.wait_for_timeout(1000)
    return True
```

**Enhanced Code:**
```python
async def select_project(self, project_name: str, max_retries: int = 3) -> bool:
    for attempt in range(1, max_retries + 1):
        try:
            # Click selector
            click_success = await self.click_project_selector()
            if not click_success:
                await self.page.wait_for_timeout(1000 * attempt)
                continue

            # Wait for dropdown menu to appear
            await self.page.wait_for_selector("role=menu", state="visible", timeout=5000)

            # Wait for specific project item to be visible
            project_locator = self.locators.PROJECT_MENU_ITEM.format(project_name=project_name)
            await self.page.wait_for_selector(project_locator, state="visible", timeout=5000)

            # Click project item
            click_item_success = await self.click_element(project_locator)
            if not click_item_success:
                continue

            # Verify switch succeeded
            await self.page.wait_for_timeout(2000)
            current_project = await self.get_current_project()
            if current_project == project_name:
                return True
        except Exception as e:
            self.logger.error(f"Attempt {attempt}: {e}")
            await self.page.wait_for_timeout(1000 * attempt)

    return False
```

**Learning**:
- **Critical navigation needs retry logic**: Project selector, login, other critical paths
- **Retry pattern elements**:
  - Max retries: 3
  - Exponential backoff: `wait = 1000 * attempt` (1s, 2s, 3s)
  - Explicit waits: Wait for dropdown, wait for item visibility
  - Verification: Confirm operation succeeded
  - Logging: Log each attempt and errors
- **Defensive checks**:
  - Check return values of each operation
  - Wait for UI state before next action
  - Verify final state matches expectation

**When to Apply**:
- Navigation to main pages (project selector)
- Authentication flows
- Operations known to be flaky
- Cross-cutting concerns used in Background steps

---

### Issue 11: Skip Tour Button Errors

**Original Code:**
```python
# framework/ui_components/overview_page.py
async def verify_on_page(self) -> bool:
    overview_page_status = await self._verify_page(...)

    if not _tour_skipped:
        if await self.is_visible(self.locators.SKIP_TOUR_BUTTON, timeout=5000):
            await self.click_element(self.locators.SKIP_TOUR_BUTTON)  # ❌ Can fail
        _tour_skipped = True

    return overview_page_status
```

**Fixed Code:**
```python
async def verify_on_page(self) -> bool:
    overview_page_status = await self._verify_page(...)

    if not _tour_skipped:
        if await self.is_visible(self.locators.SKIP_TOUR_BUTTON, timeout=5000):
            try:
                await self.click_element(self.locators.SKIP_TOUR_BUTTON)  # ✅ Wrapped
            except Exception:
                pass  # Silently ignore - tour button is optional
        _tour_skipped = True

    return overview_page_status
```

**Learning**:
- **Optional UI elements need defensive handling**: Tour popups, cookie banners, promotional modals
- **Try-except pattern for optional elements**:
  ```python
  if await self.is_visible(OPTIONAL_ELEMENT, timeout=5000):
      try:
          await self.click_element(OPTIONAL_ELEMENT)
      except Exception:
          pass  # Silently ignore - element is optional
  ```
- **When to apply**:
  - Tour/onboarding popups
  - Cookie consent banners
  - "What's new" announcements
  - Non-critical UI decorations
- **Don't apply to**:
  - Required form elements
  - Navigation elements
  - Test-critical interactions

---

### Issue 12: CLI Login Executed Multiple Times

**Original Code:**
```python
# framework/fixtures/cli_fixtures.py
@pytest.fixture(scope="module")
async def test_project(openshift_cli: OpenShiftCLI, request) -> str:
    # Every module calls is_logged_in() - wasteful
    is_logged_in = await openshift_cli.is_logged_in()
    if not is_logged_in:
        # Login logic...
```

**Fixed Code:**
```python
# Module-level flag
_cli_logged_in = False

@pytest.fixture(scope="module")
async def test_project(openshift_cli: OpenShiftCLI, request) -> str:
    global _cli_logged_in

    if not _cli_logged_in:
        # Check and login only once
        is_logged_in = await openshift_cli.is_logged_in()
        if not is_logged_in:
            # Login logic...
        _cli_logged_in = True
        logger.info("CLI login confirmed - subsequent modules will skip")
    else:
        logger.info("CLI already logged in - skipping check")
```

**Learning**:
- **One-time operations need session-level flags**: Login, tour skip, initial setup
- **Flag pattern**:
  ```python
  # Module level (outside fixtures/classes)
  _operation_completed = False

  # In fixture/method
  global _operation_completed
  if not _operation_completed:
      # Perform operation
      _operation_completed = True
  else:
      # Skip operation
  ```
- **Use cases**:
  - CLI login (once per session)
  - Tour dismissal (once per session)
  - Initial browser setup
  - Resource cleanup flags
- **Thread safety**: Not thread-safe currently - see `overview_page.py` TODO for threading.Lock() pattern when parallel execution is added

---

## Summary: Key Patterns to Incorporate

### 1. Navigation Pattern Detection

**What to Check**:
- Is the target a tab (PipelineRuns tab) or standalone page (Pipelines page)?
- Does an existing navigation step handle this?

**Pattern**:
```python
# Detect tab vs page
if resource_name.endswith("Runs") and has_parent_resource:
    # It's a tab
    background_nav = f"the user navigates to the {parent_resource} page"
    scenario_nav = f"the user navigates to {resource_name} tab"
else:
    # It's a standalone page
    background_nav = f"the user navigates to the {resource_name} page"
```

### 2. Fixture Hierarchy

**Pattern**:
```python
# ✅ Correct fixture access patterns
page["pipelines"].list.*        # Pipelines list page
page["pipelines"].runs.*        # PipelineRuns tab
page["pipelines"].pipeline.*    # Pipeline details
page["pipelines"].pipelinerun.* # PipelineRun details

# ❌ Never use
page["pipelines"].base.*        # Invalid - base is class, not fixture
```

### 3. Check for Combo Methods

**Pattern**:
```python
# Before generating:
await page[resource].list.click_create_button()
await page[resource].list.click_create_{resource}_menu_item()

# Check if combo method exists:
await page[resource].list.click_create_{resource}()  # Preferred
```

### 4. Mirror Existing Patterns

**Checklist**:
- [ ] TaskRuns → PipelineRuns: Same structure
- [ ] Directory: `{resource}s/{resource}_page.py`
- [ ] Method signatures match
- [ ] Implementation patterns match (status polling, locators, logging)

### 5. Async Resource Status Verification

**Template**:
```python
max_wait_seconds = 60
retry_interval_seconds = 20
max_attempts = (max_wait_seconds // retry_interval_seconds) + 1

for attempt in range(1, max_attempts + 1):
    await page[resource].runs.verify_{resource}_runs_tab_data_load()
    actual_status = await page[resource].runs.get_{resource}_status(name)
    logger.info(f"Attempt {attempt}/{max_attempts}: status='{actual_status}'")

    if actual_status.lower() == expected_status.lower():
        return

    if attempt < max_attempts:
        await asyncio.sleep(retry_interval_seconds)

assert False, f"Timeout: status='{actual_status}', expected='{expected_status}'"
```

### 6. Logger Initialization

**Pattern**:
```python
import logging  # Top of file


class MyPage(BasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = MyPageLocators()
        self.logger = logging.getLogger(__name__)  # Add if using self.logger.*
```

### 7. Retry Logic for Critical Operations

**Pattern**:
```python
async def critical_operation(self, max_retries: int = 3) -> bool:
    for attempt in range(1, max_retries + 1):
        try:
            # Attempt operation
            success = await self.do_operation()
            if success:
                return True

            # Exponential backoff
            await self.page.wait_for_timeout(1000 * attempt)
        except Exception as e:
            self.logger.error(f"Attempt {attempt}: {e}")
            await self.page.wait_for_timeout(1000 * attempt)

    return False
```

### 8. Optional UI Element Handling

**Pattern**:
```python
if await self.is_visible(OPTIONAL_ELEMENT, timeout=5000):
    try:
        await self.click_element(OPTIONAL_ELEMENT)
    except Exception:
        pass  # Silently ignore optional elements
```

---

## Generator Improvements Checklist

When generating BDD test code, ensure:

- [ ] **Navigation**: Detect tab vs page, use existing steps
- [ ] **Fixtures**: Correct hierarchy (`.list`, `.runs`, not `.base`)
- [ ] **Methods**: Check for combo methods before splitting actions
- [ ] **Structure**: Mirror existing patterns (TaskRuns → PipelineRuns)
- [ ] **Status**: Implement polling/retry for async resources
- [ ] **Logger**: Initialize in `__init__` if using logging
- [ ] **Retry**: Add retry logic to critical operations
- [ ] **Optional UI**: Wrap optional elements in try-except
- [ ] **Flags**: Use session-level flags for one-time operations
- [ ] **Monaco**: Use `.monaco_editor.set_content()`, verify before submit
- [ ] **Directory**: Place files in correct locations (pipelineruns/, not pipelines/)
- [ ] **Imports**: Add all necessary imports (logging, asyncio, etc.)

---

**Version**: 1.0
**Date**: 2026-05-05
**Status**: Production learnings incorporated
