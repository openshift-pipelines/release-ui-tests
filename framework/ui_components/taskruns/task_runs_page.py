import logging

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskRunsPageLocators
from framework.ui_components.tasks.tasks_base_page import TasksBasePage


class TaskRunsPage(TasksBasePage):
    """
    Page object for the TaskRuns tab - listing TaskRun resources.
    Inherits common functionality from TasksBasePage.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskRunsPageLocators()
        self.logger = logging.getLogger(__name__)

    async def click_name_column_header(self) -> bool:
        """
        Clicks the 'Name' column header to sort TaskRuns by name.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAME_COLUMN_HEADER)

    async def click_pipeline_column_header(self) -> bool:
        """
        Clicks the 'Pipeline' column header to sort TaskRuns by pipeline.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.PIPELINE_COLUMN_HEADER)

    async def click_task_column_header(self) -> bool:
        """
        Clicks the 'Task' column header to sort TaskRuns by task.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TASK_COLUMN_HEADER)

    async def click_pod_column_header(self) -> bool:
        """
        Clicks the 'Pod' column header to sort TaskRuns by pod.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.POD_COLUMN_HEADER)

    async def click_status_column_header(self) -> bool:
        """
        Clicks the 'Status' column header to sort TaskRuns by status.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.STATUS_COLUMN_HEADER)

    async def click_started_column_header(self) -> bool:
        """
        Clicks the 'Started' column header to sort TaskRuns by start time.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.STARTED_COLUMN_HEADER)

    async def verify_task_runs_tab_data_load(self) -> bool:
        """
        Verifies that TaskRun data has finished loading on the TaskRuns tab.
        :return: bool: True if data loads successfully or "no data" message is shown.
        """
        return await self.verify_data_load(tab_name="TaskRuns tab")

    async def verify_taskrun_in_list(self, taskrun_name: str) -> bool:
        """
        Verify that a TaskRun with the given name appears in the TaskRuns list.

        :param str taskrun_name: Name of the TaskRun to verify (can be partial name with generateName)
        :return: bool: True if TaskRun row is visible
        """
        locator = self.locators.TASKRUN_ROW_BY_NAME.format(taskrun_name=taskrun_name)
        return await self.is_visible(locator, timeout=5000)

    async def verify_taskrun_not_in_list(self, taskrun_name: str) -> bool:
        """
        Verify that a TaskRun with the given name does NOT appear in the TaskRuns list.

        :param str taskrun_name: Name of the TaskRun to verify absence
        :return: bool: True if TaskRun row is NOT visible
        """
        locator = self.locators.TASKRUN_ROW_BY_NAME.format(taskrun_name=taskrun_name)
        return not await self.is_visible(locator, timeout=5000)

    async def get_taskrun_status(self, taskrun_name: str) -> str:
        """
        Get the status of a TaskRun from the TaskRuns list.

        :param str taskrun_name: Name of the TaskRun (may be partial prefix for generateName resources)
        :return: str: Status text (e.g., 'Succeeded', 'Failed', 'Running')
        :raises AssertionError: If TaskRun row not found in list
        """
        try:
            # Find the row containing the taskrun name
            row_locator = self.locators.TASKRUN_ROW_BY_NAME.format(taskrun_name=taskrun_name)

            # Wait for the row to be visible
            await self.page.wait_for_selector(row_locator, timeout=5000)

            # Within that row, find the status badge
            # Try common status locator patterns used in OpenShift Console
            status_locator = f"{row_locator} >> [data-test='status-text']"

            # Get the status text
            status_element = await self.page.query_selector(status_locator)
            if status_element:
                status_text = await status_element.text_content()
                return status_text.strip()

            # Fallback: try PatternFly label content pattern
            status_locator_alt = f"{row_locator} >> .pf-c-label__content"
            status_element_alt = await self.page.query_selector(status_locator_alt)
            if status_element_alt:
                status_text = await status_element_alt.text_content()
                return status_text.strip()

            # If no status found, return empty string
            self.logger.warning(f"Status element not found for TaskRun '{taskrun_name}'")
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get status for TaskRun '{taskrun_name}': {e}")
            raise AssertionError(f"Could not retrieve status for TaskRun '{taskrun_name}'")

    async def click_taskrun_kebab_menu(self, taskrun_name: str) -> bool:
        """
        Click the kebab menu for a specific TaskRun row.

        :param str taskrun_name: Name of the TaskRun
        :return: bool: True if kebab menu click succeeds
        """
        try:
            # Find the row containing the taskrun name
            row_locator = self.locators.TASKRUN_ROW_BY_NAME.format(taskrun_name=taskrun_name)

            # Within that row, find and click the kebab menu button
            kebab_in_row = f"{row_locator} >> {self.base_locators.KEBAB_MENU_BUTTON}"
            return await self.click_element(kebab_in_row)
        except Exception as e:
            self.logger.error(f"Failed to click kebab menu for TaskRun '{taskrun_name}': {e}")
            return False

    async def click_delete_taskrun_menu_item(self) -> bool:
        """
        Click 'Delete TaskRun' menu item from the kebab menu dropdown.
        Assumes the kebab menu is already open.

        :return: bool: True if click succeeds
        """
        return await self.click_element(self.locators.DELETE_TASKRUN_MENU_ITEM)
