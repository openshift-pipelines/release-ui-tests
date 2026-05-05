import logging

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import PipelineRunsPageLocators
from framework.ui_components.pipelines.pipelines_base_page import PipelinesBasePage


class PipelineRunsPage(PipelinesBasePage):
    """
    Page object for the PipelineRuns tab - listing PipelineRun resources.
    Inherits common functionality from PipelinesBasePage.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = PipelineRunsPageLocators()
        self.logger = logging.getLogger(__name__)

    async def click_name_column_header(self) -> bool:
        """
        Clicks the 'Name' column header to sort PipelineRuns by name.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAME_COLUMN_HEADER)

    async def click_vulnerabilities_column_header(self) -> bool:
        """
        Clicks the 'Vulnerabilities' column header to sort PipelineRuns by vulnerabilities.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.VULNERABILITIES_COLUMN_HEADER)

    async def click_status_column_header(self) -> bool:
        """
        Clicks the 'Status' column header to sort PipelineRuns by status.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.STATUS_COLUMN_HEADER)

    async def click_task_status_column_header(self) -> bool:
        """
        Clicks the 'Task status' column header to sort PipelineRuns by task status.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TASK_STATUS_COLUMN_HEADER)

    async def click_started_column_header(self) -> bool:
        """
        Clicks the 'Started' column header to sort PipelineRuns by start time.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.STARTED_COLUMN_HEADER)

    async def click_duration_column_header(self) -> bool:
        """
        Clicks the 'Duration' column header to sort PipelineRuns by duration.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DURATION_COLUMN_HEADER)

    async def click_view_logs(self, index: int = 0) -> bool:
        """
        Clicks the 'View logs' button for a specific PipelineRun row.
        :param int index: The zero-based index of the row (0 for first row, 1 for second, etc.).
        :return: bool: True if click succeeds.
        """
        locator = f"{self.locators.VIEW_LOGS_BUTTON} >> nth={index}"
        return await self.click_element(locator)

    async def verify_pipeline_runs_tab_data_load(self) -> bool:
        """
        Verifies that PipelineRun data has finished loading on the PipelineRuns tab.
        :return: bool: True if data loads successfully or "no data" message is shown.
        """
        return await self.verify_data_load(tab_name="PipelineRuns tab")

    async def verify_pipelinerun_in_list(self, pipelinerun_name: str) -> bool:
        """
        Verify that a PipelineRun with the given name appears in the PipelineRuns list.
        Supports partial name matching for generateName resources (e.g., "simple-pipelinerun-").
        :param str pipelinerun_name: Name or name prefix of the PipelineRun to verify
        :return: bool: True if PipelineRun row is visible
        """
        locator = self.locators.PIPELINERUN_ROW_BY_NAME.format(pipelinerun_name=pipelinerun_name)
        return await self.is_visible(locator, timeout=5000)

    async def verify_pipelinerun_not_in_list(self, pipelinerun_name: str) -> bool:
        """
        Verify that a PipelineRun with the given name does NOT appear in the PipelineRuns list.
        Supports partial name matching for generateName resources.
        :param str pipelinerun_name: Name or name prefix of the PipelineRun to verify absence
        :return: bool: True if PipelineRun row is NOT visible
        """
        locator = self.locators.PIPELINERUN_ROW_BY_NAME.format(pipelinerun_name=pipelinerun_name)
        # Return True if element is NOT visible (inverse of is_visible)
        is_present = await self.is_visible(locator, timeout=3000)
        return not is_present

    async def get_pipelinerun_status(self, pipelinerun_name: str) -> str:
        """
        Get the status of a PipelineRun from the PipelineRuns list.

        :param str pipelinerun_name: Name of the PipelineRun (may be partial prefix for generateName resources)
        :return: str: Status text (e.g., 'Succeeded', 'Failed', 'Running')
        :raises AssertionError: If PipelineRun row not found in list
        """
        try:
            # Find the row containing the pipelinerun name
            row_locator = self.locators.PIPELINERUN_ROW_BY_NAME.format(pipelinerun_name=pipelinerun_name)

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
            self.logger.warning(f"Status element not found for PipelineRun '{pipelinerun_name}'")
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get status for PipelineRun '{pipelinerun_name}': {e}")
            raise AssertionError(f"Could not retrieve status for PipelineRun '{pipelinerun_name}'")

    async def click_pipelinerun_row(self, pipelinerun_name: str) -> bool:
        """
        Click a PipelineRun row to navigate to its details page.
        :param str pipelinerun_name: Name or name prefix of the PipelineRun
        :return: bool: True if click succeeds
        """
        locator = self.locators.PIPELINERUN_ROW_BY_NAME.format(pipelinerun_name=pipelinerun_name)
        return await self.click_element(locator)

    async def click_pipelinerun_kebab_menu(self, pipelinerun_name: str) -> bool:
        """
        Click the kebab menu button for a specific PipelineRun row.
        :param str pipelinerun_name: Name or name prefix of the PipelineRun
        :return: bool: True if click succeeds
        """
        try:
            # Find the row containing the pipelinerun name
            row_locator = self.locators.PIPELINERUN_ROW_BY_NAME.format(pipelinerun_name=pipelinerun_name)

            # Within that row, find and click the kebab menu button
            kebab_in_row = f"{row_locator} >> {self.base_locators.KEBAB_MENU_BUTTON}"
            return await self.click_element(kebab_in_row)
        except Exception as e:
            self.logger.error(f"Failed to click kebab menu for PipelineRun '{pipelinerun_name}': {e}")
            return False

    async def click_delete_pipelinerun_menu_item(self) -> bool:
        """
        Click 'Delete PipelineRun' menu item from the kebab menu dropdown.
        Assumes the kebab menu is already open.

        :return: bool: True if click succeeds
        """
        return await self.click_element(self.locators.DELETE_PIPELINERUN_MENU_ITEM)
