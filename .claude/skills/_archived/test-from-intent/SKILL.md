# Test Generation from Plain English Intent

Generate complete BDD test scenarios, step definitions, and Page Object Model code from plain English descriptions of test workflows.

**Input**: Plain English test intent (e.g., "Create a task, validate it appears in the list")

**Output**:
- Feature file with Scenario Outline
- Step definitions (if missing)
- Page Object Model code (if missing)
- Test data YAML files
- Verification report

---

## Usage

```bash
# In Claude Code prompt:
/test-from-intent Create a task with YAML, verify it appears in task list

# Or with mode specification:
/test-from-intent NEW_FILE Create a pipeline with two tasks, start the pipeline

# Or append to existing feature:
/test-from-intent APPEND task_creation.feature: Delete a task and verify it's removed
```

---

## Input Modes

1. **`NEW_FILE`** (default) - Creates new feature file with single scenario outline
2. **`NEW_FILE_MULTI`** - Creates new feature file with multiple scenario outlines
3. **`APPEND`** - Adds scenario outline to existing feature file

**Format**:
```
[MODE] [feature_file:] <plain_english_intent>
```

**Examples**:
```
NEW_FILE Create a task from YAML, verify creation
NEW_FILE_MULTI Create task | Edit task YAML | Delete task
APPEND task_management.feature: Verify task list is empty after deletion
```

---

## Architecture

This skill operates in **TWO PHASES** with a **MANDATORY APPROVAL GATE** between them:

### Phase 1: Analysis & Planning

1. **Parse Intent** → Identify user goal and workflow type
2. **Query NotebookLM** → Get Tekton/OpenShift knowledge for context
3. **Map to UI Workflow** → Break down into UI navigation steps
4. **Check Existing Coverage**:
   - Do step definitions exist?
   - Does POM support this workflow?
   - Do required locators exist?
5. **Plan Generation**:
   - What steps to create?
   - What POM methods to add?
   - What test data to generate?
6. **Present Analysis Report** → Present comprehensive plan and STOP

**🛑 MANDATORY APPROVAL GATE**: Wait for user to reply "yes" before proceeding to Phase 2

### Phase 2: Code Generation (ONLY after user approval)

7. **Generate Test Data** → Create realistic YAML files
8. **Generate/Update POM** → Add missing page methods and locators
9. **Generate Step Definitions** → Create parametrized steps
10. **Generate Feature File** → Create Scenario Outline with Examples table
11. **Verification** → Compile check and report
12. **Test Execution** → Run generated tests and validate
13. **Final Report** → Summary of all changes and test results

---

## Prerequisites

- ✅ NotebookLM MCP server configured (with Tekton documentation)
- ✅ Playwright MCP server active (for UI navigation learning)
- ✅ OpenShift Console accessible (URLs in workflow database)
- ✅ Existing POM framework in `framework/ui_components/`
- ✅ Test data directory in `framework/resources/test_data/`
- ✅ Navigation steps available in `tests/steps/test_navigation_steps.py`

---

## Navigation Pattern (CRITICAL)

**Two-Step Navigation After Login**:

For CRUD operations on Tekton resources, Background must include **TWO explicit navigation steps** AFTER login:

**Step 1**: Expand Pipelines menu (smart - only expands if not already expanded)
**Step 2**: Navigate to specific page (clicks the link under Pipelines)

| Resource Type | Background Steps |
|---------------|------------------|
| **Tasks** | 1. `When the user expands Pipelines in left navigation bar`<br>2. `When the user navigates to the Tasks page` |
| **Pipelines** | 1. `When the user expands Pipelines in left navigation bar`<br>2. `When the user navigates to the Pipelines page` |
| **PipelineRuns** | 1. `When the user expands Pipelines in left navigation bar`<br>2. `When the user navigates to the Pipelines page` |
| **Triggers** | 1. `When the user expands Pipelines in left navigation bar`<br>2. `When the user navigates to the Triggers page` |
| **Overview** | 1. `When the user expands Pipelines in left navigation bar`<br>2. `When the user navigates to the Overview page` |

**How Left Navigation Works**:
- Pipelines button in left nav bar is a **toggle**
- Click Pipelines button → expands submenu, shows: Tasks, Pipelines, Triggers, Overview links
- Click Pipelines button again → collapses submenu, hides the links
- Links are only visible when Pipelines button is expanded

**Navigation Steps Available**:
1. `When the user expands Pipelines in left navigation bar` - **Smart**: Checks if already expanded (Tasks link visible), only clicks button if collapsed. Idempotent - safe to call multiple times.
2. `When the user shrinks Pipelines in left navigation bar` - **Smart**: Checks if expanded, only clicks button if expanded. Idempotent.
3. `When the user clicks on Pipelines button` - **Dumb toggle**: Always clicks, toggles state. Use only when you want to explicitly toggle.

**What Step 1 does** (`When the user expands Pipelines in left navigation bar`):
- Checks if Tasks link is visible (menu already expanded)
- If not visible: clicks Pipelines button to expand, waits 500ms for animation
- If already visible: does nothing (idempotent)
- Result: Menu guaranteed to be expanded after this step

**What Step 2 does** (e.g., `When the user navigates to the Tasks page`):
- Clicks Tasks link under the expanded Pipelines submenu
- Waits for Tasks page to load
- Verifies page loaded successfully
- Verifies data loaded (for list pages)

**Example Feature File Structure**:
```gherkin
Feature: Task CRUD Operations

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar    # ← Step 1: Smart expand
    When the user navigates to the Tasks page                 # ← Step 2: Click Tasks link

  Scenario Outline: Create tasks...
    When the user creates a task from YAML file "<yaml_file>"
    ...
```

**Note**: CRUD action steps internally also expand Pipelines before navigating (handles browser session sharing between scenarios).

**CRITICAL - Browser Session Sharing**:
Browser sessions are **shared between scenarios** in the same feature file. After a scenario completes, we don't know which page the browser is on. Therefore:

**ALL CRUD Action Steps MUST Navigate to List Page First**:

Each CRUD action step (create/edit/delete) must **ALWAYS** navigate to the appropriate list page at the start to ensure consistent state:

| Action Type | Must Navigate To | Navigation Steps |
|-------------|------------------|------------------|
| Create Task | Tasks list page | Click Pipelines button → Click Tasks link |
| Edit Task | Tasks list page | Click Pipelines button → Click Tasks link |
| Delete Task | Tasks list page | Click Pipelines button → Click Tasks link |
| Create Pipeline | Pipelines list page | Click Pipelines button → Click Pipelines link |
| Create PipelineRun | Pipelines list page | Click Pipelines button → Click Pipelines link |
| Create Trigger | Triggers list page | Click Pipelines button → Click Triggers link |

**Why?**
- Previous scenario may have left browser on details page, YAML editor, or any other page
- Background navigation runs once per scenario (not between steps within a scenario)
- Steps must be self-contained and not depend on prior step state

**Example** - Create Task Step Pattern:
```python
async def _step() -> None:
    # ALWAYS navigate to Tasks list page first
    await page["nav"].click_pipelines_button()
    await page["raw_page"].wait_for_timeout(300)
    await page["nav"].click_tasks_link()

    # Wait for data to load
    data_loaded = await page["tasks"].list.verify_data_load()
    assert data_loaded, "Tasks list failed to load"

    # Now perform create action
    # ... load YAML, click Create, etc. ...
```

**For non-CRUD features**: Only login step in Background is sufficient.

---

## Skill Implementation

This is a **master orchestration skill** that uses specialized sub-skills:

- **intent-parser** - Parse plain English into structured workflow
- **workflow-mapper** - Map intent to UI navigation steps
- **coverage-checker** - Analyze existing POM/step coverage
- **test-data-generator** - Generate realistic Tekton YAML files
- **pom-generator** - Create/update Page Object Model code
- **step-generator** - Create BDD step definitions
- **feature-generator** - Create Gherkin feature files

Each sub-skill is invoked sequentially with context passing.

---

## Phase 1: Analysis & Planning

### Step 1: Parse Intent

**Goal**: Convert plain English to structured workflow description.

**Actions**:
1. Parse mode from input (NEW_FILE, NEW_FILE_MULTI, APPEND)
2. Extract core actions (create, edit, delete, verify, navigate, etc.)
3. Identify resources (Task, Pipeline, PipelineRun, etc.)
4. Identify verification points (appears in list, YAML is correct, status is Running, etc.)

**Output**:
```yaml
mode: NEW_FILE
resource_type: Task
actions:
  - action: create
    method: yaml
    verification: appears_in_list
  - action: verify
    check: task_visible
    location: tasks_list_page
```

### Step 2: Query NotebookLM for Context

**Goal**: Get Tekton/OpenShift domain knowledge.

**Actions**:
1. Call `mcp__notebooklm-mcp__notebook_query` with notebook ID: `ce34f1af-5b8d-47c0-ad62-b21ae6734d95`
2. Query for:
   - Resource YAML structure (if creating resources)
   - Required fields and common parameters
   - Validation rules
   - Best practices

**Example queries**:
```
"What are the required fields for a Tekton Task YAML definition?"
"What parameters can a Tekton Pipeline accept?"
"How do you reference a Task in a Pipeline spec?"
```

**Output**: Domain knowledge context for test data generation.

### Step 3: Map to UI Workflow Steps

**Goal**: Translate intent into specific UI navigation sequence.

**Knowledge Base**: Use `framework/resources/ui_workflows.yaml` (generated from URL analysis)

**Actions**:
1. Read UI workflows database
2. Match intent to known workflows
3. Break down into atomic UI steps

**Example**:
```
Intent: "Create a task with YAML"

UI Steps:
1. Login (if not already logged in)
2. Navigate to Tasks list page
3. Click Create button
4. Select "Task" from dropdown (not TaskRun)
5. Wait for YAML editor to load
6. Clear existing YAML
7. Insert test data YAML
8. Click Create button
9. Wait for redirect to Task details page
10. Verify task name matches expected
```

**Output**:
```yaml
workflow_steps:
  - page: login
    action: ensure_logged_in
    step_exists: true
    step_name: user_logged_into_openshift_kube_admin

  - page: tasks.list
    action: navigate_to_page
    method: goto
    step_exists: true
    step_name: user_navigates_to_tasks

  - page: tasks.list
    action: click_create_button
    method: click_create_button
    step_exists: false  # NEEDS CREATION
    pom_method_exists: false  # NEEDS CREATION

  - page: tasks.create
    action: fill_yaml
    method: fill_yaml_editor
    step_exists: false
    pom_method_exists: true  # EXISTS in CreateTaskPage

  - page: tasks.create
    action: click_create
    method: click_create
    step_exists: false
    pom_method_exists: true

  - page: tasks.task.details
    action: verify_task_name
    method: get_task_name
    step_exists: false
    pom_method_exists: true
```

### Step 4: Check Existing Coverage

**Goal**: Determine what code already exists vs. needs to be generated.

**Actions**:

**4a. Check Step Definitions**:
```python
# Search in tests/steps/*.py
grep -r "def create_task" tests/steps/
grep -r "@when.*creates a task" tests/steps/
```

**4b. Check POM Methods**:
```python
# Check if page object exists
framework/ui_components/tasks/create_task_page.py

# Check if methods exist
grep "def fill_yaml_editor" framework/ui_components/**/*.py
grep "def click_create_button" framework/ui_components/**/*.py
```

**4c. Check Locators**:
```python
# Check if locators exist
grep "CREATE_BUTTON" framework/locators/tasks.py
grep "YAML_EDITOR" framework/locators/tasks.py
```

**Output**:
```yaml
coverage_analysis:
  steps:
    - name: user_logged_into_openshift_kube_admin
      exists: true
      file: tests/steps/test_auth_steps.py

    - name: user_navigates_to_tasks
      exists: true
      file: tests/steps/test_navigation_steps.py

    - name: user_creates_task_from_yaml
      exists: false
      needs_creation: true

    - name: task_appears_in_list
      exists: false
      needs_creation: true

  pom_methods:
    - page: tasks.list
      method: click_create_button
      exists: false
      needs_locator: CREATE_BUTTON

    - page: tasks.create
      method: fill_yaml_editor
      exists: true  # Already exists

    - page: tasks.list
      method: verify_task_in_list
      exists: false
      needs_locator: TASK_ROW_BY_NAME

  test_data:
    - file: simple_task.yaml
      exists: true  # Already created

    - file: task_with_params.yaml
      exists: false
      needs_creation: true
```

### Step 5: Plan Generation

**Goal**: Create detailed generation plan.

**Output**:
```yaml
generation_plan:
  test_data_files:
    - path: framework/resources/test_data/tasks/simple_task.yaml
      status: exists
      action: reuse

    - path: framework/resources/test_data/tasks/multi_step_task.yaml
      status: missing
      action: generate
      content_from_notebooklm: true

  locators:
    - file: framework/locators/tasks.py
      locators_to_add:
        - CREATE_BUTTON: 'button:has-text("Create")'
        - TASK_ROW_BY_NAME: 'tr:has-text("{task_name}")'

  pom_methods:
    - file: framework/ui_components/tasks/tasks_page.py
      methods_to_add:
        - name: click_create_button
          returns: bool
          locator: TasksPageLocators.CREATE_BUTTON

        - name: verify_task_in_list
          params: [task_name: str]
          returns: bool
          locator: TasksPageLocators.TASK_ROW_BY_NAME (formatted)

  step_definitions:
    - file: tests/steps/test_task_creation_steps.py
      status: new_file
      steps_to_add:
        - pattern: 'the user creates a task from YAML file "{yaml_file}"'
          function_name: create_task_from_yaml
          params: [page, yaml_file, playwright_event_loop]

        - pattern: 'the task "{task_name}" should appear in the task list'
          function_name: verify_task_in_list
          params: [page, task_name, playwright_event_loop]

  feature_file:
    - path: tests/features/task_creation.feature
      status: new_file
      scenarios:
        - name: Create tasks from various YAML definitions
          type: scenario_outline
          examples_table:
            - yaml_file: simple_task.yaml
              task_name: simple-task
            - yaml_file: multi_step_task.yaml
              task_name: multi-step-task
```

### Step 6: Present Analysis Report

**CRITICAL**: Present the complete analysis report and STOP. Wait for explicit user approval before proceeding to Phase 2.

**Format**:

````markdown
## Test Generation Analysis Report

### Intent Parsed
**Mode**: NEW_FILE
**Resource**: Task
**Actions**: Create via YAML → Verify in list

### NotebookLM Context Retrieved
- ✅ Tekton Task YAML structure documented
- ✅ Required fields: apiVersion, kind, metadata.name, spec.steps
- ✅ Common parameters: image, script, args

### UI Workflow Mapped
**Workflow**: Create Task via YAML

**Steps** (10 total):
1. ✅ Login (existing step: `user_logged_into_openshift_kube_admin`)
2. ✅ Navigate to Tasks (existing step: `user_navigates_to_tasks`)
3. ❌ Click Create button (NEW - needs POM method + step)
4. ✅ Fill YAML editor (existing POM method: `fill_yaml_editor`)
5. ✅ Click Create (existing POM method: `click_create`)
6. ❌ Verify task in list (NEW - needs POM method + step)

### Existing Coverage
**Step Definitions**: 2/4 exist (50%)
**POM Methods**: 2/3 exist (67%)
**Test Data**: 1/2 exist (50%)

### Code Generation Plan

#### Test Data Files to Generate (1)
- `framework/resources/test_data/tasks/multi_step_task.yaml`
  - 3 steps (setup, execute, cleanup)
  - Uses parameter substitution
  - Based on NotebookLM examples

#### Locators to Add (2)
**File**: `framework/locators/tasks.py`
```python
# In TasksPageLocators class
CREATE_BUTTON = 'button:has-text("Create")'
TASK_ROW_BY_NAME = 'tr[data-test="task-row"]:has-text("{task_name}")'
```

#### POM Methods to Add (2)
**File**: `framework/ui_components/tasks/tasks_page.py`
```python
async def click_create_button(self) -> bool:
    """Click the Create button in tasks list page."""
    return await self.click_element(self.locators.CREATE_BUTTON)

async def verify_task_in_list(self, task_name: str) -> bool:
    """Verify task appears in the task list."""
    locator = self.locators.TASK_ROW_BY_NAME.format(task_name=task_name)
    return await self.is_visible(locator)
```

#### Step Definitions to Create (2)
**File**: `tests/steps/test_task_creation_steps.py` (NEW FILE)
```python
@when(parsers.parse('the user creates a task from YAML file "{yaml_file}"'))
def create_task_from_yaml(
    page: Dict[str, Any],
    yaml_file: str,
    playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    # Load YAML from test_data, navigate, fill, create

@then(parsers.parse('the task "{task_name}" should appear in the task list'))
def verify_task_in_list(
    page: Dict[str, Any],
    task_name: str,
    playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    # Verify task row is visible
```

#### Feature File to Create
**File**: `tests/features/task_creation.feature`
```gherkin
Feature: Task Creation and Verification

  Background:
    Given the user is logged into openshift console with auth kube:admin

  Scenario Outline: Create tasks from various YAML definitions
    When the user navigates to the Tasks page
    And the user creates a task from YAML file "<yaml_file>"
    Then the task "<task_name>" should appear in the task list

    Examples:
      | yaml_file           | task_name       |
      | simple_task.yaml    | simple-task     |
      | multi_step_task.yaml| multi-step-task |
```

### Files to Create/Modify

| Action | File | Lines |
|--------|------|-------|
| CREATE | framework/resources/test_data/tasks/multi_step_task.yaml | ~25 |
| MODIFY | framework/locators/tasks.py | +2 locators |
| MODIFY | framework/ui_components/tasks/tasks_page.py | +2 methods (~15 lines) |
| CREATE | tests/steps/test_task_creation_steps.py | ~45 lines |
| CREATE | tests/features/task_creation.feature | ~15 lines |

**Total**: 2 new files, 2 modified files, ~100 lines of code

---

## 🛑 APPROVAL REQUIRED

**Do you approve this plan?**

- Reply **"yes"** to proceed with code generation in Phase 2
- Reply **"no"** or describe what you'd like changed

````

---

### *** MANDATORY STOP — WAIT FOR USER APPROVAL ***

**CRITICAL INSTRUCTIONS**:
- Do NOT proceed to Phase 2 (Code Generation) until the user explicitly approves
- If the user says "yes", proceed with Steps 7-13 (Code Generation)
- If the user says "no" or requests changes, update the analysis and re-present the report
- If the user provides feedback, incorporate it and re-present the modified plan for approval

---

## Phase 2: Code Generation (ONLY after user approval)

**IMPORTANT**: This phase must ONLY be executed after the user has explicitly approved the plan in Phase 1 by replying "yes".

If the user has not approved yet, DO NOT proceed with any of the steps below.

---

### Step 7: Generate Test Data

**For each test data file in plan**:

1. **Query NotebookLM** for realistic examples:
   ```
   "Show me an example of a Tekton Task YAML with multiple steps and parameters"
   ```

2. **Generate YAML** following Tekton best practices:
   ```yaml
   apiVersion: tekton.dev/v1
   kind: Task
   metadata:
     name: multi-step-task
   spec:
     params:
       - name: message
         type: string
         default: "Hello"
     steps:
       - name: setup
         image: registry.redhat.io/ubi9/ubi-minimal
         script: |
           #!/bin/bash
           echo "Setting up..."

       - name: execute
         image: registry.redhat.io/ubi9/ubi-minimal
         script: |
           #!/bin/bash
           echo "Executing: $(params.message)"

       - name: cleanup
         image: registry.redhat.io/ubi9/ubi-minimal
         script: |
           #!/bin/bash
           echo "Cleaning up..."
   ```

3. **Write file** using `Write` tool

### Step 8: Generate/Update Locators

**Action**: Use `Edit` tool to append locators to appropriate file.

**Example**:
```python
# Append to framework/locators/tasks.py
class TasksPageLocators:
    # ... existing locators ...

    # Create button
    CREATE_BUTTON = 'button:has-text("Create")'

    # Task list verification
    TASK_ROW_BY_NAME = 'tr[data-test="task-row"]:has-text("{task_name}")'
```

### Step 9: Generate/Update POM Methods

**Action**: Use `Edit` tool to append methods to appropriate page class.

**Template**:
```python
async def {method_name}(self, {params}) -> bool:
    """
    {docstring}

    :param {type} {name}: {description}
    :return: bool: True if {action} successful
    """
    {implementation}
```

**Example**:
```python
async def click_create_button(self) -> bool:
    """
    Click the Create button to open resource creation dropdown.

    :return: bool: True if button clicked successfully
    """
    return await self.click_element(self.locators.CREATE_BUTTON)


async def verify_task_in_list(self, task_name: str) -> bool:
    """
    Verify that a task with the given name appears in the task list.

    :param str task_name: Name of the task to verify
    :return: bool: True if task row is visible
    """
    locator = self.locators.TASK_ROW_BY_NAME.format(task_name=task_name)
    return await self.is_visible(locator, timeout=5000)
```

### Step 10: Generate Step Definitions

**Action**: Create new step file or append to existing using `Write` or `Edit`.

**Template**:
```python
"""
{Resource} {Action} Test Steps.

BDD step definitions for {description}.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

from pytest_bdd import given, parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async


@when(parsers.parse('{step_pattern}'))
def {function_name}(
    page: Dict[str, Any],
    {parameters},
    playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    {docstring}

    :param Dict[str, Any] page: Page object dictionary
    :param {type} {name}: {description}
    :return: None: Raises AssertionError if {condition} fails
    """
    async def _step() -> None:
        {async_implementation}

    run_async(playwright_event_loop, _step())
```

**Example for task creation**:
```python
@when(parsers.parse('the user creates a task from YAML file "{yaml_file}"'))
def create_task_from_yaml(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop, config: object
) -> None:
    """
    Create a task by loading YAML from test data and submitting via UI.

    Always navigates to Tasks list page first to ensure consistent starting state
    (browser session is shared between scenarios, so we don't know which page we're on).

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/tasks/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if creation fails
    """

    async def _step() -> None:
        # ALWAYS navigate to Tasks list page first (session shared between scenarios)
        # Ensure Pipelines menu is expanded first (smart check)
        is_expanded = await page["nav"].verify_link_available_under_pipelines_button("Tasks")
        if not is_expanded:
            await page["nav"].click_pipelines_button()
            await page["raw_page"].wait_for_timeout(500)

        # Now navigate to Tasks
        await page["nav"].navigate_to_tasks()

        # Wait for tasks list to load
        data_loaded = await page["tasks"].list.verify_data_load()
        assert data_loaded, "Tasks list failed to load before creating task"

        # Load YAML content using helper (DRY principle)
        yaml_content = YamlLoader.load_task_yaml(yaml_file)

        # Click Create button
        create_clicked = await page["tasks"].list.click_create_button()
        assert create_clicked, "Failed to click Create button on Tasks list page"

        # Wait for dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Task" option (not "TaskRun")
        task_option_clicked = await page["tasks"].list.click_create_task_menu_item()
        assert task_option_clicked, "Failed to click 'Task' menu item from Create dropdown"

        # Wait for Create Task page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Fill YAML editor
        yaml_filled = await page["tasks"].create.fill_yaml_editor(yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{yaml_file}'"

        # Click Create button to submit
        create_submitted = await page["tasks"].create.click_create()
        assert create_submitted, "Failed to click Create button to submit task YAML"

        # Wait for redirect to details page
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

    run_async(playwright_event_loop, _step())
```

### Step 11: Generate Feature File

**Action**: Create new feature file using `Write`.

**Template**:
```gherkin
Feature: {Feature Title}

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smoke @sanity
  Scenario Outline: {Scenario Title}
    {Given/When/Then steps with <parameters>}

    Examples:
      | {column1} | {column2} | {column3} |
      | {value1}  | {value2}  | {value3}  |
```

**Example**:
```gherkin
Feature: Task Creation and Verification

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar    # Smart expand
    When the user navigates to the Tasks page                 # Click Tasks link

  @smoke @sanity
  Scenario Outline: Create tasks from various YAML definitions
    When the user creates a task from YAML file "<yaml_file>"
    Then the task "<task_name>" should appear in the tasks list

    Examples:
      | yaml_file            | task_name        |
      | simple_task.yaml     | simple-task      |
      | multi_step_task.yaml | multi-step-task  |
```

**Important Navigation Pattern**:
- Background includes TWO explicit navigation steps after login:
  1. "When the user clicks on Pipelines button" - expands submenu in left nav
  2. "When the user navigates to the [Resource] page" - clicks specific link under Pipelines
- Pipelines button is a toggle: click to expand/show links, click again to collapse/hide links
- Action steps (create/edit/delete) assume user is already on the correct page
- Pattern applies to: Tasks, Pipelines, PipelineRuns, Triggers, Overview pages

### Step 12: Verification & Report

**Actions**:

1. **Compile check all Python files**:
   ```bash
   python -m py_compile {generated_file}
   ```

2. **Verify test collection**:
   ```bash
   pytest --collect-only tests/features/{new_feature}.feature
   ```

3. **Generate report**:

````markdown
## Test Generation Complete ✅

### Files Created (2)
| File | Lines | Status |
|------|-------|--------|
| framework/resources/test_data/tasks/multi_step_task.yaml | 25 | ✅ Created |
| tests/steps/test_task_creation_steps.py | 48 | ✅ Created + Compiled |
| tests/features/task_creation.feature | 16 | ✅ Created |

### Files Modified (2)
| File | Changes | Status |
|------|---------|--------|
| framework/locators/tasks.py | +2 locators | ✅ Modified + Compiled |
| framework/ui_components/tasks/tasks_page.py | +2 methods (16 lines) | ✅ Modified + Compiled |

### Test Collection
```
$ pytest --collect-only tests/features/task_creation.feature
====== 2 tests collected ======
tests/steps/test_task_creation_steps.py::test_create_tasks_from_various_yaml_definitions[simple_task.yaml-simple-task]
tests/steps/test_task_creation_steps.py::test_create_tasks_from_various_yaml_definitions[multi_step_task.yaml-multi-step-task]
```

### Next Steps

**To run the generated tests**:
```bash
# Ensure environment is configured
cp .env.example .env
# Edit .env with your credentials

# Run the specific feature
pytest tests/features/task_creation.feature -v

# Or run with smoke marker
pytest -m smoke -v
```

**Test execution will**:
1. Create isolated project: `release-ui-test-{random}`
2. Run scenarios with test data
3. Verify task creation and visibility
4. Delete project if tests pass (keep if failed for debugging)

### Summary
- ✅ 105 lines of code generated
- ✅ All files compile successfully
- ✅ 2 test scenarios ready to run
- ✅ Integrated with existing POM and step definitions
- ✅ Follows project coding standards
````

---

### Step 13: Test Execution & Validation

**CRITICAL**: After generating all code, **ALWAYS run the tests** to verify they work correctly.

**Actions**:

1. **Run all scenarios in the generated/modified feature file**:
   ```bash
   pytest tests/steps/{step_file}.py -v --tb=short
   ```

2. **Check test results**:
   - If ALL scenarios PASS ✅ → Report success
   - If ANY scenario FAILS ❌ → Analyze failure, fix issues, re-run

3. **Common failure patterns & fixes**:

   **a) Locator not found**:
   ```
   Error: Element not found: button:has-text("Create")
   ```
   **Fix**: Update locator in `framework/locators/{resource}.py` with correct selector from page inspection

   **b) Navigation timing issue**:
   ```
   Error: TimeoutError waiting for selector
   ```
   **Fix**: Increase wait time or add explicit wait for element visibility

   **c) YAML validation error**:
   ```
   Error: YAML parsing failed
   ```
   **Fix**: Validate YAML syntax in test data file, ensure proper indentation

   **d) Test data not found**:
   ```
   Error: FileNotFoundError: simple_task.yaml
   ```
   **Fix**: Verify test data file exists in correct directory

4. **Update report with test execution results**:

````markdown
## Test Generation & Execution Complete ✅

### Files Generated
[... same as before ...]

### Test Execution Results

**Command**: `pytest tests/steps/test_task_crud_steps.py -v`

**Results**:
```
tests/steps/test_task_crud_steps.py::test_create_tasks_from_yaml_and_verify_in_list[simple_task.yaml-task-for-create] PASSED
tests/steps/test_task_crud_steps.py::test_view_task_details[task_for_edit.yaml-task-for-edit] PASSED
tests/steps/test_task_crud_steps.py::test_edit_task_yaml_and_verify_changes[task_for_edit.yaml-task-for-edit-task_for_edit_updated.yaml] PASSED
tests/steps/test_task_crud_steps.py::test_delete_task_and_verify_removal[task_for_delete.yaml-task-for-delete] PASSED

====== 4 passed in 45.23s ======
```

**Status**: ✅ ALL SCENARIOS PASSED

### Summary
- ✅ 105 lines of code generated
- ✅ All files compile successfully
- ✅ 4 test scenarios executed
- ✅ All scenarios PASSED ✅
- ✅ Tests verified on live OpenShift cluster
- ✅ Ready for production use
````

**If tests fail**, iterate:
1. Analyze failure output
2. Fix the issue (locator, logic, test data, etc.)
3. Re-run tests
4. Repeat until all scenarios pass

**Note**: Test execution requires:
- ✅ `.env` file configured with credentials
- ✅ OpenShift cluster accessible
- ✅ `oc` CLI installed and authenticated (for project isolation)

---

## Error Handling

### Missing POM Pages
**Error**: Required page object doesn't exist (e.g., `CreateTaskPage`)

**Action**:
1. Use `multi-page-pom` skill to generate missing page objects
2. Provide URL for the missing page
3. Regenerate step definitions after POM is created

### NotebookLM Query Failures
**Error**: NotebookLM authentication or query timeout

**Action**:
1. Run `nlm login` via Bash tool
2. Retry query
3. If still fails, use fallback templates from existing test data

### Invalid YAML Generation
**Error**: Generated test data YAML is invalid

**Action**:
1. Validate YAML syntax
2. Re-query NotebookLM with more specific question
3. Use stricter template with required fields only

---

## Examples

### Example 1: Simple Task Creation

**Input**:
```
/test-from-intent Create a task from YAML, verify it appears in the task list
```

**Generated**:
- `tests/features/task_creation.feature` (Scenario Outline with 2 examples)
- `tests/steps/test_task_creation_steps.py` (2 new steps)
- `framework/resources/test_data/tasks/multi_step_task.yaml` (if didn't exist)
- Updated `framework/locators/tasks.py` (if locators missing)
- Updated `framework/ui_components/tasks/tasks_page.py` (if methods missing)

### Example 2: Pipeline Workflow

**Input**:
```
/test-from-intent NEW_FILE_MULTI Create pipeline | Start pipeline | Verify PipelineRun is Running
```

**Generated**:
- `tests/features/pipeline_workflow.feature` (3 Scenario Outlines)
- `tests/steps/test_pipeline_workflow_steps.py`
- Test data for pipelines and pipelineruns
- Any missing POM methods

### Example 3: Append to Existing Feature

**Input**:
```
/test-from-intent APPEND task_management.feature: Delete a task and verify it's removed from the list
```

**Generated**:
- Appends new Scenario Outline to existing `tests/features/task_management.feature`
- Adds new step definition for delete verification
- Reuses existing steps where possible

---

## Configuration

### NotebookLM Notebook ID

Default: `ce34f1af-5b8d-47c0-ad62-b21ae6734d95` (Introducing Tekton)

To use a different notebook, edit this skill file and update the notebook ID.

### UI Workflows Database

Location: `framework/resources/ui_workflows.yaml`

This file maps UI actions to page navigation sequences. It's auto-generated from the workflow URLs you provided.

**Format**:
```yaml
workflows:
  create_task_yaml:
    name: Create Task via YAML
    pages:
      - url_pattern: /tasks/ns/{namespace}
        page_object: tasks.list
        actions:
          - click_create_button
          - select_task_option
      - url_pattern: /k8s/ns/{namespace}/tekton.dev~v1~Task/~new
        page_object: tasks.create
        actions:
          - fill_yaml_editor
          - click_create
    verification:
      - page: tasks.task.details
        method: get_task_name
        expected: matches_yaml_metadata_name
```

---

## Limitations

1. **UI-only workflows** - Does not generate tests for CLI-based operations (use CLI for test data setup)
2. **Modal/popup interactions** - May need manual refinement for complex modal workflows
3. **Dynamic waits** - Generated code uses standard waits; may need tuning for slow clusters
4. **Validation logic** - Generates basic visibility checks; complex validations need manual addition

---

## Troubleshooting

**Q: Skill says POM method exists but step generation fails**
A: The method signature might not match expected parameters. Check the method in POM and adjust step manually.

**Q: Test data YAML fails validation in cluster**
A: Query NotebookLM with more specific requirements or check Tekton version compatibility.

**Q: Generated test fails with timeout**
A: Increase `APP_TIMEOUT` in `.env` or add explicit waits in step definition.

**Q: Scenario Outline generates duplicate examples**
A: Check if test data files have unique names. Skill uses filename to derive task/pipeline names.

---

## Future Enhancements

- [ ] Support for Pipeline Builder (visual) in addition to YAML
- [ ] Generate negative test scenarios (invalid YAML, duplicate names, etc.)
- [ ] Auto-detect and reuse existing test data
- [ ] Generate data-driven tests with multiple parameter combinations
- [ ] Integration with test coverage reports

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2026-04-14
