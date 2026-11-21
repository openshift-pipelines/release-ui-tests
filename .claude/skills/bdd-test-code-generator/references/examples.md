# Examples

## Example 1: Task CRUD Operations

**Input**:
```bash
/bdd-test-code-generator NEW_FILE_MULTI Create task from YAML | Edit task YAML | Delete task
```

**Generated**:
- `tests/features/task_crud_operations.feature` (3 Scenario Outlines)
- `tests/steps/test_task_crud_steps.py` (6 step definitions)
- `framework/resources/test_data/tasks/*.yaml` (test YAML files)
- Updated POM methods and locators (if missing)

## Example 2: Pipeline Workflow

**Input**:
```bash
/bdd-test-code-generator Create pipeline with two tasks, start pipeline, verify PipelineRun is running
```

**Generated**:
- Complete test for complex multi-step workflow
- Pipeline and Task test data
- All supporting code
