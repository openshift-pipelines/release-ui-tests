# Test-from-Intent Skill System

Automatically generate complete BDD test scenarios from plain English descriptions.

## 🎯 Quick Start

```bash
# In Claude Code, type:
/test-from-intent Create a task with YAML, verify it appears in the task list
```

**That's it!** The skill will:
1. ✅ Analyze your intent and map to UI workflows
2. ✅ Query NotebookLM for Tekton knowledge
3. ✅ Check what code already exists
4. ✅ Present a detailed plan for your approval
5. ✅ Generate all missing code (feature file, steps, POM, test data)
6. ✅ Verify everything compiles and is ready to run

---

## 📚 What Gets Generated

### From this simple input:
```
/test-from-intent Create a task with YAML, verify it appears in task list
```

### You get ALL of this:

**1. Feature File** (`tests/features/task_creation.feature`)
```gherkin
Feature: Task Creation and Verification

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user clicks on Pipelines button          # Step 1: Expand submenu
    When the user navigates to the Tasks page         # Step 2: Click Tasks link

  @smoke @sanity
  Scenario Outline: Create tasks from various YAML definitions
    When the user creates a task from YAML file "<yaml_file>"
    Then the task "<task_name>" should appear in the tasks list

    Examples:
      | yaml_file            | task_name        |
      | simple_task.yaml     | simple-task      |
      | multi_step_task.yaml | multi-step-task  |
```

**Navigation Pattern**:

**Background**: Includes TWO explicit steps after login:
1. Click Pipelines button (expands submenu to show Tasks/Pipelines/Triggers/Overview links)
2. Navigate to specific page (clicks the link, verifies page loaded)

**Action Steps**: ALWAYS navigate to list page first because:
- Browser session is shared between scenarios
- Previous scenario may have left browser on any page (details, YAML editor, etc.)
- Each step must be self-contained and ensure consistent starting state

Example: "creates a task" step ALWAYS navigates to Tasks list page first, then performs create action.

Note: Pipelines button is a toggle - click to expand, click again to collapse.

**2. Step Definitions** (`tests/steps/test_task_creation_steps.py`)
```python
@when(parsers.parse('the user creates a task from YAML file "{yaml_file}"'))
def create_task_from_yaml(page, yaml_file, playwright_event_loop, config):
    # Automatically generated with proper async handling
    # ALWAYS navigates to Tasks list page first (browser session shared between scenarios)
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
    """Generated method with proper docstring."""
    return await self.click_element(self.locators.CREATE_BUTTON)


async def verify_task_in_list(self, task_name: str) -> bool:
    """Generated verification method."""
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

## 🚀 Usage Examples

### Example 1: Simple Single Workflow

```bash
/test-from-intent Create a pipeline, start it, verify PipelineRun is running
```

**Result**: Complete test with 3 main steps, all supporting code.

---

### Example 2: Multiple Scenarios in One Feature

```bash
/test-from-intent NEW_FILE_MULTI Create task | Edit task YAML | Delete task
```

**Result**: Feature file with 3 Scenario Outlines:
- Scenario 1: Create tasks from YAML
- Scenario 2: Edit task YAML definitions
- Scenario 3: Delete tasks and verify removal

---

### Example 3: Append to Existing Feature

```bash
/test-from-intent APPEND task_management.feature: Verify task list is empty
```

**Result**: Adds new Scenario Outline to existing feature file, reuses existing steps where possible.

---

## 🧠 How It Works

### Phase 1: Analysis (requires your approval)

1. **Parse Intent** → "Create task" = resource:Task, action:create, method:yaml
2. **Query NotebookLM** → Get Tekton Task YAML structure, required fields
3. **Map to UI Workflow** → Uses `framework/resources/ui_workflows.yaml`
   ```
   Navigate to Tasks → Click Create → Fill YAML → Submit → Verify
   ```
4. **Check Coverage** → What exists vs. needs generation?
   - ✅ Login step exists
   - ✅ Navigate to Tasks exists
   - ❌ Create task step missing → GENERATE
   - ❌ Verify in list missing → GENERATE
   - ✅ YAML editor POM method exists
   - ❌ List verification method missing → GENERATE

5. **Present Plan** → Detailed report showing:
   - What will be generated
   - Where code will be added
   - What test data will be created
   - Final feature file structure

6. **Wait for Approval** → You review and say "yes" to proceed

### Phase 2: Generation (after approval)

7. **Generate Test Data** → Query NotebookLM for realistic examples
8. **Add Locators** → Append to appropriate locators file
9. **Add POM Methods** → Update page classes with new methods
10. **Generate Steps** → Create parametrized step definitions
11. **Generate Feature** → Create Scenario Outline with Examples
12. **Verify** → Compile all files, confirm tests collected

---

## 🗺️ UI Workflows Database

The skill uses `framework/resources/ui_workflows.yaml` which maps **50+ workflows** across:

- ✅ **Tasks**: create, edit, delete, view details, view YAML, edit labels/annotations
- ✅ **TaskRuns**: create, view logs, delete
- ✅ **Pipelines**: create (YAML & Builder), start, start with params, edit, delete
- ✅ **PipelineRuns**: create, view logs, view taskruns, rerun, delete
- ✅ **Triggers**: EventListeners, TriggerTemplates, TriggerBindings, ClusterTriggerBindings
- ✅ **Modal actions**: Edit labels, Edit annotations, Delete confirmations

**Example workflow entry**:
```yaml
tasks:
  create_yaml:
    name: "Create Task via YAML"
    intent_keywords: ["create task", "new task", "task from yaml"]
    steps:
      - page: "tasks.list"
        actions:
          - action: "click_create_button"
            method: "click_create_button"
      - page: "tasks.create"
        actions:
          - action: "fill_yaml_editor"
            params: ["yaml_content"]
          - action: "click_create"
      - page: "tasks.task.details"
        verification:
          - method: "get_task_name"
            expected: "matches_yaml_metadata_name"
```

---

## 📖 NotebookLM Integration

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

## 🎛️ Input Modes

### Mode 1: `NEW_FILE` (default)
Creates new feature file with single scenario outline.

```bash
/test-from-intent Create a task, verify it in list
# or explicitly:
/test-from-intent NEW_FILE Create a task, verify it in list
```

---

### Mode 2: `NEW_FILE_MULTI`
Creates new feature file with multiple scenario outlines from pipe-separated intents.

```bash
/test-from-intent NEW_FILE_MULTI Create task | Edit task | Delete task
```

**Result**: 3 separate Scenario Outlines in one feature file.

---

### Mode 3: `APPEND`
Adds scenario to existing feature file.

```bash
/test-from-intent APPEND task_management.feature: Delete task and verify removal
```

**Result**: New Scenario Outline appended to existing file, reuses existing steps.

---

## 🔧 Advanced Features

### Smart Code Reuse

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

### Scenario Outline with Examples

All generated tests use **Scenario Outline** pattern (as you requested):

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

**Navigation Note**: Background includes TWO steps:
1. "When the user clicks on Pipelines button" - expands submenu
2. "When the user navigates to the Tasks page" - clicks Tasks link, verifies page loaded

---

### Automatic Test Data Generation

Test data YAML files are generated using NotebookLM knowledge:

**Generated**:
```yaml
# framework/resources/test_data/tasks/multi_step_task.yaml
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
        echo "Setting up..."
    - name: execute
      image: registry.redhat.io/ubi9/ubi-minimal
      script: |
        echo "Executing: $(params.message)"
```

**Benefit**: Realistic, valid test data based on Tekton best practices.

---

## 📊 Detailed Analysis Report

Before generating any code, the skill presents a complete analysis:

**Report includes**:
- ✅ Intent parsing results
- ✅ NotebookLM knowledge retrieved
- ✅ UI workflow mapped (step-by-step)
- ✅ Existing coverage analysis (what exists vs. needs generation)
- ✅ Complete generation plan with:
  - Files to create
  - Files to modify
  - Code snippets preview
  - Line counts
- ✅ Final feature file preview

**You review and approve before any code is generated.**

---

## 🛡️ Safety Features

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

## 🎓 Learning from Existing Tests

The skill analyzes your existing test patterns:

```python
# Learns from:
tests/steps/test_auth_steps.py      # How you structure auth steps
tests/steps/test_navigation_steps.py # How you handle navigation
tests/features/*.feature            # Your Gherkin style

# Applies patterns to new code:
- Same docstring format
- Same parameter ordering
- Same assertion style
- Same error handling
```

**Result**: Generated code matches your existing style.

---

## 🚦 Example End-to-End Flow

### Step 1: User Input
```bash
/test-from-intent Create a task with multiple steps, verify task runs successfully
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

## 📁 File Structure

```
release-ui-tests/
├── .claude/skills/test-from-intent/
│   ├── skill.md           # Main skill logic
│   └── README.md          # This file
│
├── framework/
│   ├── resources/
│   │   ├── ui_workflows.yaml      # 50+ workflow mappings
│   │   └── test_data/
│   │       ├── tasks/              # Generated task YAMLs
│   │       ├── pipelines/          # Generated pipeline YAMLs
│   │       └── ...
│   │
│   ├── locators/                  # Locator classes (updated by skill)
│   └── ui_components/             # Page objects (updated by skill)
│
└── tests/
    ├── features/                  # Feature files (generated by skill)
    └── steps/                     # Step definitions (generated by skill)
```

---

## 🔍 Troubleshooting

### Q: Skill says "POM method exists" but generates duplicate
**A**: The existing method might have different parameters. Review the analysis report - it shows method signatures. Approve anyway and merge manually, or edit the plan.

---

### Q: Generated test data YAML fails in cluster
**A**: The skill uses NotebookLM knowledge, but Tekton versions vary. Check the YAML against your cluster's Tekton version docs. You can also provide more specific intent:

```bash
# Instead of:
/test-from-intent Create a task

# Try:
/test-from-intent Create a Tekton v1 task with parameters and workspace
```

---

### Q: How do I use a different NotebookLM notebook?
**A**: Edit `.claude/skills/test-from-intent/skill.md` and update the `notebook_id` constant to point to your preferred notebook.

---

### Q: Can I customize generated code style?
**A**: Yes! The skill learns from existing tests. To change style, update a few existing test files and the skill will match your new pattern.

---

## 🎯 Best Practices

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

## 🌟 Advanced Usage

### Combining Multiple Workflows

```bash
/test-from-intent NEW_FILE_MULTI Create pipeline with 2 tasks | Start pipeline with parameters | Wait for completion | Verify logs contain success message
```

**Result**: Complex end-to-end test with 4 major verification points.

---

### Negative Testing

```bash
/test-from-intent Create task with invalid YAML, verify error message displayed
```

**Result**: Test that expects failure and validates error handling.

---

### Cleanup Workflows

```bash
/test-from-intent APPEND task_lifecycle.feature: Delete all tasks in namespace, verify list is empty
```

**Result**: Cleanup scenario added to existing feature.

---

## 📈 Benefits

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

## 🎉 Summary

The `test-from-intent` skill is a complete test generation system that:

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

## 📞 Support

**Issues?** Open a discussion or report bugs.

**Feature requests?** Describe your use case and we'll enhance the skill.

**Questions?** Check the main skill file (`skill.md`) for detailed implementation notes.

---

**Ready to try it?**

```bash
/test-from-intent Create a task, verify it appears in task list
```

Let the magic happen! ✨
