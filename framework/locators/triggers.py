"""Locators for Trigger-related pages (EventListener, TriggerTemplate, TriggerBinding, ClusterTriggerBinding)."""


class TriggersPageLocators:
    """Locators for the Triggers Page"""

    TRIGGERS_HEADER = 'h1:has-text("Triggers")'
    EVENT_LISTENERS_TAB = 'a[role="tab"]:has-text("EventListeners")'
    TRIGGER_TEMPLATES_TAB = (
        'a[href^="/triggers/all-namespaces/"][href$="/trigger-templates"], '
        'a[href^="/triggers/ns/"][href$="/trigger-templates"]'
    )
    TRIGGER_BINDINGS_TAB = (
        'a[href^="/triggers/all-namespaces/"][href$="/trigger-bindings"], '
        'a[href^="/triggers/ns/"][href$="/trigger-bindings"]'
    )
    CLUSTER_TRIGGER_BINDINGS_TAB = (
        'a[href^="/triggers/all-namespaces/"][href$="/cluster-trigger-bindings"], '
        'a[href^="/triggers/ns/"][href$="/cluster-trigger-bindings"]'
    )
    TRIGGERS_DATA_LOAD_CHECK = 'table[data-ouia-component-type="PF6/Table"]'
    TRIGGERS_NO_DATA_LOAD_CHECK = 'div[data-test="empty-box-body"], div.pf-v6-c-empty-state__body'


class CreateEventListenerPageLocators:
    """Locators for the Create EventListener YAML Editor Page"""

    # Page header
    CREATE_EVENTLISTENER_HEADER = 'h1:has-text("Create EventListener")'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    CREATE_BUTTON = 'button:has-text("Create")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'


class CreateTriggerTemplatePageLocators:
    """Locators for the Create TriggerTemplate YAML Editor Page"""

    # Page header
    CREATE_TRIGGERTEMPLATE_HEADER = 'h1:has-text("Create TriggerTemplate")'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    CREATE_BUTTON = 'button:has-text("Create")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'


class CreateTriggerBindingPageLocators:
    """Locators for the Create TriggerBinding YAML Editor Page"""

    # Page header
    CREATE_TRIGGERBINDING_HEADER = 'h1:has-text("Create TriggerBinding")'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    CREATE_BUTTON = 'button:has-text("Create")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'


class CreateClusterTriggerBindingPageLocators:
    """Locators for the Create ClusterTriggerBinding YAML Editor Page"""

    # Page header
    CREATE_CLUSTERTRIGGERBINDING_HEADER = 'h1:has-text("Create ClusterTriggerBinding")'

    # YAML editor
    YAML_EDITOR = ".monaco-editor"

    # Editor toolbar
    COPY_CODE_BUTTON = 'button[aria-label="Copy code to clipboard"]'
    EDITOR_SETTINGS_BUTTON = 'button[aria-label="Editor settings"]'
    TOGGLE_FULLSCREEN_BUTTON = 'button[aria-label="Toggle fullscreen mode"]'
    SHORTCUTS_BUTTON = 'button:has-text("Shortcuts")'

    # Action buttons
    CREATE_BUTTON = 'button:has-text("Create")'
    CANCEL_BUTTON = 'button:has-text("Cancel")'
    DOWNLOAD_BUTTON = 'button:has-text("Download")'


class EventListenerDetailsPageLocators:
    """Locators for the EventListener Details page."""

    # Breadcrumb
    BREADCRUMB_EVENTLISTENERS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("EventListeners")'
    BREADCRUMB_EVENTLISTENER_DETAILS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("EventListener details")'

    # Page header
    EVENTLISTENER_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'

    # Details section
    EVENTLISTENER_DETAILS_HEADING = 'h2:has-text("EventListener details")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    EDIT_LABELS_BUTTON = 'dt:has(button:has-text("Labels")) button:has-text("Edit")'
    ANNOTATIONS_BUTTON = 'button:has-text("annotation")'

    # Conditions section
    CONDITIONS_HEADING = 'h2:has-text("Conditions")'
    CONDITIONS_TABLE = 'h2:has-text("Conditions") + * role=grid'


class EventListenerYamlPageLocators:
    """Locators for the EventListener YAML editor tab."""

    # Breadcrumb
    BREADCRUMB_EVENTLISTENERS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("EventListeners")'

    # Page header
    EVENTLISTENER_NAME_HEADING = "h1"

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


class TriggerTemplateDetailsPageLocators:
    """Locators for the TriggerTemplate Details page."""

    # Breadcrumb
    BREADCRUMB_TRIGGERTEMPLATES_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TriggerTemplates")'
    BREADCRUMB_TRIGGERTEMPLATE_DETAILS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TriggerTemplate details")'

    # Page header
    TRIGGERTEMPLATE_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'

    # Details section
    TRIGGERTEMPLATE_DETAILS_HEADING = 'h2:has-text("TriggerTemplate details")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    EDIT_LABELS_BUTTON = 'dt:has(button:has-text("Labels")) button:has-text("Edit")'
    ANNOTATIONS_BUTTON = 'button:has-text("annotation")'


class TriggerTemplateYamlPageLocators:
    """Locators for the TriggerTemplate YAML editor tab."""

    # Breadcrumb
    BREADCRUMB_TRIGGERTEMPLATES_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TriggerTemplates")'

    # Page header
    TRIGGERTEMPLATE_NAME_HEADING = "h1"

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


class TriggerBindingDetailsPageLocators:
    """Locators for the TriggerBinding Details page."""

    # Breadcrumb
    BREADCRUMB_TRIGGERBINDINGS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TriggerBindings")'
    BREADCRUMB_TRIGGERBINDING_DETAILS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TriggerBinding details")'

    # Page header
    TRIGGERBINDING_NAME_HEADING = "h1"

    # Tabs
    DETAILS_TAB = 'role=tab[name="Details"]'
    YAML_TAB = 'role=tab[name="YAML"]'

    # Details section
    TRIGGERBINDING_DETAILS_HEADING = 'h2:has-text("TriggerBinding details")'
    NAMESPACE_LINK = 'a[href^="/k8s/cluster/namespaces/"]'
    EDIT_LABELS_BUTTON = 'dt:has(button:has-text("Labels")) button:has-text("Edit")'
    ANNOTATIONS_BUTTON = 'button:has-text("annotation")'


class TriggerBindingYamlPageLocators:
    """Locators for the TriggerBinding YAML editor tab."""

    # Breadcrumb
    BREADCRUMB_TRIGGERBINDINGS_LINK = 'nav[aria-label="Breadcrumb"] a:has-text("TriggerBindings")'

    # Page header
    TRIGGERBINDING_NAME_HEADING = "h1"

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
