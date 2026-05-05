"""Locators for Pipeline-related pages."""


class PipelinesBasePageLocators:
    """Common locators for Pipelines, PipelineRuns, and Repositories pages (shared UI elements)."""

    # Page header
    PIPELINES_HEADER = 'h1:has-text("Pipelines")'
    SETUP_GITHUB_APP_LINK = 'a:has-text("Setup GitHub App")'

    # Create actions
    CREATE_BUTTON = 'button:has-text("Create")'
    CREATE_PIPELINE_MENU_ITEM = 'role=menuitem[name="Pipeline"]'
    CREATE_PIPELINE_RUN_MENU_ITEM = 'role=menuitem[name="PipelineRun"]'
    CREATE_REPOSITORY_MENU_ITEM = 'role=menuitem[name="Repository"]'

    # Tab navigation
    PIPELINES_TAB = 'a[href^="/pipelines/ns/"]'
    PIPELINE_RUNS_TAB = 'a[href^="/pipelines/ns/"][href$="/pipeline-runs"]'
    REPOSITORIES_TAB = 'a[href^="/pipelines/ns/"][href$="/repositories"]'

    # Search/Filter toolbar
    SEARCH_INPUT = 'input[placeholder="Search by name..."]'
    FILTER_BUTTON = 'button:has-text("Filter")'
    CLEAR_ALL_FILTERS_BUTTON = 'button:has-text("Clear all filters")'

    # Row actions
    KEBAB_MENU_BUTTON = 'button[aria-label="kebab menu"]'

    # Data load checks
    DATA_GRID = "table.ReactVirtualized__VirtualGrid"
    NO_DATA_MESSAGE = "#no-resource-msg"


class PipelinesPageLocators:
    """Locators specific to the Pipelines tab"""

    # Pipeline-specific table columns
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    LAST_RUN_COLUMN_HEADER = 'role=columnheader[name="Last run"]'
    TASK_STATUS_COLUMN_HEADER = 'role=columnheader[name="Task status"]'
    LAST_RUN_STATUS_COLUMN_HEADER = 'role=columnheader[name="Last run status"]'
    LAST_RUN_TIME_COLUMN_HEADER = 'role=columnheader[name="Last run time"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'

    # Pipeline-specific actions
    VIEW_LOGS_BUTTON = 'button:has-text("View logs")'

    # Kebab menu items (Pipeline-specific)
    START_MENU_ITEM = 'role=menuitem[name="Start"]'
    START_LAST_RUN_MENU_ITEM = 'role=menuitem[name="Start last run"]'
    ADD_TRIGGER_MENU_ITEM = 'role=menuitem[name="Add Trigger"]'
    REMOVE_TRIGGER_MENU_ITEM = 'role=menuitem[name="Remove Trigger"]'
    EDIT_LABELS_MENU_ITEM = 'role=menuitem[name="Edit labels"]'
    EDIT_ANNOTATIONS_MENU_ITEM = 'role=menuitem[name="Edit annotations"]'
    EDIT_PIPELINE_MENU_ITEM = 'role=menuitem[name="Edit Pipeline"]'
    DELETE_PIPELINE_MENU_ITEM = 'role=menuitem[name="Delete Pipeline"]'

    # Pipeline row verification
    PIPELINE_ROW_BY_NAME = 'tr[data-test-rows="resource-row"]:has-text("{pipeline_name}")'


class PipelineRunsPageLocators:
    """Locators specific to the PipelineRuns tab"""

    # PipelineRun-specific table columns
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    VULNERABILITIES_COLUMN_HEADER = 'role=columnheader[name="Vulnerabilities"]'
    STATUS_COLUMN_HEADER = 'role=columnheader[name="Status"]'
    TASK_STATUS_COLUMN_HEADER = 'role=columnheader[name="Task status"]'
    STARTED_COLUMN_HEADER = 'role=columnheader[name="Started"]'
    DURATION_COLUMN_HEADER = 'role=columnheader[name="Duration"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'

    # PipelineRun-specific actions
    VIEW_LOGS_BUTTON = 'button:has-text("View logs")'

    # Row verification and actions
    PIPELINERUN_ROW_BY_NAME = 'tr[data-test-rows="resource-row"]:has-text("{pipelinerun_name}")'
    PIPELINERUN_STATUS_CELL = 'tr:has-text("{pipelinerun_name}") td.pf-v5-c-table__td:nth-child(3)'
    DELETE_PIPELINERUN_MENU_ITEM = 'role=menuitem[name="Delete PipelineRun"]'


class RepositoriesPageLocators:
    """Locators specific to the Repositories tab"""

    # Repository-specific table columns (to be filled when page is analyzed)
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'


class PipelineBuilderPageLocators:
    """Common locators for Pipeline Builder page (shared across both views)."""

    # Page header
    PIPELINE_BUILDER_HEADER = 'h2:has-text("Pipeline builder")'

    # Configuration mode switcher
    PIPELINE_BUILDER_RADIO = 'input[type="radio"] + label:has-text("Pipeline builder")'
    YAML_VIEW_RADIO = 'input[type="radio"] + label:has-text("YAML view")'

    # Form actions (common to both views)
    CREATE_BUTTON = 'button:has-text("Create")'
    SAVE_BUTTON = 'button:has-text("Save")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'


class BuilderViewLocators:
    """Locators specific to the Pipeline Builder's visual form view."""

    # Form fields
    PIPELINE_NAME_INPUT = 'input[type="text"]'

    # Tasks section
    ADD_TASK_BUTTON = 'button:has-text("Add task"), div:has-text("Add task")'
    ADD_FINALLY_TASK_BUTTON = 'div:has-text("Add finally task")'

    # Parameters section
    ADD_PARAMETER_BUTTON = 'button:has-text("Add parameter")'

    # Workspaces section
    ADD_WORKSPACE_BUTTON = 'button:has-text("Add workspace")'

    # Quick search dialog
    QUICK_SEARCH_DIALOG = 'dialog[aria-label="Quick search"]'
    QUICK_SEARCH_INPUT = 'input[placeholder="Add task..."]'
    QUICK_SEARCH_LIST = 'list[aria-label="Quick search list"]'
    ADD_TASK_FROM_SEARCH_BUTTON = 'button:has-text("Add")'


class YamlViewLocators:
    """Locators specific to the Pipeline Builder's YAML editor view."""

    # YAML editor (Monaco editor)
    YAML_EDITOR = ".monaco-editor"
    YAML_EDITOR_MOUNTED = '[data-test="code-editor"]'

    # Sidebar panel
    SIDEBAR_CLOSE_BUTTON = 'button:has-text("Close")'
    SAMPLES_TAB = 'role=tab[name="Samples"]'
    SNIPPETS_TAB = 'role=tab[name="Snippets"]'

    # Sample pipelines (in Samples tab)
    SAMPLE_TRY_IT_BUTTON = 'button:has-text("Try it")'
    SAMPLE_DOWNLOAD_YAML_BUTTON = 'button:has-text("Download YAML")'


class OverViewPageLocators:
    """Locators for the Overview Page"""

    OVERVIEW_HEADER = 'h1:has-text("Overview")'
    SKIP_TOUR_BUTTON = 'button:has-text("Skip tour")'


class PipelinesOverViewPageLocators:
    """Locators for the Pipelines Overview Page"""

    OVERVIEW_HEADER = 'h2:has-text("Overview")'


class PipelineDetailsPageLocators:
    """Locators for the Pipeline Details page"""

    # Breadcrumb
    BREADCRUMB_PIPELINES_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("Pipelines")'
    BREADCRUMB_PIPELINE_DETAILS_TEXT = 'nav[aria-label="Breadcrumb"] >> text="Pipeline details"'

    # Page header
    PIPELINE_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'
    PARAMETERS_TAB = 'role=tab[name="Parameters"]'
    METRICS_TAB = 'role=tab[name="Metrics"]'
    PIPELINERUNS_TAB = 'role=tab[name="PipelineRuns"]'

    # Pipeline visualization controls
    PIPELINE_DETAILS_HEADING = 'h2:has-text("Pipeline details")'
    ZOOM_IN_BUTTON = 'button:has-text("Zoom in")'
    ZOOM_OUT_BUTTON = 'button:has-text("Zoom out")'
    FIT_TO_SCREEN_BUTTON = 'button:has-text("Fit to screen")'
    RESET_VIEW_BUTTON = 'button:has-text("Reset view")'

    # Details section
    NAME_BUTTON = 'button:has-text("Name")'
    NAMESPACE_BUTTON = 'button:has-text("Namespace")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    LABELS_BUTTON = 'button:has-text("Labels")'
    EDIT_LABELS_BUTTON = 'dt:has(button:has-text("Labels")) button:has-text("Edit")'
    ANNOTATIONS_BUTTON = 'button:has-text("Annotations")'
    CREATED_AT_BUTTON = 'button:has-text("Created at")'
    OWNER_BUTTON = 'button:has-text("Owner")'


class PipelineYamlPageLocators:
    """Locators for the Pipeline YAML editor tab"""

    # Breadcrumb
    BREADCRUMB_PIPELINES_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("Pipelines")'

    # Page header
    PIPELINE_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'
    PARAMETERS_TAB = 'role=tab[name="Parameters"]'
    METRICS_TAB = 'role=tab[name="Metrics"]'
    PIPELINERUNS_TAB = 'role=tab[name="PipelineRuns"]'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    TOGGLE_SIDEBAR_BUTTON = 'button[aria-label="Show sidebar"], button[aria-label="Hide sidebar"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    SAVE_BUTTON = 'button:has-text("Save")'
    RELOAD_BUTTON = 'button:has-text("Reload")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'


class PipelineParametersPageLocators:
    """Locators for the Pipeline Parameters tab"""

    # Breadcrumb
    BREADCRUMB_PIPELINES_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("Pipelines")'

    # Page header
    PIPELINE_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'
    PARAMETERS_TAB = 'role=tab[name="Parameters"]'
    METRICS_TAB = 'role=tab[name="Metrics"]'
    PIPELINERUNS_TAB = 'role=tab[name="PipelineRuns"]'

    # Parameters editor
    PARAMETER_NAME_INPUT = 'textbox[placeholder="Name"]'
    PARAMETER_DESCRIPTION_INPUT = 'textbox[placeholder="Description"]'
    PARAMETER_DEFAULT_VALUE_INPUT = 'textbox[placeholder="Default value"]'
    REMOVE_PARAMETER_BUTTON = 'button:has-text("Remove")'
    ADD_PARAMETER_BUTTON = 'button:has-text("Add Pipeline parameter")'

    # Action buttons
    SAVE_BUTTON = 'button:has-text("Save")'
    RELOAD_BUTTON = 'button:has-text("Reload")'


class PipelinePipelineRunsTabPageLocators:
    """Locators for the Pipeline PipelineRuns tab"""

    # Breadcrumb
    BREADCRUMB_PIPELINES_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("Pipelines")'

    # Page header
    PIPELINE_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'
    PARAMETERS_TAB = 'role=tab[name="Parameters"]'
    METRICS_TAB = 'role=tab[name="Metrics"]'
    PIPELINERUNS_TAB = 'role=tab[name="PipelineRuns"]'

    # Search/Filter toolbar
    SEARCH_INPUT = 'input[placeholder="Search by name..."]'
    FILTER_BUTTON = 'button:has-text("Filter")'
    CLEAR_ALL_FILTERS_BUTTON = 'button:has-text("Clear all filters")'

    # PipelineRun-specific table columns
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    VULNERABILITIES_COLUMN_HEADER = 'role=columnheader[name="Vulnerabilities"]'
    STATUS_COLUMN_HEADER = 'role=columnheader[name="Status"]'
    TASK_STATUS_COLUMN_HEADER = 'role=columnheader[name="Task status"]'
    STARTED_COLUMN_HEADER = 'role=columnheader[name="Started"]'
    DURATION_COLUMN_HEADER = 'role=columnheader[name="Duration"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'

    # PipelineRun-specific actions
    VIEW_LOGS_BUTTON = 'button:has-text("View logs")'
    KEBAB_MENU_BUTTON = 'button[aria-label="kebab menu"]'

    # Data load checks
    DATA_GRID = "table.ReactVirtualized__VirtualGrid"
