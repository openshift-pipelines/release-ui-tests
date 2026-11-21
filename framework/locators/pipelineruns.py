"""Locators for PipelineRun-related pages."""


class CreatePipelineRunPageLocators:
    """Locators for the Create PipelineRun YAML Editor Page"""

    # Page header
    CREATE_PIPELINE_RUN_HEADER = 'h1:has-text("Create PipelineRun")'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    TOGGLE_SIDEBAR_BUTTON = 'button[aria-label="Hide sidebar"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    CREATE_BUTTON = 'button:has-text("Create")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'

    # Schema sidebar
    SCHEMA_SIDEBAR_HEADING = 'h2:has-text("PipelineRun")'
    CLOSE_SIDEBAR_BUTTON = 'button:has-text("Close")'
    SCHEMA_TAB = 'role=tab[name="Schema"]'


class PipelineRunBasePageLocators:
    """Common locators for PipelineRun Details and YAML pages (shared UI elements)."""

    # Breadcrumb
    BREADCRUMB_PIPELINERUNS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("PipelineRuns")'

    # Page header
    PIPELINERUN_NAME_HEADING = "div.pipelinerun-details-page"

    # Tabs (common to all PipelineRun pages)
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'
    PARAMETERS_TAB = 'role=tab[name="Parameters"]'
    LOGS_TAB = 'role=tab[name="Logs"]'
    EVENTS_TAB = 'role=tab[name="Events"]'
    APPROVAL_TASKS_TAB = 'role=tab[name="ApprovalTasks"]'
    OUTPUT_TAB = 'role=tab[name="Output"]'
    TASK_RUNS_TAB = 'role=tab[name="TaskRuns"]'

    # Actions menu items (common to all PipelineRun pages)
    ACTIONS_RERUN_MENU_ITEM = 'role=menuitem[name="Rerun"]'
    ACTIONS_DELETE_PIPELINERUN_MENU_ITEM = 'role=menuitem[name="Delete PipelineRun"]'


class PipelineRunDetailsPageLocators:
    """Locators specific to the PipelineRun Details page"""

    # Pipeline visualization
    PIPELINERUN_DETAILS_HEADING = 'h2:has-text("PipelineRun details")'
    ZOOM_IN_BUTTON = 'button:has-text("Zoom in")'
    ZOOM_OUT_BUTTON = 'button:has-text("Zoom out")'
    FIT_TO_SCREEN_BUTTON = 'button:has-text("Fit to screen")'
    RESET_VIEW_BUTTON = 'button:has-text("Reset view")'

    # Details section (left column)
    NAME_BUTTON = 'button:has-text("Name")'
    NAMESPACE_BUTTON = 'button:has-text("Namespace")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    LABELS_BUTTON = 'button:has-text("Labels")'
    EDIT_LABELS_BUTTON = 'dt:has(button:has-text("Labels")) button:has-text("Edit")'
    ANNOTATIONS_BUTTON = 'button:has-text("annotation")'
    CREATED_AT_BUTTON = 'button:has-text("Created at")'
    OWNER_BUTTON = 'button:has-text("Owner")'

    # Status section (right column)
    PIPELINE_LINK = 'a[href*="/tekton.dev~v1~Pipeline/"]'

    # Conditions table
    CONDITIONS_HEADING = 'h2:has-text("Conditions")'
    CONDITIONS_TABLE = 'div:has(h2:has-text("Conditions")) div[role="grid"]'


class PipelineRunYamlPageLocators:
    """Locators specific to the PipelineRun YAML editor tab"""

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    TOGGLE_SIDEBAR_BUTTON = 'button[aria-label="Show sidebar"], button[aria-label="Hide sidebar"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    RELOAD_BUTTON = 'button:has-text("Reload")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'


class PipelineRunParametersPageLocators:
    """Locators specific to the PipelineRun Parameters tab"""

    # Parameters table headers
    NAME_HEADER = 'text="Name*"'
    VALUE_HEADER = 'text="Value"'

    # Parameters display (read-only textboxes)
    PARAMETER_NAME_TEXTBOX = "textbox[disabled]"
    PARAMETER_VALUE_TEXTBOX = "textbox[disabled]"


class PipelineRunLogsPageLocators:
    """Locators specific to the PipelineRun Logs tab"""

    # Task navigation
    TASK_NAVIGATION = 'nav[aria-label="Global"]'
    TASK_LINK = 'nav[aria-label="Global"] a'
    TASK_LINK_ACTIVE = 'nav[aria-label="Global"] a.pf-m-current'

    # Logs toolbar buttons
    DOWNLOAD_BUTTON = 'button:has-text("Download"):not(:has-text("all"))'
    DOWNLOAD_ALL_BUTTON = 'button:has-text("Download all task logs")'
    EXPAND_BUTTON = 'button:has-text("Expand")'

    # Logs content area
    LOGS_CONTAINER = 'div[data-test-id="logs-task-container"]'
    # Logs are in divs within the multi-stream logs component
    # Try multiple selectors to find log content
    LOGS_TEXT_CONTENT = (
        "div.odc-multi-stream-logs__logviewer, div.odc-multi-stream-logs, div.odc-pipeline-run-logs__container"
    )
    LOG_WINDOW = "div.log-window"

    # Task status indicators in navigation
    # Using SVG path detection for stable element identification across theme changes
    # SVG paths are more reliable than RGB colors which vary by theme/PatternFly version
    # These paths correspond to PatternFly icons: CheckCircleIcon, ExclamationCircleIcon, etc.
    # If PatternFly updates icon paths, update these selectors accordingly
    # Status is conveyed only by the icon's path data; the wrapper svg carries no
    # distinguishing class. Success and failure differ from the third decimal
    # (136.967 vs 136.997), so these must anchor with ^= rather than *=.
    TASK_SUCCESS_ICON = 'svg.pf-v6-svg path[d^="M504 256c0 136.967"]'  # CheckCircleIcon
    TASK_FAILURE_ICON = 'svg.pf-v6-svg path[d^="M504 256c0 136.997"]'  # ExclamationCircleIcon
    TASK_RUNNING_ICON = 'svg.pf-v6-svg path[d^="M370.72 133.28"]'  # InProgressIcon
    # Unverified: queued tasks are not rendered in the logs task nav at all on 4.22,
    # so this branch of get_task_status is unreachable and could not be confirmed.
    TASK_PENDING_ICON = 'svg.pf-v6-svg path[d^="M256 8C119"]'  # PendingIcon

    # Status badges/labels
    STATUS_LABEL = '[data-test="status-text"]'
    SUCCESS_STATUS = '[data-test="status-text"]:has-text("Succeeded")'
    FAILED_STATUS = '[data-test="status-text"]:has-text("Failed")'
    RUNNING_STATUS = '[data-test="status-text"]:has-text("Running")'

    # Step information
    STEP_HEADER = 'div:has-text("STEP-")'
    STEP_CONTAINER = 'div[class*="step"]'

    # Loading states
    LOADING_INDICATOR = '[data-test="loading-indicator"]'
    # Transient loading state, so not directly verifiable; the prefix was pre-PF6.
    SKELETON_LOADER = ".pf-v6-c-skeleton"

    # Empty/No data states
    NO_LOGS_MESSAGE = 'text="No logs available"'
    NO_TASKS_MESSAGE = 'text="No tasks found"'


class PipelineRunTaskRunsPageLocators:
    """Locators specific to the PipelineRun TaskRuns tab"""

    # Search/Filter toolbar
    SEARCH_INPUT = 'input[aria-label="Search input"]'
    # PF6 DataView has no "Filter" button; filtering starts from the attribute dropdown.
    FILTER_BUTTON = "button.pf-m-full-width.pf-v6-c-menu-toggle"
    COLUMN_MANAGEMENT_BUTTON = 'button[aria-label="Column management"]'
    # Rendered but hidden until at least one filter is applied.
    CLEAR_ALL_FILTERS_BUTTON = '[data-ouia-component-id="DataViewToolbar-clear-all-filters"]'

    # TaskRuns table columns
    NAME_COLUMN_HEADER = 'role=columnheader[name="Name"]'
    PIPELINE_COLUMN_HEADER = 'role=columnheader[name="Pipeline"]'
    TASK_COLUMN_HEADER = 'role=columnheader[name="Task"]'
    POD_COLUMN_HEADER = 'role=columnheader[name="Pod"]'
    STATUS_COLUMN_HEADER = 'role=columnheader[name="Status"]'
    STARTED_COLUMN_HEADER = 'role=columnheader[name="Started"]'
    ACTIONS_COLUMN_HEADER = 'role=columnheader[name="Actions"]'

    # Row actions
    KEBAB_MENU_BUTTON = 'button[aria-label="Actions"]'

    # Data load checks
    DATA_GRID = 'table[data-ouia-component-type="PF6/Table"]'
