import re

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskRunEventsPageLocators
from framework.ui_components.console_url_patterns import TASKRUN_EVENTS_URL
from framework.ui_components.taskruns.taskrun_base_page import TaskRunBasePage


class TaskRunEventsPage(TaskRunBasePage):
    """
    Page object for the TaskRun Events tab.
    Displays streaming Kubernetes events related to the TaskRun execution.
    Inherits common functionality from TaskRunBasePage.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskRunEventsPageLocators()

    async def verify_on_page(self) -> bool:
        """
        Verifies that the TaskRun Events page is currently displayed by checking URL.
        :return: bool: True if URL matches the pattern.
        :raises AssertionError: With specific message if URL check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(
            TASKRUN_EVENTS_URL, self.base_locators.TASKRUN_NAME_HEADING, "TaskRun Events page"
        )

    async def is_events_grid_visible(self) -> bool:
        """
        Checks if the events grid is visible on the page.
        :return: bool: True if events grid is visible.
        """
        return await self.is_visible(self.locators.EVENTS_GRID)

    async def get_events_count(self) -> int:
        """
        Retrieves the count of events from the "Showing X event" text.
        :return: int: Number of events displayed.
        :raises AssertionError: If count text is not found or has unexpected format.
        """
        count_text = await self.page.locator(self.locators.SHOWING_COUNT).inner_text()
        if not count_text:
            raise AssertionError("Events count text is empty")

        match = re.search(r"Showing\s+(\d+)\s+event", count_text)
        if not match:
            raise AssertionError(f"Unexpected events count format: '{count_text}'")

        return int(match.group(1))

    async def click_pause_streaming(self) -> bool:
        """
        Clicks the 'Pause event streaming' button to pause live event updates.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.PAUSE_STREAMING_BUTTON)

    async def is_streaming_active(self) -> bool:
        """
        Checks if the events streaming status indicator is visible.
        :return: bool: True if "Streaming events..." text is visible.
        """
        return await self.is_visible(self.locators.STREAMING_STATUS)

    async def get_event_rows(self) -> list:
        """
        Retrieves all event rows from the events grid.
        Useful for validation and counting events.
        :return: list: List of Playwright Locator objects for each event row.
        """
        return await self.page.locator(self.locators.EVENT_ROW).all()

    async def get_event_rows_count(self) -> int:
        """
        Counts the number of event rows in the events grid.
        :return: int: Number of event rows displayed.
        """
        rows = await self.get_event_rows()
        return len(rows)
