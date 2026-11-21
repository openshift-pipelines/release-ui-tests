# Page Object Model Hierarchy

This document describes the hierarchical organization of page objects in the framework.

## Design Pattern

The framework uses the **Composite Pattern** to organize page objects hierarchically, mirroring the actual UI navigation structure in OpenShift Console.

## Structure

```
page (fixture)
├── raw_page (playwright Page)
├── login (LoginPage)
├── nav (LeftNavigationBar)
├── overview (OverViewPage)
├── pipelines (PipelinesPages)
│   ├── overview (PipelinesOverViewPage)
│   ├── list (PipelinesPage)
│   ├── runs (PipelineRunsPage)
│   ├── repositories (RepositoriesPage)
│   ├── builder (PipelineBuilderPage)
│   ├── pipeline (PipelinePages)
│   │   ├── details (PipelineDetailsPage)
│   │   ├── yaml (PipelineYamlPage)
│   │   ├── parameters (PipelineParametersPage)
│   │   └── runs_tab (PipelinePipelineRunsTabPage)
│   ├── pipelinerun (PipelineRunPages)
│   │   ├── details (PipelineRunDetailsPage)
│   │   ├── yaml (PipelineRunYamlPage)
│   │   ├── parameters (PipelineRunParametersPage)
│   │   ├── logs (PipelineRunLogsPage)
│   │   └── task_runs (PipelineRunTaskRunsPage)
│   └── create_run (CreatePipelineRunPage)
├── tasks (TasksPages)
│   ├── list (TasksPage)
│   ├── runs (TaskRunsPage)
│   ├── task (TaskPages)
│   │   ├── details (TaskDetailsPage)
│   │   └── yaml (TaskYamlPage)
│   └── create (CreateTaskPage)
└── triggers (TriggersPages)
    ├── list (TriggersPage)
    ├── eventlistener (EventListenerPages)
    │   ├── details (EventListenerDetailsPage)
    │   └── yaml (EventListenerYamlPage)
    ├── triggertemplate (TriggerTemplatePages)
    │   ├── details (TriggerTemplateDetailsPage)
    │   └── yaml (TriggerTemplateYamlPage)
    ├── triggerbinding (TriggerBindingPages)
    │   ├── details (TriggerBindingDetailsPage)
    │   └── yaml (TriggerBindingYamlPage)
    └── create (TriggerCreatePages)
        ├── eventlistener (CreateEventListenerPage)
        ├── triggertemplate (CreateTriggerTemplatePage)
        ├── triggerbinding (CreateTriggerBindingPage)
        └── clustertriggerbinding (CreateClusterTriggerBindingPage)
```

## Usage Examples

### Navigating to Pipelines List
```python
await page["nav"].click_pipelines_button()
await page["pipelines"].list.verify_on_page()
await page["pipelines"].list.click_create_button()
```

### Working with Pipeline Details
```python
# Navigate to a specific pipeline's details
await page["pipelines"].pipeline.details.verify_on_page()
name = await page["pipelines"].pipeline.details.get_pipeline_name()

# Switch to YAML tab
await page["pipelines"].pipeline.details.navigate_to_yaml_tab()
await page["pipelines"].pipeline.yaml.verify_on_page()
await page["pipelines"].pipeline.yaml.click_save()
```

### Working with PipelineRuns
```python
# View pipeline runs list
await page["pipelines"].runs.verify_on_page()
await page["pipelines"].runs.click_name_column_header()

# View a specific run's logs
await page["pipelines"].pipelinerun.logs.verify_on_page()
await page["pipelines"].pipelinerun.logs.click_download_logs()
```

### Working with Tasks
```python
# Navigate to tasks
await page["tasks"].list.verify_on_page()
await page["tasks"].list.click_create_button()

# Create a task
await page["tasks"].create.verify_on_page()
await page["tasks"].create.click_save_changes()

# View task details
await page["tasks"].task.details.verify_on_page()
await page["tasks"].task.details.navigate_to_yaml_tab()
await page["tasks"].task.yaml.is_yaml_editor_visible()
```

### Working with Triggers
```python
# Navigate to triggers
await page["triggers"].list.verify_on_page()
await page["triggers"].list.click_event_listeners_tab()

# Create an EventListener
await page["triggers"].create.eventlistener.verify_on_page()
await page["triggers"].create.eventlistener.click_create()

# View EventListener details
await page["triggers"].eventlistener.details.verify_on_page()
name = await page["triggers"].eventlistener.details.get_eventlistener_name()

# Edit YAML
await page["triggers"].eventlistener.yaml.verify_on_page()
await page["triggers"].eventlistener.yaml.click_save()
```

## Benefits

1. **Clear Navigation Path**: The hierarchy mirrors the actual UI navigation
2. **Type Safety**: IDEs can provide autocomplete for available pages
3. **Discoverability**: Easy to find related pages by exploring the hierarchy
4. **Maintainability**: Adding new pages is straightforward
5. **Separation of Concerns**: Each container manages related pages
6. **Testability**: Easy to mock entire sections for testing

## Adding New Pages

When adding a new page:

1. Create the page class in the appropriate module (pipelines/, tasks/, etc.)
2. Create its locator class in framework/locators/
3. Add it to the appropriate container in `page_containers.py`
4. Update this documentation

## Migration Guide

If you have existing tests using the old flat structure, update them as follows:

```python
# Old (flat structure)
await page["pipelines"].click_create_button()
await page["pipeline_details"].verify_on_page()
await page["pipeline_yaml"].click_save()
await page["eventlistener_details"].get_eventlistener_name()

# New (hierarchical structure)
await page["pipelines"].list.click_create_button()
await page["pipelines"].pipeline.details.verify_on_page()
await page["pipelines"].pipeline.yaml.click_save()
await page["triggers"].eventlistener.details.get_eventlistener_name()
```
