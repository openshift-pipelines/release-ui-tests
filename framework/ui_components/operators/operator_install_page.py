"""Install an operator through the OpenShift 4.22 Software Catalog UI.

The flow: Ecosystem -> Software Catalog -> filter by keyword -> open the card ->
choose channel (and version, if pinned) -> Install -> set update approval and console
plugin -> Install -> wait for "View Operator" -> confirm in Installed Operators.
"""

import logging

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from framework.config.config import Config
from framework.locators.operators import (
    InstalledOperatorsLocators,
    InstallOperatorLocators,
    InstallResultLocators,
    OperatorDetailPanelLocators,
    SoftwareCatalogLocators,
    SoftwareCatalogNavLocators,
)
from framework.ui_components.base_page import BasePage

logger = logging.getLogger(__name__)

OSP_DISPLAY_NAME = "Red Hat OpenShift Pipelines"

# Install is asynchronous: OLM has to resolve the subscription, pull the bundle and
# report the CSV before the console confirms.
INSTALL_TIMEOUT_MS = 600000
CATALOG_LOAD_TIMEOUT_MS = 120000
# The subscribe form's radio groups appear after its Install button does.
FORM_CONTROL_TIMEOUT_MS = 60000


class OperatorInstallPage(BasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)

    async def _expand_ecosystem(self) -> None:
        """Open the Ecosystem nav section.

        Its children stay in the DOM while collapsed but are not visible, so clicking
        one without expanding first times out on visibility rather than failing to
        find it.
        """
        ecosystem = self.page.locator(SoftwareCatalogNavLocators.ECOSYSTEM_BUTTON).first
        await ecosystem.wait_for(state="visible", timeout=60000)
        if await ecosystem.get_attribute("aria-expanded") == "false":
            await ecosystem.click()
            await self.page.wait_for_timeout(2000)

    async def navigate_to_software_catalog(self) -> bool:
        """Expand Ecosystem if collapsed, then open Software Catalog."""
        logger.info("[OSP UI] Opening Ecosystem > Software Catalog...")
        await self._expand_ecosystem()
        await self.page.locator(SoftwareCatalogNavLocators.SOFTWARE_CATALOG_LINK).first.click()
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.locator(SoftwareCatalogLocators.KEYWORD_FILTER).wait_for(
            state="visible", timeout=CATALOG_LOAD_TIMEOUT_MS
        )
        return True

    async def search_operator(self, keyword: str = OSP_DISPLAY_NAME) -> bool:
        logger.info("[OSP UI] Filtering catalog by '%s'...", keyword)
        await self.page.locator(SoftwareCatalogLocators.KEYWORD_FILTER).fill(keyword)
        await self.page.locator(SoftwareCatalogLocators.operator_card(keyword)).first.wait_for(
            state="visible", timeout=60000
        )
        return True

    async def open_operator_card(self, catalog_source: str, display_name: str = OSP_DISPLAY_NAME) -> bool:
        """Open the card belonging to `catalog_source`.

        On a non-prod environment the CLI has already created a custom CatalogSource,
        so the keyword matches two cards with the same display name - one provided by
        Red Hat, one by Custom Operators. Selecting by display name alone would pick
        whichever rendered first; the card id carries the source, so use that.
        """
        matches = await self.page.locator(SoftwareCatalogLocators.operator_card(display_name)).count()
        logger.info("[OSP UI] '%s' matched %d card(s); selecting source '%s'.", display_name, matches, catalog_source)

        card_action = SoftwareCatalogLocators.operator_card_action_by_source(catalog_source)
        if not await self.exists(card_action, timeout=30000):
            raise AssertionError(
                f"No catalog card for source '{catalog_source}'. The CatalogSource may not be ready yet, "
                f"or its package name differs from '{SoftwareCatalogLocators._OSP_PACKAGE}'."
            )
        await self.page.locator(card_action).first.click()
        await self.page.locator(OperatorDetailPanelLocators.CTA).first.wait_for(state="visible", timeout=60000)
        return True

    async def is_operator_installed(self) -> bool:
        """True when the panel's action reads "Uninstall", which only happens once installed."""
        cta_text = (await self.page.locator(OperatorDetailPanelLocators.CTA).first.inner_text()).strip()
        logger.info("[OSP UI] Panel action reads '%s'.", cta_text)
        return cta_text.lower() == "uninstall"

    async def select_channel(self, channel: str) -> bool:
        logger.info("[OSP UI] Selecting channel '%s'...", channel)
        await self.page.locator(OperatorDetailPanelLocators.CHANNEL_TOGGLE).click()
        await self.page.locator(OperatorDetailPanelLocators.MENU_ITEM).first.wait_for(state="visible", timeout=30000)
        await self.page.locator(OperatorDetailPanelLocators.menu_option(channel)).first.click()
        await self.page.wait_for_timeout(2000)
        return True

    async def select_version(self, version: str) -> bool:
        logger.info("[OSP UI] Pinning version '%s'...", version)
        await self.page.locator(OperatorDetailPanelLocators.VERSION_TOGGLE).click()
        await self.page.locator(OperatorDetailPanelLocators.MENU_ITEM).first.wait_for(state="visible", timeout=30000)
        await self.page.locator(OperatorDetailPanelLocators.menu_option_by_text(version)).first.click()
        await self.page.wait_for_timeout(2000)
        return True

    async def click_install_on_panel(self) -> bool:
        logger.info("[OSP UI] Clicking Install on the detail panel...")
        await self.page.locator(OperatorDetailPanelLocators.CTA).first.click()
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.locator(InstallOperatorLocators.INSTALL_BUTTON).wait_for(state="visible", timeout=60000)
        # The Install button is not proof the form finished rendering; the approval
        # radios are the last group to appear and the ones we are about to set.
        await self.page.locator(InstallOperatorLocators.UPDATE_APPROVAL_AUTOMATIC).wait_for(
            state="attached", timeout=FORM_CONTROL_TIMEOUT_MS
        )
        return True

    async def _ensure_selected(self, locator: str, label: str) -> bool:
        """Select a radio only when it is not already the active choice.

        The radio groups render after the Install button does, so an immediate
        `count()` reports them missing and the setting is silently skipped. Wait for
        the control before concluding it is absent.
        """
        option = self.page.locator(locator)
        try:
            await option.wait_for(state="attached", timeout=FORM_CONTROL_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            logger.warning("[OSP UI] %s option never rendered (%s).", label, locator)
            return False
        if await option.is_checked():
            logger.info("[OSP UI] %s already selected.", label)
            return True
        await option.click()
        logger.info("[OSP UI] Selected %s.", label)
        return True

    async def configure_subscription(self) -> bool:
        """Select automatic updates and enable the console plugin.

        The UI path always uses Automatic, unlike the CLI path which picks Manual for
        nightly and pinned installs. Automatic means OLM creates the CSV on its own,
        so no InstallPlan approval step is needed afterwards.
        """
        await self._ensure_selected(InstallOperatorLocators.UPDATE_APPROVAL_AUTOMATIC, "Update approval 'Automatic'")
        await self._ensure_selected(InstallOperatorLocators.CONSOLE_PLUGIN_ENABLE, "Console plugin 'Enable'")
        return True

    async def click_install(self) -> bool:
        logger.info("[OSP UI] Submitting the install...")
        await self.page.locator(InstallOperatorLocators.INSTALL_BUTTON).click()
        await self.page.wait_for_load_state("domcontentloaded")
        return True

    async def wait_for_install_success(self) -> bool:
        """The "View Operator" control appearing is the console's own success signal."""
        logger.info("[OSP UI] Waiting for 'View Operator' (up to %ds)...", INSTALL_TIMEOUT_MS // 1000)
        try:
            await self.page.locator(InstallResultLocators.VIEW_OPERATOR).first.wait_for(
                state="visible", timeout=INSTALL_TIMEOUT_MS
            )
        except PlaywrightTimeoutError:
            logger.error("[OSP UI] 'View Operator' never appeared - install did not complete.")
            return False
        logger.info("[OSP UI] 'View Operator' visible - install reported successful.")
        return True

    async def verify_in_installed_operators(self, display_name: str = OSP_DISPLAY_NAME) -> bool:
        """Second, independent check: the operator is listed under Installed Operators."""
        logger.info("[OSP UI] Confirming '%s' in Installed Operators...", display_name)
        # The install left us on a page where the nav section has collapsed again.
        await self._expand_ecosystem()
        await self.page.locator(SoftwareCatalogNavLocators.INSTALLED_OPERATORS_LINK).first.click()
        await self.page.wait_for_load_state("domcontentloaded")
        try:
            await self.page.locator(InstalledOperatorsLocators.OSP_ROW).first.wait_for(state="visible", timeout=120000)
        except PlaywrightTimeoutError:
            logger.error("[OSP UI] '%s' is not listed in Installed Operators.", display_name)
            return False
        logger.info("[OSP UI] '%s' is listed in Installed Operators.", display_name)
        return True

    async def install_operator(
        self,
        catalog_source: str,
        channel: str | None = None,
        version: str | None = None,
        nightly: bool = False,
    ) -> bool:
        """Run the whole flow, short-circuiting if the operator is already installed.

        A nightly build installs the channel head: its OPERATOR_VERSION is a
        channel-ish value like "5.0" that does not exist in the version dropdown, so
        pinning it would either fail or select the wrong build.
        """
        await self.navigate_to_software_catalog()
        await self.search_operator()
        await self.open_operator_card(catalog_source)

        if await self.is_operator_installed():
            logger.info("[OSP UI] Operator already installed; nothing to do.")
            return True

        if channel:
            await self.select_channel(channel)
        if nightly:
            logger.info("[OSP UI] Nightly build - installing channel head, not pinning a version.")
        elif version:
            await self.select_version(version)

        await self.click_install_on_panel()
        await self.configure_subscription()
        await self.click_install()

        if not await self.wait_for_install_success():
            return False
        return await self.verify_in_installed_operators()
