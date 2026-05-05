from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import PipelinesPageLocators
from framework.ui_components.pipelines.pipelines_base_page import PipelinesBasePage


class PipelinesPage(PipelinesBasePage):
    """
    Page object for the Pipelines tab - listing Pipeline resources.
    Inherits common functionality from PipelinesBasePage.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = PipelinesPageLocators()

    async def click_name_column_header(self) -> bool:
        """
        Clicks the 'Name' column header to sort Pipelines by name.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAME_COLUMN_HEADER)

    async def click_last_run_column_header(self) -> bool:
        """
        Clicks the 'Last run' column header to sort Pipelines by last run.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.LAST_RUN_COLUMN_HEADER)

    async def click_task_status_column_header(self) -> bool:
        """
        Clicks the 'Task status' column header to sort Pipelines by task status.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TASK_STATUS_COLUMN_HEADER)

    async def click_last_run_status_column_header(self) -> bool:
        """
        Clicks the 'Last run status' column header to sort Pipelines by last run status.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.LAST_RUN_STATUS_COLUMN_HEADER)

    async def click_last_run_time_column_header(self) -> bool:
        """
        Clicks the 'Last run time' column header to sort Pipelines by last run time.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.LAST_RUN_TIME_COLUMN_HEADER)

    async def click_view_logs(self, index: int = 0) -> bool:
        """
        Clicks the 'View logs' button for a specific Pipeline row.
        :param int index: The zero-based index of the row (0 for first row, 1 for second, etc.).
        :return: bool: True if click succeeds.
        """
        locator = f"{self.locators.VIEW_LOGS_BUTTON} >> nth={index}"
        return await self.click_element(locator)

    async def click_start_menu_item(self) -> bool:
        """
        Clicks the 'Start' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.START_MENU_ITEM)

    async def click_start_last_run_menu_item(self) -> bool:
        """
        Clicks the 'Start last run' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.START_LAST_RUN_MENU_ITEM)

    async def click_add_trigger_menu_item(self) -> bool:
        """
        Clicks the 'Add Trigger' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.ADD_TRIGGER_MENU_ITEM)

    async def click_remove_trigger_menu_item(self) -> bool:
        """
        Clicks the 'Remove Trigger' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.REMOVE_TRIGGER_MENU_ITEM)

    async def click_edit_labels_menu_item(self) -> bool:
        """
        Clicks the 'Edit labels' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDIT_LABELS_MENU_ITEM)

    async def click_edit_annotations_menu_item(self) -> bool:
        """
        Clicks the 'Edit annotations' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDIT_ANNOTATIONS_MENU_ITEM)

    async def click_edit_pipeline_menu_item(self) -> bool:
        """
        Clicks the 'Edit Pipeline' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDIT_PIPELINE_MENU_ITEM)

    async def click_delete_pipeline_menu_item(self) -> bool:
        """
        Clicks the 'Delete Pipeline' menu item from the kebab menu.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DELETE_PIPELINE_MENU_ITEM)

    async def verify_pipelines_tab_data_load(self) -> bool:
        """
        Verifies that Pipeline data has finished loading on the Pipelines tab.
        :return: bool: True if data loads successfully or "no data" message is shown.
        """
        return await self.verify_data_load(tab_name="Pipelines tab")

    async def click_create_pipeline_menu_item(self) -> bool:
        """
        Click 'Pipeline' menu item from Create dropdown.
        Assumes Create dropdown is already open.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.base_locators.CREATE_PIPELINE_MENU_ITEM)

    async def verify_pipeline_in_list(self, pipeline_name: str) -> bool:
        """
        Verify that a pipeline with the given name appears in the pipelines list.
        :param str pipeline_name: Name of the pipeline to verify
        :return: bool: True if pipeline row is visible
        """
        locator = self.locators.PIPELINE_ROW_BY_NAME.format(pipeline_name=pipeline_name)
        return await self.is_visible(locator, timeout=5000)

    async def verify_pipeline_not_in_list(self, pipeline_name: str) -> bool:
        """
        Verify that a pipeline with the given name does NOT appear in the pipelines list.
        :param str pipeline_name: Name of the pipeline to verify absence
        :return: bool: True if pipeline row is NOT visible
        """
        locator = self.locators.PIPELINE_ROW_BY_NAME.format(pipeline_name=pipeline_name)
        return not await self.is_visible(locator, timeout=5000)

    async def click_pipeline_kebab_menu(self, pipeline_name: str) -> bool:
        """
        Click the kebab menu for a specific pipeline row.
        :param str pipeline_name: Name of the pipeline
        :return: bool: True if kebab menu click succeeds
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            # Find the row containing the pipeline name
            row_locator = self.locators.PIPELINE_ROW_BY_NAME.format(pipeline_name=pipeline_name)

            # Within that row, find and click the kebab menu button
            kebab_in_row = f"{row_locator} >> {self.base_locators.KEBAB_MENU_BUTTON}"
            return await self.click_element(kebab_in_row)
        except Exception as e:
            logger.error(f"Failed to click kebab menu for pipeline '{pipeline_name}': {e}")
            return False
