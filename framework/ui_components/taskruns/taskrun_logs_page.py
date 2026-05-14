from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskRunLogsPageLocators
from framework.ui_components.console_url_patterns import TASKRUN_LOGS_URL
from framework.ui_components.taskruns.taskrun_base_page import TaskRunBasePage


class TaskRunLogsPage(TaskRunBasePage):
    """
    Page object for the TaskRun Logs tab.
    Displays logs from all steps in the TaskRun execution with navigation and download options.
    Inherits common functionality from TaskRunBasePage.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskRunLogsPageLocators()

    async def verify_on_page(self) -> bool:
        """
        Verifies that the TaskRun Logs page is currently displayed by checking URL.
        :return: bool: True if URL matches the pattern.
        :raises AssertionError: With specific message if URL check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(
            TASKRUN_LOGS_URL, self.base_locators.TASKRUN_NAME_HEADING, "TaskRun Logs page"
        )

    # Logs page specific methods
    async def click_step_link(self, step_name: str) -> bool:
        """
        Clicks a step link in the navigation to view that step's logs.
        :param str step_name: The name of the step to view logs for (e.g., "build", "test").
        :return: bool: True if click succeeds.
        """
        locator = f'{self.locators.STEP_LINK}:has-text("{step_name}")'
        return await self.click_element(locator)

    async def get_available_steps(self) -> list[str]:
        """
        Returns a list of step names available in the logs navigation.
        :return: list[str]: List of step names from the TaskRun execution.
        """
        step_links = await self.page.locator(self.locators.STEP_LINK).all()
        step_names = []
        for link in step_links:
            text = await link.inner_text()
            # Remove any whitespace and extract just the step name
            step_name = text.strip()
            if step_name:
                step_names.append(step_name)
        return step_names

    async def click_download(self) -> bool:
        """
        Clicks the 'Download' button to download the current step's logs.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DOWNLOAD_BUTTON)

    async def click_download_all(self) -> bool:
        """
        Clicks the 'Download all task logs' button to download logs from all steps.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DOWNLOAD_ALL_BUTTON)

    async def click_expand(self) -> bool:
        """
        Clicks the 'Expand' button to expand/collapse the logs view.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EXPAND_BUTTON)

    async def is_logs_container_visible(self) -> bool:
        """
        Checks if the logs content container is visible.
        :return: bool: True if logs container is visible.
        """
        return await self.is_visible(self.locators.LOGS_CONTAINER)

    async def is_step_navigation_visible(self) -> bool:
        """
        Checks if the step navigation sidebar is visible.
        :return: bool: True if step navigation is visible.
        """
        return await self.is_visible(self.locators.STEP_NAVIGATION)

    async def get_logs_content(self) -> str:
        """
        Retrieves the text content from the logs container.
        Useful for verifying specific step output appears in logs.
        :return: str: The text content of the logs container.
        """
        return await self.page.locator(self.locators.LOGS_CONTAINER).inner_text()
