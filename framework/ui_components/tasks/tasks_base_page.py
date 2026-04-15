from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TasksBasePageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector
from framework.ui_components.console_url_patterns import TASKS_URL


class TasksBasePage(BasePage):
    """
    Abstract base class for Tasks and TaskRuns pages.
    Contains shared UI elements and behaviors common to both tabs.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.base_locators = TasksBasePageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Tasks/TaskRuns page is currently displayed by checking URL and header visibility.
        Waits for the URL to match tasks/all-namespaces or tasks/ns/<namespace>, then checks if the
        Tasks header is visible.
        :return: bool: True if URL matches and Tasks header is visible.
        :raises AssertionError: With specific message if URL or header check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(TASKS_URL, self.base_locators.TASKS_HEADER, "Tasks page")

    async def search_by_name(self, search_text: str) -> bool:
        """
        Types text into the 'Search by name...' input field to filter resources.
        :param str search_text: The text to search for.
        :return: bool: True if fill succeeds.
        """
        return await self.fill_input(self.base_locators.SEARCH_INPUT, search_text)

    async def click_filter_button(self) -> bool:
        """
        Clicks the 'Filter' button to open the filter dropdown.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.FILTER_BUTTON)

    async def click_column_management(self) -> bool:
        """
        Clicks the 'Column management' button to customize visible columns.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.COLUMN_MANAGEMENT_BUTTON)

    async def click_clear_all_filters(self) -> bool:
        """
        Clicks the 'Clear all filters' button to reset all active filters.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.CLEAR_ALL_FILTERS_BUTTON)

    async def click_kebab_menu(self, index: int = 0) -> bool:
        """
        Clicks the kebab menu button for a specific row to open row actions.
        :param int index: The zero-based index of the row (0 for first row, 1 for second, etc.).
        :return: bool: True if click succeeds.
        """
        locator = f"{self.base_locators.KEBAB_MENU_BUTTON} >> nth={index}"
        return await self.click_element(locator)

    async def click_create_button(self) -> bool:
        """
        Clicks the 'Create' button to open the create dropdown menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.CREATE_BUTTON)

    async def click_create_task_menu_item(self) -> bool:
        """
        Clicks the 'Task' menu item from the Create dropdown.
        Assumes the Create dropdown is already open.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.CREATE_TASK_MENU_ITEM)

    async def click_create_task_run_menu_item(self) -> bool:
        """
        Clicks the 'TaskRun' menu item from the Create dropdown.
        Assumes the Create dropdown is already open.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.CREATE_TASK_RUN_MENU_ITEM)

    async def click_create_task(self) -> bool:
        """
        Opens the Create dropdown and clicks 'Task' to navigate to the Create Task form.
        :return: bool: True if both clicks succeed.
        """
        return await self.click_element(self.base_locators.CREATE_BUTTON) and await self.click_element(
            self.base_locators.CREATE_TASK_MENU_ITEM
        )

    async def click_create_task_run(self) -> bool:
        """
        Opens the Create dropdown and clicks 'TaskRun' to navigate to the Create TaskRun form.
        :return: bool: True if both clicks succeed.
        """
        return await self.click_element(self.base_locators.CREATE_BUTTON) and await self.click_element(
            self.base_locators.CREATE_TASK_RUN_MENU_ITEM
        )

    async def navigate_to_tasks_tab(self) -> bool:
        """
        Navigates to the Tasks tab by clicking on the Tasks tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.base_locators.TASKS_TAB)

    async def navigate_to_task_runs_tab(self) -> bool:
        """
        Navigates to the TaskRuns tab by clicking on the TaskRuns tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.base_locators.TASK_RUNS_TAB)

    async def verify_data_load(self, tab_name: str = "Tasks page") -> bool:
        """
        Verifies that data has finished loading on the Tasks or TaskRuns tab.
        First checks for 'no data' state, which is a valid state. If no data element is visible,
        continues with normal data load verification.
        :param str tab_name: Tab name for error messages (e.g., "Tasks tab", "TaskRuns tab").
        :return: bool: True if data element becomes visible within the timeout, or if no data element is visible.
        :raises AssertionError: If data does not load within the timeout.
        """
        return await self._verify_data_load(self.base_locators.DATA_GRID, tab_name, self.base_locators.NO_DATA_MESSAGE)
