from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import PipelineYamlPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.actions_menu import ActionsMenu
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.monaco_editor import MonacoEditor
from framework.ui_components.commons.project_selector import ProjectSelector
from framework.ui_components.console_url_patterns import PIPELINE_YAML_URL


class PipelineYamlPage(BasePage):
    """Page object for the Pipeline YAML editor tab."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = PipelineYamlPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)
        self.actions_menu = ActionsMenu(page, config)
        # Compose MonacoEditor component for editor interactions
        self.monaco_editor = MonacoEditor(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Pipeline YAML tab is currently displayed by checking URL and
        YAML editor visibility.
        :return: bool: True if URL matches and YAML editor is visible.
        :raises AssertionError: With specific message if URL or editor check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(PIPELINE_YAML_URL, self.locators.YAML_EDITOR, "Pipeline YAML page")

    async def get_pipeline_name(self) -> str:
        """
        Returns the pipeline name displayed in the h1 heading.
        :return: str: The text content of the pipeline name heading.
        """
        return await self.page.locator(self.locators.PIPELINE_NAME_HEADING).inner_text()

    async def navigate_to_details_tab(self) -> bool:
        """
        Switches to the Details tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.DETAILS_TAB)

    async def navigate_to_yaml_tab(self) -> bool:
        """
        Switches to the YAML tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.YAML_TAB)

    async def navigate_to_parameters_tab(self) -> bool:
        """
        Switches to the Parameters tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.PARAMETERS_TAB)

    async def navigate_to_metrics_tab(self) -> bool:
        """
        Switches to the Metrics tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.METRICS_TAB)

    async def navigate_to_pipelineruns_tab(self) -> bool:
        """
        Switches to the PipelineRuns tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.PIPELINERUNS_TAB)

    async def click_breadcrumb_pipelines(self) -> bool:
        """
        Clicks the 'Pipelines' breadcrumb link to navigate back to the Pipelines list page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.BREADCRUMB_PIPELINES_LINK)

    async def is_yaml_editor_visible(self) -> bool:
        """
        Checks whether the Monaco YAML editor is visible on the page.
        :return: bool: True if the editor is visible, False otherwise.
        """
        return await self.is_visible(self.locators.YAML_EDITOR)

    async def click_copy_code(self) -> bool:
        """
        Clicks the 'Copy code to clipboard' toolbar button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.COPY_CODE_BUTTON)

    async def click_editor_settings(self) -> bool:
        """
        Clicks the 'Editor settings' toolbar button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDITOR_SETTINGS_BUTTON)

    async def click_toggle_fullscreen(self) -> bool:
        """
        Clicks the 'Toggle fullscreen mode' toolbar button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TOGGLE_FULLSCREEN_BUTTON)

    async def click_toggle_sidebar(self) -> bool:
        """
        Clicks the sidebar toggle button to show/hide the schema sidebar.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TOGGLE_SIDEBAR_BUTTON)

    async def click_shortcuts(self) -> bool:
        """
        Clicks the 'Shortcuts' button to display keyboard shortcuts.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SHORTCUTS_BUTTON)

    async def click_save(self) -> bool:
        """
        Clicks the 'Save' button to save the YAML changes.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SAVE_BUTTON)

    async def click_reload(self) -> bool:
        """
        Clicks the 'Reload' button to discard local edits and reload the YAML from the server.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.RELOAD_BUTTON)

    async def click_cancel(self) -> bool:
        """
        Clicks the 'Cancel' button to discard changes and navigate back.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CANCEL_BUTTON)

    async def click_download(self) -> bool:
        """
        Clicks the 'Download' button to download the current YAML content as a file.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DOWNLOAD_BUTTON)
