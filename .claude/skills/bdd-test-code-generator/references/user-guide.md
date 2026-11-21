# User Guide

Examples, best practices, and tips for using the BDD Test Code Generator skill effectively.

---

## What Gets Generated

### From Plain English Intent

**Input**:
```
/bdd-test-code-generator Create a task with YAML, verify it appears in task list
```

### You Get ALL Of This:

**1. Feature File** (`tests/features/task_creation.feature`)
```gherkin
Feature: Task Creation and Verification

  Background:
    Given the user is logged into openshift console
    When the user expands Pipelines in left navigation bar    # Step 1: Smart expand
    When the user navigates to the Tasks page                 # Step 2: Click Tasks link

  @smoke @sanity
  Scenario Outline: Create tasks from various YAML definitions
    When the user creates a task from YAML file "<yaml_file>"
    Then the task "<task_name>" should appear in the task list

    Examples:
      | yaml_file            | task_name        |
      | simple_task.yaml     | simple-task      |
      | multi_step_task.yaml | multi-step-task  |
```

**2. Step Definitions** (`tests/steps/test_task_creation_steps.py`)
```python
@when(parsers.parse('the user creates a task from YAML file "{yaml_file}"'))
def create_task_from_yaml(page, yaml_file, playwright_event_loop, config):
    # Automatically generated with proper async handling
    # ALWAYS navigates to Tasks list page first (browser session shared)
    # Then loads YAML using YamlLoader helper and creates task
    pass


@then(parsers.parse('the task "{task_name}" should appear in the task list'))
def verify_task_in_list(page, task_name, playwright_event_loop):
    # Automatically generated verification
    pass
```

**3. Page Object Methods** (if missing)
```python
# In framework/ui_components/tasks/tasks_page.py
async def click_create_button(self) -> bool:
    """Click the Create button in tasks list page."""
    return await self.click_element(self.locators.CREATE_BUTTON)


async def verify_task_in_list(self, task_name: str) -> bool:
    """Verify task appears in the task list."""
    locator = self.locators.TASK_ROW_BY_NAME.format(task_name=task_name)
    return await self.is_visible(locator)
```

**4. Locators** (if missing)
```python
# In framework/locators/tasks.py
class TasksPageLocators:
    CREATE_BUTTON = 'button:has-text("Create")'
    TASK_ROW_BY_NAME = 'tr[data-test="task-row"]:has-text("{task_name}")'
```

**5. Test Data YAML**
```yaml
# framework/resources/test_data/tasks/multi_step_task.yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: multi-step-task
spec:
  # Generated from NotebookLM Tekton knowledge
  params: [...]
  steps: [...]
```

---

## Usage Examples

### Example 1: Simple Single Workflow

```bash
/bdd-test-code-generator Create a pipeline, start it, verify PipelineRun is running
```

**Result**: Complete test with 3 main steps, all supporting code.

---

### Example 2: Multiple Scenarios in One Feature

```bash
/bdd-test-code-generator NEW_FILE_MULTI Create task | Edit task YAML | Delete task
```

**Result**: Feature file with 3 Scenario Outlines:
- Scenario 1: Create tasks from YAML
- Scenario 2: Edit task YAML definitions
- Scenario 3: Delete tasks and verify removal

---

### Example 3: Append to Existing Feature

```bash
/bdd-test-code-generator APPEND task_management.feature: Verify task list is empty
```

**Result**: New Scenario Outline appended to existing feature file, reuses existing steps.

---

## Best Practices

### 1. Be Specific in Intent

**Good**:
```
Create a task with 3 steps (setup, execute, cleanup), verify task appears in list
```

**Too Vague**:
```
Create task
```

---

### 2. Use Descriptive Resource Names

**Good**:
```yaml
Examples:
  | yaml_file                  | task_name            |
  | task_with_params.yaml      | task-with-params     |
  | multi_step_build_task.yaml | multi-step-build-task|
```

**Not Ideal**:
```yaml
Examples:
  | yaml_file  | task_name |
  | task1.yaml | task1     |
  | task2.yaml | task2     |
```

---

### 3. Review Analysis Report Carefully

The approval gate is your chance to catch issues:
- Check file paths
- Review method names
- Verify locator strategies
- Confirm test data structure

**If something looks off, describe changes instead of approving.**

---

### 4. Run Generated Tests Immediately

```bash
pytest tests/features/generated_feature.feature -v
```

**Why?** Catch any runtime issues early (locators changed, UI updated, etc.)

---

## Advanced Usage

### Combining Multiple Workflows

```bash
/bdd-test-code-generator NEW_FILE_MULTI Create pipeline with 2 tasks | Start pipeline with parameters | Wait for completion | Verify logs contain success message
```

**Result**: Complex end-to-end test with 4 major verification points.

---

### Negative Testing

```bash
/bdd-test-code-generator Create task with invalid YAML, verify error message displayed
```

**Result**: Test that expects failure and validates error handling.

---

### Cleanup Workflows

```bash
/bdd-test-code-generator APPEND task_lifecycle.feature: Delete all tasks in namespace, verify list is empty
```

**Result**: Cleanup scenario added to existing feature.

---

## Benefits

### Before (Manual)
1. Write feature file (15 min)
2. Implement step definitions (30 min)
3. Create/update POM methods (20 min)
4. Generate test data YAML (10 min)
5. Debug compilation errors (10 min)
6. Fix import issues (5 min)

**Total: ~90 minutes per test**

### After (Automated)
1. Type plain English intent (30 sec)
2. Review analysis report (2 min)
3. Approve generation (5 sec)
4. Run tests (30 sec)

**Total: ~3 minutes per test**

**Productivity gain: 30x faster** ⚡

---

## Smart Code Reuse

The skill checks existing code before generating:

```python
# Skill analysis output:
coverage_analysis:
  steps:
    - name: user_logged_into_openshift_kube_admin
      exists: true  # ✅ Will reuse
      file: tests/steps/test_auth_steps.py

    - name: user_creates_task
      exists: false  # ❌ Will generate
      needs_creation: true
```

**Benefit**: Generates only what's missing, integrates with existing code.

---

## Scenario Outline with Examples

All generated tests use **Scenario Outline** pattern:

```gherkin
Scenario Outline: Create tasks from various YAML definitions
  When the user creates a task from YAML file "<yaml_file>"
  Then the task "<task_name>" should appear in the tasks list

  Examples:
    | yaml_file            | task_name        |
    | simple_task.yaml     | simple-task      |
    | multi_step_task.yaml | multi-step-task  |
```

**Why?** Data-driven tests are easier to extend - just add rows!

---

## Safety Features

### 1. Approval Gate
**Never generates code without your approval.**

### 2. Compilation Verification
All generated Python code is compiled before reporting success:
```bash
python -m py_compile generated_file.py
```

### 3. Test Collection Check
Verifies pytest can discover generated tests:
```bash
pytest --collect-only tests/features/new_feature.feature
```

### 4. Existing Code Preservation
Only adds new code, never modifies existing logic without your review.

---

## Common Workflows Supported

The skill uses `framework/resources/ui_workflows.yaml` which maps **50+ workflows** across:

- ✅ **Tasks**: create, edit, delete, view details, view YAML, edit labels/annotations
- ✅ **TaskRuns**: create, view logs, delete
- ✅ **Pipelines**: create (YAML & Builder), start, start with params, edit, delete
- ✅ **PipelineRuns**: create, view logs, view taskruns, rerun, delete
- ✅ **Triggers**: EventListeners, TriggerTemplates, TriggerBindings, ClusterTriggerBindings
- ✅ **Modal actions**: Edit labels, Edit annotations, Delete confirmations

---

## NotebookLM Integration

The skill queries your NotebookLM notebook for domain knowledge:

**Notebook**: "Introducing Tekton: Cloud-Native CI/CD Framework"
**ID**: `ce34f1af-5b8d-47c0-ad62-b21ae6734d95`

**What it retrieves**:
- Tekton resource YAML structure (Tasks, Pipelines, etc.)
- Required and optional fields
- Common parameters and steps
- Best practices and examples
- Validation rules

**Example query during test generation**:
```python
query = "What are the required fields for a Tekton Task YAML definition?"

# NotebookLM returns:
# - apiVersion: tekton.dev/v1
# - kind: Task
# - metadata.name (required)
# - spec.steps (array, required)
# - Common step fields: name, image, script
```

This ensures generated test data is **realistic and valid**.

---

## Example End-to-End Flow

### Step 1: User Input
```bash
/bdd-test-code-generator Create a task with multiple steps, verify task runs successfully
```

### Step 2: Analysis Phase
```
Analyzing intent...
✅ Parsed: resource=Task, actions=[create, verify_execution]
✅ Queried NotebookLM: Retrieved Task YAML structure
✅ Mapped to UI workflow: 8 steps identified
✅ Coverage check: 4/8 steps exist, 4 need generation

Generating analysis report...
```

### Step 3: Approval Request
```markdown
## Test Generation Analysis Report

### Intent Parsed
**Resource**: Task
**Actions**: Create via YAML → Run Task → Verify Execution

### Coverage
**Existing**: 50% (4/8 steps)
**To Generate**: 50% (4/8 steps)

### Generation Plan
- Create: test_data/tasks/complex_task.yaml
- Modify: framework/locators/tasks.py (+2 locators)
- Modify: framework/ui_components/tasks/tasks_page.py (+1 method)
- Create: tests/steps/test_task_execution_steps.py (45 lines)
- Create: tests/features/task_execution.feature (18 lines)

**Approve? (yes/no)**
```

### Step 4: User Approves
```
yes
```

### Step 5: Code Generation
```
Generating code...
✅ Created test_data/tasks/complex_task.yaml
✅ Updated framework/locators/tasks.py
✅ Updated framework/ui_components/tasks/tasks_page.py
✅ Created tests/steps/test_task_execution_steps.py
✅ Created tests/features/task_execution.feature

Verifying...
✅ All files compile successfully
✅ pytest collected 2 tests

Generation complete!
```

### Step 6: Run Tests
```bash
pytest tests/features/task_execution.feature -v
```

---

## Troubleshooting FAQs

### Q: Skill says "POM method exists" but generates duplicate
**A**: The existing method might have different parameters. Review the analysis report - it shows method signatures. Approve anyway and merge manually, or edit the plan.

---

### Q: Generated test data YAML fails in cluster
**A**: The skill uses NotebookLM knowledge, but Tekton versions vary. Check the YAML against your cluster's Tekton version docs. You can also provide more specific intent:

```bash
# Instead of:
/bdd-test-code-generator Create a task

# Try:
/bdd-test-code-generator Create a Tekton v1 task with parameters and workspace
```

---

### Q: How do I use a different NotebookLM notebook?
**A**: Edit the skill's notebook ID configuration to point to your preferred notebook.

---

### Q: Can I customize generated code style?
**A**: Yes! The skill learns from existing tests. To change style, update a few existing test files and the skill will match your new pattern.

---

## Summary

The `bdd-test-code-generator` skill is a complete test generation system that:

✅ **Understands** plain English test intentions
✅ **Queries** NotebookLM for Tekton domain knowledge
✅ **Maps** intents to UI workflows using comprehensive database
✅ **Analyzes** existing code coverage
✅ **Plans** generation with detailed preview
✅ **Waits** for your approval
✅ **Generates** all missing code (feature, steps, POM, locators, test data)
✅ **Verifies** everything compiles and tests are discovered
✅ **Integrates** seamlessly with existing framework

**Result**: Production-ready tests in minutes, not hours.

---

**Ready to try it?**

```bash
/bdd-test-code-generator Create a task, verify it appears in task list
```

Let the magic happen! ✨
