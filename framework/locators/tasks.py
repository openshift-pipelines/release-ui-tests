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
    TASKS_TAB = 'a[role="tab"]:has-text("Tasks")'
    TASK_RUNS_TAB = 'a[href^="/tasks/all-namespaces/"][href$="/task-runs"], a[href^="/tasks/ns/"][href$="/task-runs"]'

    # Search/Filter toolbar
    SEARCH_INPUT = 'input[aria-label="Search input"]'
    # PF6 DataView has no "Filter" button; filtering starts from the attribute dropdown.
    FILTER_BUTTON = "button.pf-m-full-width.pf-v6-c-menu-toggle"
    # Rendered but hidden until at least one filter is applied.
    CLEAR_ALL_FILTERS_BUTTON = '[data-ouia-component-id="DataViewToolbar-clear-all-filters"]'

    # Row actions
    KEBAB_MENU_BUTTON = 'button[aria-label="Actions"]'
    EDIT_LABELS_MENU_ITEM = 'role=menuitem[name="Edit labels"]'
    EDIT_ANNOTATIONS_MENU_ITEM = 'role=menuitem[name="Edit annotations"]'
    EDIT_TASK_MENU_ITEM = 'role=menuitem[name="Edit Task"]'
    DELETE_TASK_MENU_ITEM = 'role=menuitem[name="Delete Task"]'

    # Data load checks
    DATA_GRID = 'table[data-ouia-component-type="PF6/Table"]'
    NO_DATA_MESSAGE = 'div[data-test="empty-box-body"], div.pf-v6-c-empty-state__body:has-text("Not found")'


class TasksPageLocators:
    """Locators specific to the Tasks tab (Task resource listing)."""

    # Task-specific table columns
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    NAMESPACE_COLUMN_HEADER = 'role=columnheader[name="Namespace"]'
    CREATED_COLUMN_HEADER = 'role=columnheader[name="Created"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'

    # Task row verification
    TASK_ROW_BY_NAME = 'tr[data-ouia-component-type="PF6/TableRow"]:has(a[data-test-id="{task_name}"])'
    TASK_NAME_LINK_BY_NAME = 'a[data-test-id="{task_name}"]'


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

    EDIT_TASKRUN_MENU_ITEM = 'role=menuitem[name="Edit TaskRun"]'
    DELETE_TASKRUN_MENU_ITEM = 'role=menuitem[name="Delete TaskRun"]'
    # TaskRun row verification
    TASKRUN_ROW_BY_NAME = 'tr[data-ouia-component-type="PF6/TableRow"]:has-text("{taskrun_name}")'
    TASKRUN_NAME_IN_ROW_BY_NAME = (
        'tr[data-ouia-component-type="PF6/TableRow"]:has-text("{taskrun_name}") '
        "td:first-child a.co-resource-item__resource-name"
    )


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
    TASK_NAME = 'dd[data-test-selector="details-item-value__Name"]'
    TASK_DETAILS_HEADING = 'h2:has-text("Task details")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    NAMESPACE_VALUE = 'dd[data-test-selector="details-item-value__Namespace"]'
    LABELS_VALUE = 'dd[data-test-selector="details-item-value__Labels"]'
    EDIT_LABELS_BUTTON = 'dt:has(button:has-text("Labels")) button:has-text("Edit")'
    ANNOTATIONS_COUNT_VALUE = 'dd[data-test-selector="details-item-value__Annotations"]'
    EDIT_ANNOTATIONS_BUTTON = 'button[data-test="edit-annotations"]'


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


class TaskRunDetailsPageLocators:
    """Locators for the TaskRun Details page"""

    # Breadcrumb
    BREADCRUMB_TASKRUNS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TaskRuns")'
    BREADCRUMB_TASKRUN_DETAILS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TaskRun details")'

    # Page header
    TASKRUN_NAME_HEADING = "div.taskrun-details-page"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'

    # Details section
    TASKRUN_DETAILS_HEADING = 'h2:has-text("TaskRun details")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    STATUS_LABEL = 'dt:has-text("Status")'
    TASKRUN_NAME = 'dd[data-test-selector="details-item-value__Name"]'
    LABELS_VALUE = 'dd[data-test-selector="details-item-value__Labels"]'
    EDIT_LABELS_BUTTON = 'button[data-test="Labels-details-item__edit-button"]'
    EDIT_ANNOTATIONS_BUTTON = 'button[data-test="edit-annotations"]'
    ANNOTATIONS_COUNT_VALUE = 'dd[data-test-selector="details-item-value__Annotations"]'


class TaskRunYamlPageLocators:
    """Locators for the TaskRun YAML editor tab"""

    # Breadcrumb
    BREADCRUMB_TASKRUNS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TaskRuns")'

    # Page header
    TASKRUN_NAME_HEADING = "h1"

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
    # Absent on a completed TaskRun, which the console renders read-only.
    SAVE_BUTTON = '[data-test="save-changes"]'
    RELOAD_BUTTON = 'button:has-text("Reload")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'
