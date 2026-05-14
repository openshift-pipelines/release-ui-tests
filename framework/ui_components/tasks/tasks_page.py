from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TasksPageLocators
from framework.ui_components.tasks.tasks_base_page import TasksBasePage


class TasksPage(TasksBasePage):
    """
    Page object for the Tasks tab - listing Task resources.
    Inherits common functionality from TasksBasePage.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TasksPageLocators()

    async def click_name_column_header(self) -> bool:
        """
        Clicks the 'Name' column header to sort Tasks by name.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAME_COLUMN_HEADER)

    async def click_namespace_column_header(self) -> bool:
        """
        Clicks the 'Namespace' column header to sort Tasks by namespace.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAMESPACE_COLUMN_HEADER)

    async def click_created_column_header(self) -> bool:
        """
        Clicks the 'Created' column header to sort Tasks by creation date.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CREATED_COLUMN_HEADER)

    async def verify_tasks_tab_data_load(self) -> bool:
        """
        Verifies that Task data has finished loading on the Tasks tab.
        :return: bool: True if data loads successfully or "no data" message is shown.
        """
        return await self.verify_data_load(tab_name="Tasks tab")

    async def click_task_kebab_menu(self, task_name: str) -> bool:
        """
        Click the kebab menu button for a specific task row.

        :param str task_name: Name of the task
        :return: bool: True if kebab menu clicked successfully
        """
        # Locate the specific task row and click its kebab menu
        task_row_locator = self.locators.TASK_ROW_BY_NAME.format(task_name=task_name)
        kebab_button = f"{task_row_locator} {self.base_locators.KEBAB_MENU_BUTTON}"
        return await self.click_element(kebab_button)

    async def click_edit_task_menu_item(self) -> bool:
        """
        Click the 'Edit Task' menu item from the kebab menu dropdown.

        :return: bool: True if menu item clicked successfully
        """
        return await self.click_element(self.base_locators.EDIT_TASK_MENU_ITEM)

    async def click_delete_task_menu_item(self) -> bool:
        """
        Click the 'Delete Task' menu item from the kebab menu dropdown.

        :return: bool: True if menu item clicked successfully
        """
        return await self.click_element(self.base_locators.DELETE_TASK_MENU_ITEM)

    async def verify_task_in_list(self, task_name: str) -> bool:
        """
        Verify that a task with the given name appears in the task list.

        :param str task_name: Name of the task to verify
        :return: bool: True if task row is visible
        """
        locator = self.locators.TASK_ROW_BY_NAME.format(task_name=task_name)
        return await self.is_visible(locator, timeout=self.config.timeout_ms)

    async def verify_task_not_in_list(self, task_name: str) -> bool:
        """
        Verify that a task with the given name does NOT appear in the task list.

        :param str task_name: Name of the task to verify absence
        :return: bool: True if task row is NOT visible (disappeared)
        """
        locator = self.locators.TASK_ROW_BY_NAME.format(task_name=task_name)
        # Wait for the element to disappear
        try:
            await self.page.wait_for_selector(locator, state="hidden", timeout=self.config.timeout_ms)
            return True
        except Exception:
            # If element is still visible or wait times out, verification failed
            return False

    async def click_task_name(self, task_name: str) -> bool:
        """
        Click on the task name link to navigate to the task details page.

        :param str task_name: Name of the task to click
        :return: bool: True if task name link clicked successfully
        """
        locator = self.locators.TASK_NAME_LINK.format(task_name=task_name)
        return await self.click_element(locator)
