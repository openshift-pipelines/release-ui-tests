from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskRunDetailsPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector


class TaskRunDetailsPage(BasePage):
    """Page object for the TaskRun Details page."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskRunDetailsPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the TaskRun Details page is currently displayed.
        Checks if the URL contains the TaskRun resource path and verifies the page heading is visible.

        :return: bool: True if on TaskRun details page
        """
        return await self.wait_for_url_to_contain("tekton.dev~v1~TaskRun") and await self.is_visible(
            self.locators.TASKRUN_NAME_HEADING
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

    async def get_namespace(self) -> str:
        """
        Gets the namespace of the TaskRun from the namespace link.

        :return: str: Namespace name
        """
        try:
            namespace_text = await self.page.text_content(self.locators.NAMESPACE_LINK)
            return namespace_text.strip() if namespace_text else ""
        except Exception as e:
            self.logger.error(f"Failed to get namespace: {e}")
            return ""

    async def get_status(self) -> str:
        """
        Gets the status of the TaskRun.

        :return: str: Status value (e.g., "Succeeded", "Running", "Failed")
        """
        try:
            # Find the status value next to the status label
            status_element = f"{self.locators.STATUS_LABEL} + dd"
            status_text = await self.page.text_content(status_element)
            return status_text.strip() if status_text else ""
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return ""

    async def click_task_link(self) -> bool:
        """
        Clicks the Task link to navigate to the referenced Task details.

        :return: bool: True if click succeeds
        """
        return await self.click_element(self.locators.TASK_LINK)

    async def is_details_section_visible(self) -> bool:
        """
        Checks if the TaskRun details section is visible.

        :return: bool: True if details section is visible
        """
        return await self.is_visible(self.locators.TASKRUN_DETAILS_HEADING)
