from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelineruns import CreatePipelineRunPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.monaco_editor import MonacoEditor
from framework.ui_components.commons.project_selector import ProjectSelector


class CreatePipelineRunPage(BasePage):
    """Page object for the Create PipelineRun YAML editor page."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = CreatePipelineRunPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)
        self.monaco_editor = MonacoEditor(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Create PipelineRun page is currently displayed by checking URL and header visibility.
        Waits for the URL to contain 'tekton.dev~v1~PipelineRun/~new', then checks if the Create PipelineRun
        header is visible.
        :return: bool: True if URL matches and Create PipelineRun header is visible.
        :raises AssertionError: With specific message if URL or header check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self.wait_for_url_to_contain("tekton.dev~v1~PipelineRun/~new") and await self.is_visible(
            self.locators.CREATE_PIPELINE_RUN_HEADER
        )

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
        Clicks the 'Hide sidebar' toolbar button to show/hide the schema sidebar.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TOGGLE_SIDEBAR_BUTTON)

    async def click_shortcuts(self) -> bool:
        """
        Clicks the 'Shortcuts' button to display keyboard shortcuts.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SHORTCUTS_BUTTON)

    async def click_create(self) -> bool:
        """
        Clicks the 'Create' button to submit the YAML and create the PipelineRun resource.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CREATE_BUTTON)

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

    async def click_close_sidebar(self) -> bool:
        """
        Clicks the 'Close' button on the schema sidebar to close it.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CLOSE_SIDEBAR_BUTTON)

    async def is_schema_sidebar_visible(self) -> bool:
        """
        Checks whether the schema sidebar (with 'PipelineRun' heading) is visible.
        :return: bool: True if the sidebar is visible, False otherwise.
        """
        return await self.is_visible(self.locators.SCHEMA_SIDEBAR_HEADING)
