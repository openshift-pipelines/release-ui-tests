from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskRunBasePageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector


class TaskRunBasePage(BasePage):
    """
    Abstract base class for TaskRun Details, YAML, Logs, and Events pages.
    Contains shared UI elements and behaviors common to all TaskRun tabs.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.base_locators = TaskRunBasePageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)

    async def get_taskrun_name(self) -> str:
        """
        Returns the TaskRun name displayed in the h1 heading.
        :return: str: The text content of the TaskRun name heading.
        """
        return await self.page.locator(self.base_locators.TASKRUN_NAME_HEADING).inner_text()

    async def click_breadcrumb_taskruns(self) -> bool:
        """
        Clicks the 'TaskRuns' breadcrumb link to navigate back to the TaskRuns list page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.BREADCRUMB_TASKRUNS_LINK)

    # Tab navigation methods (shared across all TaskRun pages)
    async def navigate_to_details_tab(self) -> bool:
        """
        Switches to the Details tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.base_locators.DETAILS_TAB)

    async def navigate_to_yaml_tab(self) -> bool:
        """
        Switches to the YAML tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.base_locators.YAML_TAB)

    async def navigate_to_logs_tab(self) -> bool:
        """
        Switches to the Logs tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.base_locators.LOGS_TAB)

    async def navigate_to_events_tab(self) -> bool:
        """
        Switches to the Events tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.base_locators.EVENTS_TAB)
