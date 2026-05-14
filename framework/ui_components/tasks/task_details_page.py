import logging
import re
from typing import Dict

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskDetailsPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.actions_menu import ActionsMenu
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector
from framework.ui_components.console_url_patterns import TASK_DETAILS_URL


class TaskDetailsPage(BasePage):
    """Page object for the Task Details page (viewing a specific Task resource)."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskDetailsPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)
        self.actions_menu = ActionsMenu(page, config)
        self.logger = logging.getLogger(__name__)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Task Details page is currently displayed by checking URL and
        the Task details heading visibility.
        :return: bool: True if URL matches and Task details heading is visible.
        :raises AssertionError: With specific message if URL or heading check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(TASK_DETAILS_URL, self.locators.TASK_DETAILS_HEADING, "Task Details page")

    async def get_task_name(self) -> str:
        """
        Returns the task name displayed in the h1 heading.
        :return: str: The text content of the task name heading.
        """
        return await self.page.locator(self.locators.TASK_NAME_HEADING).inner_text()

    async def navigate_to_details_tab(self) -> bool:
        """
        Switches to the Details tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.DETAILS_TAB)

    async def navigate_to_yaml_tab(self) -> bool:
        """
        Switches to the YAML tab to view/edit the task YAML.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.YAML_TAB)

    async def click_breadcrumb_tasks(self) -> bool:
        """
        Clicks the 'Tasks' breadcrumb link to navigate back to the Tasks list page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.BREADCRUMB_TASKS_LINK)

    async def click_namespace_link(self) -> bool:
        """
        Clicks the namespace link in the details section to navigate to the namespace page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAMESPACE_LINK)

    async def click_edit_labels(self) -> bool:
        """
        Clicks the 'Edit' button next to Labels to open the labels editor.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDIT_LABELS_BUTTON)

    async def click_annotations(self) -> bool:
        """
        Clicks the annotations button to view/edit annotations.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.ANNOTATIONS_BUTTON)

    async def get_namespace(self) -> str:
        """
        Get the namespace name from the task details page.

        Uses inner_text() which automatically waits for element to be visible
        before retrieving text content.

        :return: str: Namespace name (e.g., 'ui-test')
        :raises AssertionError: If namespace value is missing
        :raises TimeoutError: If element is not visible within timeout
        """
        namespace_text = await self.page.inner_text(self.locators.NAMESPACE_VALUE)

        if not namespace_text or not namespace_text.strip():
            raise AssertionError("Namespace value is empty or missing in task details")

        return namespace_text.strip()

    async def get_labels(self) -> Dict[str, str]:
        """
        Get all labels from the task details page.

        Uses inner_text() which automatically waits for elements to be visible
        before retrieving text content.

        :return: Dict[str, str]: Dictionary of label key-value pairs (empty if no labels)
        :raises TimeoutError: If labels section is not visible within timeout
        """
        # Get all label badge elements
        label_elements = await self.page.locator(self.locators.LABEL_BADGE).all()
        labels = {}

        for element in label_elements:
            # inner_text() waits for element to be visible
            label_text = await element.inner_text()
            if label_text and "=" in label_text:
                key, value = label_text.split("=", 1)
                labels[key.strip()] = value.strip()
            elif label_text:
                # Label exists but doesn't have '=' separator - log warning
                self.logger.warning(f"Label has unexpected format (missing '='): '{label_text}'")

        return labels

    async def get_annotations_count(self) -> int:
        """
        Get the count of annotations from the annotations button text.

        Uses inner_text() which automatically waits for button to be visible
        before retrieving text content.

        :return: int: Number of annotations
        :raises AssertionError: If button text is missing or format is unexpected
        :raises TimeoutError: If button is not visible within timeout
        """
        button_text = await self.page.inner_text(self.locators.ANNOTATIONS_COUNT)

        if not button_text:
            raise AssertionError("Annotations button text is empty")

        # Button text format: "3 annotations" or "1 annotation"
        match = re.search(r"(\d+)\s+annotation", button_text)
        if not match:
            raise AssertionError(
                f"Annotations button text has unexpected format: '{button_text}'. Expected format: 'N annotation(s)'"
            )

        return int(match.group(1))
