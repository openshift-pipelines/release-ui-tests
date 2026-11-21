# Navigation Guide

Detailed explanation of the navigation pattern for Tekton resources in OpenShift Console.

---

## Overview

For CRUD operations on Tekton resources (Tasks, Pipelines, PipelineRuns, Triggers), the Background section of generated feature files **must include TWO explicit navigation steps** after login.

---

## The Navigation Pattern

```gherkin
Background:
  Given the user is logged into openshift console
  When the user expands Pipelines in left navigation bar    # Step 1: Smart expand
  When the user navigates to the Tasks page                 # Step 2: Navigate to page
```

---

## Why Two Steps?

### How Left Navigation Works

The OpenShift Console left navigation has a **Pipelines** button that acts as a **toggle**:

1. **Click Pipelines button** → Expands submenu, shows links:
   - Tasks
   - Pipelines
   - Triggers
   - Overview

2. **Click Pipelines button again** → Collapses submenu, hides the links

**Key point**: The links (Tasks, Pipelines, etc.) are **only visible when the Pipelines button is expanded**.

---

## Step 1: Expand Pipelines Menu

**Step definition**:
```gherkin
When the user expands Pipelines in left navigation bar
```

**What it does**:
- Checks if Tasks link is visible (menu already expanded)
- If **not visible**: clicks Pipelines button to expand, waits 500ms for animation
- If **already visible**: does nothing (idempotent)
- **Result**: Menu guaranteed to be expanded after this step

**Implementation**:
```python
async def expand_pipelines_menu(page):
    is_expanded = await page["nav"].verify_link_available_under_pipelines_button("Tasks")
    if not is_expanded:
        await page["nav"].click_pipelines_button()
        await page["raw_page"].wait_for_timeout(500)
```

**Why it's "smart"**: It's **idempotent** - safe to call multiple times. Won't toggle if already expanded.

---

## Step 2: Navigate to Specific Page

**Step definition**:
```gherkin
When the user navigates to the Tasks page
```

**What it does**:
- Clicks the **Tasks** link under the expanded Pipelines submenu
- Waits for Tasks page to load
- Verifies page loaded successfully
- Verifies data loaded (for list pages)

**Implementation**:
```python
async def navigate_to_tasks_page(page):
    await page["nav"].click_tasks_link()
    await page["raw_page"].wait_for_load_state("networkidle")
    data_loaded = await page["tasks"].list.verify_data_load()
    assert data_loaded, "Tasks list failed to load"
```

---

## Available Navigation Steps

### Step 1 Options (Smart expand/collapse)

1. **`When the user expands Pipelines in left navigation bar`**
   - **Smart**: Checks if already expanded (Tasks link visible), only clicks button if collapsed
   - **Idempotent**: Safe to call multiple times
   - **Result**: Menu guaranteed to be expanded

2. **`When the user shrinks Pipelines in left navigation bar`**
   - **Smart**: Checks if expanded, only clicks button if expanded
   - **Idempotent**: Safe to call multiple times
   - **Result**: Menu guaranteed to be collapsed

3. **`When the user clicks on Pipelines button`**
   - **Dumb toggle**: Always clicks, toggles state (expand ↔ collapse)
   - **Use case**: Only when you want to explicitly toggle

**Recommendation**: Use **expand** in Background (Step 1), not the dumb toggle.

---

### Step 2 Options (Navigate to page)

For each Tekton resource type:

| Resource Type | Step Definition |
|---------------|-----------------|
| **Tasks** | `When the user navigates to the Tasks page` |
| **Pipelines** | `When the user navigates to the Pipelines page` |
| **PipelineRuns** | `When the user navigates to the Pipelines page` (then switch to PipelineRuns tab) |
| **Triggers** | `When the user navigates to the Triggers page` |
| **Overview** | `When the user navigates to the Overview page` |

---

## Browser Session Sharing (CRITICAL)

**Important**: Browser sessions are **shared between scenarios** in the same feature file.

**Problem**: After Scenario 1 completes, we **don't know which page the browser is on**:
- Could be on Task details page
- Could be on YAML editor
- Could be on list page
- Could be on any other page

**Solution**: **ALL CRUD action steps MUST navigate to list page first** to ensure consistent starting state.

---

## CRUD Action Steps Pattern

Each CRUD action step (create/edit/delete) **ALWAYS** navigates to the appropriate list page at the start:

| Action Type | Must Navigate To | Navigation Steps |
|-------------|------------------|------------------|
| Create Task | Tasks list page | Expand Pipelines → Click Tasks link |
| Edit Task | Tasks list page | Expand Pipelines → Click Tasks link |
| Delete Task | Tasks list page | Expand Pipelines → Click Tasks link |
| Create Pipeline | Pipelines list page | Expand Pipelines → Click Pipelines link |
| Create PipelineRun | Pipelines list page | Expand Pipelines → Click Pipelines link |
| Create Trigger | Triggers list page | Expand Pipelines → Click Triggers link |

---

## Example: Create Task Step Implementation

```python
@when(parsers.parse('the user creates a task from YAML file "{yaml_file}"'))
def create_task_from_yaml(page, yaml_file, playwright_event_loop, config):
    """
    Create a task by loading YAML from test data and submitting via UI.

    Always navigates to Tasks list page first to ensure consistent starting state.
    """

    async def _step():
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

        # NOW perform create action
        yaml_content = YamlLoader.load_task_yaml(yaml_file)
        await page["tasks"].list.click_create_button()
        # ... rest of create logic ...

    run_async(playwright_event_loop, _step())
```

**Why navigate first?**
- Previous scenario may have left browser on **any page** (details, YAML editor, etc.)
- Background navigation runs **once per scenario** (not between steps within a scenario)
- Steps must be **self-contained** and not depend on prior step state

---

## Feature File Structure Example

### Complete Example

```gherkin
Feature: Task CRUD Operations

  Background:
    Given the user is logged into openshift console
    When the user expands Pipelines in left navigation bar    # ← Step 1: Smart expand
    When the user navigates to the Tasks page                 # ← Step 2: Click Tasks link

  @smoke @sanity
  Scenario Outline: Create tasks from various YAML definitions
    When the user creates a task from YAML file "<yaml_file>"
    Then the task "<task_name>" should appear in the task list

    Examples:
      | yaml_file            | task_name        |
      | simple_task.yaml     | simple-task      |
      | multi_step_task.yaml | multi-step-task  |

  @smoke @sanity
  Scenario Outline: Edit task YAML and verify changes
    When the user edits the task "<task_name>" with YAML file "<updated_yaml_file>"
    Then the task "<task_name>" should have updated YAML content

    Examples:
      | task_name            | updated_yaml_file              |
      | simple-task          | simple_task_updated.yaml       |
      | multi-step-task      | multi_step_task_updated.yaml   |
```

**Note**:
- Background runs **once before each scenario**
- Browser is guaranteed to be on Tasks list page at start of each scenario
- But within a scenario, if step 1 navigates elsewhere, step 2 must handle navigation

---

## For Non-CRUD Features

If your feature does NOT involve CRUD operations (create/edit/delete), only the **login step** in Background is sufficient:

```gherkin
Feature: View Task Details

  Background:
    Given the user is logged into openshift console

  Scenario: View task details page
    When the user navigates to task "example-task" details page
    Then the task details should be displayed
```

**Why?** View-only operations can navigate directly to the target page without needing to go through list page first.

---

## Summary

1. **For CRUD features**: Background includes TWO navigation steps (expand + navigate)
2. **Pipelines button is a toggle**: Click to expand/collapse submenu
3. **Links only visible when expanded**: Tasks, Pipelines, Triggers, Overview
4. **Browser sessions are shared**: Previous scenario may have left browser on any page
5. **CRUD action steps ALWAYS navigate first**: Ensures consistent starting state
6. **Use "smart" expand step**: Idempotent, checks before clicking
7. **For non-CRUD features**: Only login step in Background is sufficient

---

**This pattern ensures robust, reliable tests that work regardless of browser state from previous scenarios.**
