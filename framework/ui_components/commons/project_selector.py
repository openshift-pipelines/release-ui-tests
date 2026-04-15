from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.commons import ProjectSelectorLocators
from framework.ui_components.base_page import BasePage


class ProjectSelector(BasePage):
    """Shared component for the project selector dropdown that appears across pages."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = ProjectSelectorLocators()

    async def click_project_selector(self) -> bool:
        """
        Clicks the project selector dropdown button to open the project list.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.PROJECT_SELECTOR_BUTTON)

    async def is_project_selector_visible(self) -> bool:
        """
        Checks whether the project selector button is visible on the page.
        :return: bool: True if the project selector is visible, False otherwise.
        """
        return await self.is_visible(self.locators.PROJECT_SELECTOR_BUTTON)

    async def select_project(self, project_name: str) -> bool:
        """
        Selects a specific project from the project selector dropdown.

        :param str project_name: Name of the project to select
        :return: bool: True if project selected successfully, False otherwise
        """
        try:
            # Click project selector to open dropdown
            if not await self.click_project_selector():
                return False

            # Wait for dropdown to appear
            await self.page.wait_for_timeout(500)

            # Click the project menu item
            project_locator = self.locators.PROJECT_MENU_ITEM.format(project_name=project_name)
            if not await self.click_element(project_locator):
                return False

            # Wait for page to reload with new project context
            await self.page.wait_for_timeout(1000)

            return True
        except Exception as e:
            self.logger.error(f"Failed to select project '{project_name}': {e}")
            return False

    async def get_current_project(self) -> str:
        """
        Gets the current selected project name from the project selector button text.

        :return: str: Current project name (empty string if selector not visible or error)
        """
        try:
            button_text = await self.page.text_content(self.locators.PROJECT_SELECTOR_BUTTON)
            # Button text is like "Project: ui-test" - extract project name
            if button_text and "Project:" in button_text:
                return button_text.replace("Project:", "").strip()
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get current project: {e}")
            return ""
