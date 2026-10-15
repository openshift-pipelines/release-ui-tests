"""Locators for the Software Catalog operator install flow.

OpenShift 4.22 replaced OperatorHub with the Software Catalog: `/operatorhub` now
redirects to `/catalog/...?catalogType=operator`, reached from Ecosystem in the left
navigation. Every selector below was probed against a live 4.22 console during a real
install.
"""


class SoftwareCatalogNavLocators:
    """Left navigation: Ecosystem and its children."""

    ECOSYSTEM_BUTTON = 'button.pf-v6-c-nav__link:has-text("Ecosystem")'
    SOFTWARE_CATALOG_LINK = 'a.pf-v6-c-nav__link:has-text("Software Catalog")'
    INSTALLED_OPERATORS_LINK = 'a.pf-v6-c-nav__link:has-text("Installed Operators")'


class SoftwareCatalogLocators:
    """The catalog grid and its keyword filter."""

    KEYWORD_FILTER = 'input[placeholder="Filter by keyword..."]'
    CATALOG_TILE = '[data-test^="operator-"]'

    # Each card's id encodes its catalog source, which is the only reliable way to
    # tell the entries apart: with a custom CatalogSource installed, two cards share
    # the display name "Red Hat OpenShift Pipelines" - one from Red Hat, one from
    # Custom Operators - so data-test alone is ambiguous.
    OSP_PACKAGE = "openshift-pipelines-operator-rh"
    MARKETPLACE_NAMESPACE = "openshift-marketplace"
    PROVIDER_BADGE = ".catalog-tile-pf-badge"

    @staticmethod
    def operator_card(display_name: str) -> str:
        """By display name. Matches every source, so prefer `operator_card_by_source`."""
        return f'[data-test="operator-{display_name}"]'

    @staticmethod
    def operator_card_by_source(catalog_source: str, package: str = OSP_PACKAGE) -> str:
        """The single card belonging to one catalog source.

        `catalog_source` comes straight from config: redhat-operators for prod,
        custom-operators for stage and pre-stage.
        """
        return f'[id="{package}-{catalog_source}-{SoftwareCatalogLocators.MARKETPLACE_NAMESPACE}"]'

    @staticmethod
    def operator_card_action(display_name: str) -> str:
        """The card is a div; only this inner button opens the detail panel."""
        return f'[data-test="operator-{display_name}"] button.pf-v6-c-card__clickable-action'

    @staticmethod
    def operator_card_action_by_source(catalog_source: str, package: str = OSP_PACKAGE) -> str:
        card = SoftwareCatalogLocators.operator_card_by_source(catalog_source, package)
        return f"{card} button.pf-v6-c-card__clickable-action"


class OperatorDetailPanelLocators:
    """The right-hand panel opened by clicking a catalog card."""

    PANEL = '[role="dialog"]'
    # One control serves as both the action and the install-state indicator: it reads
    # "Install" when the operator is absent and "Uninstall" once it is installed.
    CTA = '[data-test="catalog-details-modal-cta"]'
    CHANNEL_TOGGLE = '[data-test="operator-channel-select-toggle"]'
    VERSION_TOGGLE = '[data-test="operator-version-select-toggle"]'
    MENU_ITEM = ".pf-v6-c-menu__item"

    @staticmethod
    def menu_option(option_id: str) -> str:
        """Channel ids contain dots (`pipelines-1.24`), which a `#id` selector parses
        as a class. The attribute form is the only one that works."""
        return f'.pf-v6-c-menu__item[id="{option_id}"]'

    @staticmethod
    def menu_option_by_text(text: str) -> str:
        return f'.pf-v6-c-menu__item:has-text("{text}")'


class InstallOperatorLocators:
    """The subscribe form reached from the panel's Install button."""

    UPDATE_APPROVAL_AUTOMATIC = "#Automatic"
    UPDATE_APPROVAL_MANUAL = "#Manual"
    CONSOLE_PLUGIN_ENABLE = "#pipelines-console-plugin-enabled"
    CONSOLE_PLUGIN_DISABLE = "#pipelines-console-plugin-disabled"
    INSTALL_MODE_ALL_NAMESPACES = "#operator-install-mode-all-namespaces"
    INSTALL_BUTTON = '[data-test="install-operator"]'


class InstallResultLocators:
    """The page shown after submitting the subscribe form."""

    # Rendered as both a link and a button, so callers must scope to one.
    VIEW_OPERATOR = 'a:has-text("View Operator"), button:has-text("View Operator")'


class InstalledOperatorsLocators:
    """The Installed Operators list, used as the final confirmation."""

    OSP_ROW = 'tr:has-text("Red Hat OpenShift Pipelines")'
    OSP_LINK = 'a:has-text("Red Hat OpenShift Pipelines")'
    STATUS_SUCCEEDED = 'td:has-text("Succeeded")'
