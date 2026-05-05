from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskRunYamlPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.monaco_editor import MonacoEditor
from framework.ui_components.commons.project_selector import ProjectSelector


class TaskRunYamlPage(BasePage):
    """Page object for the TaskRun YAML editor tab."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskRunYamlPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)
        # Compose MonacoEditor component for editor interactions
        self.monaco_editor = MonacoEditor(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the TaskRun YAML page is currently displayed.
        Checks if the URL contains the TaskRun resource path with /yaml and verifies YAML tab is active.

        :return: bool: True if on TaskRun YAML page
        """
        return await self.wait_for_url_to_contain("tekton.dev~v1~TaskRun") and await self.is_visible(
            self.locators.YAML_EDITOR
        )

    async def get_taskrun_name(self) -> str:
        """
        Extracts the TaskRun name from the page heading.

        :return: str: TaskRun name displayed in the heading
        """
        try:
            return await self.page.text_content(self.locators.TASKRUN_NAME_HEADING) or ""
        except Exception as e:
            self.logger.error(f"Failed to get TaskRun name: {e}")
            return ""

    async def click_breadcrumb_taskruns(self) -> bool:
        """
        Clicks the 'TaskRuns' link in the breadcrumb to navigate back to TaskRuns list.

        :return: bool: True if click succeeds
        """
        return await self.click_element(self.locators.BREADCRUMB_TASKRUNS_LINK)

    async def navigate_to_details_tab(self) -> bool:
        """
        Navigates to the Details tab.

        :return: bool: True if tab click succeeds
        """
        return await self.click_element(self.locators.DETAILS_TAB)

    async def navigate_to_yaml_tab(self) -> bool:
        """
        Navigates to the YAML tab.

        :return: bool: True if tab click succeeds
        """
        return await self.click_element(self.locators.YAML_TAB)

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
        Clicks the 'Save' button to save changes to the YAML.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SAVE_BUTTON)

    async def click_reload(self) -> bool:
        """
        Clicks the 'Reload' button to reload the YAML from the server.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.RELOAD_BUTTON)

    async def click_cancel(self) -> bool:
        """
        Clicks the 'Cancel' button to discard changes.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CANCEL_BUTTON)

    async def click_download(self) -> bool:
        """
        Clicks the 'Download' button to download the YAML as a file.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DOWNLOAD_BUTTON)

    async def is_yaml_editor_visible(self) -> bool:
        """
        Checks whether the Monaco YAML editor is visible on the page.
        :return: bool: True if the editor is visible, False otherwise.
        """
        return await self.is_visible(self.locators.YAML_EDITOR)
