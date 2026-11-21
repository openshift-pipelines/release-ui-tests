# Test Migration Guide

This document outlines the changes required to update existing tests to use the new hierarchical page fixture structure.

## Breaking Changes

### 1. Hierarchical Page Fixture Structure

The page fixture now returns a hierarchical structure instead of a flat dictionary.

#### Old Structure (Flat)
```python
page["pipelines"]  # PipelinesPage
page["pipeline_details"]  # PipelineDetailsPage
page["pipeline_yaml"]  # PipelineYamlPage
page["tasks"]  # TasksPage
page["task_details"]  # TaskDetailsPage
page["pipelines_overview"]  # PipelinesOverViewPage
page["triggers"]  # TriggersPage
page["eventlistener_details"]  # EventListenerDetailsPage
```

#### New Structure (Hierarchical)
```python
page["pipelines"].list  # PipelinesPage
page["pipelines"].pipeline.details  # PipelineDetailsPage
page["pipelines"].pipeline.yaml  # PipelineYamlPage
page["tasks"].list  # TasksPage
page["tasks"].task.details  # TaskDetailsPage
page["pipelines"].overview  # PipelinesOverViewPage
page["triggers"].list  # TriggersPage
page["triggers"].eventlistener.details  # EventListenerDetailsPage
```

## Migration Patterns

### Pipelines Section

| Old Pattern | New Pattern |
|-------------|-------------|
| `page["pipelines"].verify_on_page()` | `page["pipelines"].list.verify_on_page()` |
| `page["pipelines"].verify_data_load()` | `page["pipelines"].list.verify_data_load()` |
| `page["pipelines"].navigate_to_pipelines_tab()` | `page["pipelines"].list.navigate_to_pipelines_tab()` |
| `page["pipelines"].navigate_to_pipeline_runs_tab()` | `page["pipelines"].list.navigate_to_pipeline_runs_tab()` |
| `page["pipelines"].navigate_to_repositories_tab()` | `page["pipelines"].list.navigate_to_repositories_tab()` |
| `page["pipelines_overview"].verify_on_page()` | `page["pipelines"].overview.verify_on_page()` |

### Tasks Section

| Old Pattern | New Pattern |
|-------------|-------------|
| `page["tasks"].verify_on_page()` | `page["tasks"].list.verify_on_page()` |
| `page["tasks"].verify_data_load()` | `page["tasks"].list.verify_data_load()` |
| `page["tasks"].navigate_to_tasks_tab()` | `page["tasks"].list.navigate_to_tasks_tab()` |
| `page["tasks"].navigate_to_task_runs_tab()` | `page["tasks"].list.navigate_to_task_runs_tab()` |

### Triggers Section

| Old Pattern | New Pattern |
|-------------|-------------|
| `page["triggers"].verify_on_page()` | `page["triggers"].list.verify_on_page()` |
| `page["triggers"].verify_data_load()` | `page["triggers"].list.verify_data_load()` |
| `page["triggers"].navigate_to_event_listeners_tab()` | `page["triggers"].list.navigate_to_event_listeners_tab()` |
| `page["triggers"].navigate_to_trigger_templates_tab()` | `page["triggers"].list.navigate_to_trigger_templates_tab()` |
| `page["triggers"].navigate_to_trigger_bindings_tab()` | `page["triggers"].list.navigate_to_trigger_bindings_tab()` |
| `page["triggers"].navigate_to_cluster_trigger_bindings_tab()` | `page["triggers"].list.navigate_to_cluster_trigger_bindings_tab()` |

## Files Affected

- `tests/steps/test_common_steps.py` - 25 updates
- `tests/steps/test_pipeline_steps.py` - 1 update
- `tests/steps/test_task_steps.py` - 1 update (also fixed a bug)

## Benefits of New Structure

1. **Clear Navigation Hierarchy**: Mirrors the actual UI navigation
2. **Better Organization**: Related pages grouped together
3. **Type Safety**: IDE autocomplete works better
4. **Maintainability**: Easier to add new pages
5. **Self-Documenting**: Code shows the navigation path

## Example: Complete Scenario Update

### Before
```python
@when("the user navigates to the Pipelines page")
def user_navigates_to_pipelines(page, playwright_event_loop):
    assert run_async(playwright_event_loop, page["nav"].navigate_to_pipelines())
    assert run_async(playwright_event_loop, page["pipelines"].verify_on_page())
    assert run_async(playwright_event_loop, page["pipelines"].verify_data_load(tab_name="Pipelines tab"))
```

### After
```python
@when("the user navigates to the Pipelines page")
def user_navigates_to_pipelines(page, playwright_event_loop):
    assert run_async(playwright_event_loop, page["nav"].navigate_to_pipelines())
    assert run_async(playwright_event_loop, page["pipelines"].list.verify_on_page())
    assert run_async(playwright_event_loop, page["pipelines"].list.verify_data_load(tab_name="Pipelines tab"))
```

## Automated Migration Script

If you have many tests to update, you can use this sed command:

```bash
# Update pipelines references
sed -i 's/page\["pipelines"\]\.verify_on_page/page["pipelines"].list.verify_on_page/g' tests/steps/*.py
sed -i 's/page\["pipelines"\]\.verify_data_load/page["pipelines"].list.verify_data_load/g' tests/steps/*.py
sed -i 's/page\["pipelines"\]\.navigate_to/page["pipelines"].list.navigate_to/g' tests/steps/*.py

# Update tasks references
sed -i 's/page\["tasks"\]\.verify_on_page/page["tasks"].list.verify_on_page/g' tests/steps/*.py
sed -i 's/page\["tasks"\]\.verify_data_load/page["tasks"].list.verify_data_load/g' tests/steps/*.py
sed -i 's/page\["tasks"\]\.navigate_to/page["tasks"].list.navigate_to/g' tests/steps/*.py

# Update triggers references
sed -i 's/page\["triggers"\]\.verify_data_load/page["triggers"].list.verify_data_load/g' tests/steps/*.py
sed -i 's/page\["triggers"\]\.navigate_to/page["triggers"].list.navigate_to/g' tests/steps/*.py

# Update pipelines_overview reference
sed -i 's/page\["pipelines_overview"\]/page["pipelines"].overview/g' tests/steps/*.py
```

Note: The triggers `.verify_on_page()` call was already updated to `.list.verify_on_page()` in line 254 of test_common_steps.py.
