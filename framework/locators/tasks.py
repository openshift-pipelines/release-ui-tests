"""Locators for Task-related pages."""


class TasksBasePageLocators:
    """Common locators for Tasks and TaskRuns pages (shared UI elements)."""

    # Page header
    TASKS_HEADER = 'h1:has-text("Tasks")'

    # Create actions
    CREATE_BUTTON = '[data-test="item-create"]'
    CREATE_TASK_MENU_ITEM = 'role=menuitem[name="Task"]'
    CREATE_TASK_RUN_MENU_ITEM = 'role=menuitem[name="TaskRun"]'

    # Tab navigation
    TASKS_TAB = 'a[href^="/tasks/all-namespaces"], a[href^="/tasks/ns/"]'
    TASK_RUNS_TAB = 'a[href^="/tasks/all-namespaces/"][href$="/task-runs"], a[href^="/tasks/ns/"][href$="/task-runs"]'

    # Search/Filter toolbar
    SEARCH_INPUT = 'input[placeholder="Search by name..."]'
    FILTER_BUTTON = 'button:has-text("Filter")'
    COLUMN_MANAGEMENT_BUTTON = 'button[aria-label="Column management"]'
    CLEAR_ALL_FILTERS_BUTTON = 'button:has-text("Clear all filters")'

    # Row actions
    KEBAB_MENU_BUTTON = 'button[aria-label="kebab menu"]'
    EDIT_TASK_MENU_ITEM = 'role=menuitem[name="Edit Task"]'
    DELETE_TASK_MENU_ITEM = 'role=menuitem[name="Delete Task"]'

    # Data load checks
    DATA_GRID = "table.ReactVirtualized__VirtualGrid"
    NO_DATA_MESSAGE = "#no-resource-msg"


class TasksPageLocators:
    """Locators specific to the Tasks tab (Task resource listing)."""

    # Task-specific table columns
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    NAMESPACE_COLUMN_HEADER = 'role=columnheader[name="Namespace"]'
    CREATED_COLUMN_HEADER = 'role=columnheader[name="Created"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'

    # Task row verification
    TASK_ROW_BY_NAME = 'tr[data-test-rows="resource-row"]:has-text("{task_name}")'
    TASK_NAME_LINK = 'tr[data-test-rows="resource-row"]:has-text("{task_name}") a[href*="/tekton.dev~v1~Task/"]'


class TaskRunsPageLocators:
    """Locators specific to the TaskRuns tab (TaskRun resource listing)."""

    # TaskRun-specific table columns
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    PIPELINE_COLUMN_HEADER = 'role=columnheader[name="Pipeline"]'
    TASK_COLUMN_HEADER = 'role=columnheader[name="Task"]'
    POD_COLUMN_HEADER = 'role=columnheader[name="Pod"]'
    STATUS_COLUMN_HEADER = 'role=columnheader[name="Status"]'
    STARTED_COLUMN_HEADER = 'role=columnheader[name="Started"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'

    DELETE_TASKRUN_MENU_ITEM = 'role=menuitem[name="Delete TaskRun"]'
    # TaskRun row verification
    TASKRUN_ROW_BY_NAME = 'tr[data-test-rows="resource-row"]:has-text("{taskrun_name}")'


class CreateTaskPageLocators:
    """Locators for the Create Task YAML Editor Page"""

    # Page header
    CREATE_TASK_HEADER = 'h1:has-text("Create Task")'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    TOGGLE_SIDEBAR_BUTTON = 'button[aria-label="Hide sidebar"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    SAVE_CHANGES_BUTTON = '[data-test="save-changes"]'
    CANCEL_BUTTON = '[data-test="cancel"]'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'

    # Schema sidebar
    SCHEMA_SIDEBAR_HEADING = 'h2:has-text("Task")'
    CLOSE_SIDEBAR_BUTTON = 'button[aria-label="Close"]'
    SCHEMA_TAB = 'role=tab[name="Schema"]'


class TaskDetailsPageLocators:
    """Locators for the Task Details page"""

    # Breadcrumb
    BREADCRUMB_TASKS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("Tasks")'
    BREADCRUMB_TASK_DETAILS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("Task details")'

    # Page header
    TASK_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'

    # Details section
    TASK_DETAILS_HEADING = 'h2:has-text("Task details")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    EDIT_LABELS_BUTTON = 'dt:has(button:has-text("Labels")) button:has-text("Edit")'
    ANNOTATIONS_BUTTON = 'button:has-text("annotations")'

    # Field values for validation
    NAMESPACE_VALUE = 'dt:has-text("Namespace") + dd a'
    LABELS_SECTION = 'dt:has-text("Labels") + dd'
    LABEL_BADGE = 'dt:has-text("Labels") + dd span.pf-v5-c-label__content'
    ANNOTATIONS_COUNT = 'button:has-text("annotation")'


class TaskYamlPageLocators:
    """Locators for the Task YAML editor tab"""

    # Breadcrumb
    BREADCRUMB_TASKS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("Tasks")'

    # Page header
    TASK_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'

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


class CreateTaskRunPageLocators:
    """Locators for the Create TaskRun YAML Editor Page"""

    # Page header
    CREATE_TASKRUN_HEADER = 'h1:has-text("Create TaskRun")'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    TOGGLE_SIDEBAR_BUTTON = 'button[aria-label="Hide sidebar"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    SAVE_CHANGES_BUTTON = '[data-test="save-changes"]'
    CANCEL_BUTTON = '[data-test="cancel"]'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'

    # Schema sidebar
    SCHEMA_SIDEBAR_HEADING = 'h2:has-text("TaskRun")'
    CLOSE_SIDEBAR_BUTTON = 'button[aria-label="Close"]'
    SCHEMA_TAB = 'role=tab[name="Schema"]'


class TaskRunBasePageLocators:
    """Common locators for TaskRun pages (shared UI elements across Details, YAML, Logs, Events)."""

    # Breadcrumb
    BREADCRUMB_TASKRUNS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TaskRuns")'

    # Page header
    TASKRUN_NAME_HEADING = "h1"

    # Tabs (common to all TaskRun pages)
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'
    LOGS_TAB = 'role=tab[name="Logs"]'
    EVENTS_TAB = 'role=tab[name="Events"]'


class TaskRunDetailsPageLocators:
    """Locators for the TaskRun Details page"""

    # Details section
    TASKRUN_DETAILS_HEADING = 'h2:has-text("TaskRun details")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    STATUS_LABEL = 'dt:has-text("Status")'
    TASK_LINK = 'dt:has-text("Task") + dd a'

    # Field values for validation
    NAMESPACE_VALUE = 'dt:has-text("Namespace") + dd a'
    LABELS_SECTION = 'dt:has-text("Labels") + dd'
    LABEL_BADGE = 'dt:has-text("Labels") + dd span.pf-v5-c-label__content'
    ANNOTATIONS_COUNT = 'button:has-text("annotation")'


class TaskRunYamlPageLocators:
    """Locators for the TaskRun YAML editor tab"""

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


class TaskRunLogsPageLocators:
    """Locators for the TaskRun Logs tab"""

    # Step navigation
    STEP_NAVIGATION = 'nav[aria-label="Global"]'
    STEP_LINK = 'nav[aria-label="Global"] a'

    # Logs toolbar buttons
    DOWNLOAD_BUTTON = 'button:has-text("Download"):not(:has-text("all"))'
    DOWNLOAD_ALL_BUTTON = 'button:has-text("Download all task logs")'
    EXPAND_BUTTON = 'button:has-text("Expand")'

    # Logs content area
    LOGS_CONTAINER = 'div:has(> div:has-text("STEP-"))'


class TaskRunEventsPageLocators:
    """Locators for the TaskRun Events tab"""

    # Events page specific
    STREAMING_STATUS = 'generic:has-text("Streaming events")'
    PAUSE_STREAMING_BUTTON = 'button:has-text("Pause event streaming")'
    EVENTS_GRID = 'grid[aria-label="grid"]'
    EVENT_ROW = 'grid[aria-label="grid"] > row'
    SHOWING_COUNT = 'generic:has-text("Showing")'
