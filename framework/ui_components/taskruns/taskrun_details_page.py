import logging
import re
from typing import Dict

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskRunDetailsPageLocators
from framework.ui_components.taskruns.taskrun_base_page import TaskRunBasePage


class TaskRunDetailsPage(TaskRunBasePage):
    """Page object for the TaskRun Details page. Inherits common functionality from TaskRunBasePage."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskRunDetailsPageLocators()
        self.logger = logging.getLogger(__name__)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the TaskRun Details page is currently displayed.
        Checks if the URL contains the TaskRun resource path and verifies the page heading is visible.

        :return: bool: True if on TaskRun details page
        """
        return await self.wait_for_url_to_contain("tekton.dev~v1~TaskRun") and await self.is_visible(
            self.base_locators.TASKRUN_NAME_HEADING
        )

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

    async def get_labels(self) -> Dict[str, str]:
        """
        Get all labels from the TaskRun details page.
        Uses inner_text() which automatically waits for visibility and returns only visible text.

        :return: Dict[str, str]: Dictionary of label key-value pairs
        :raises AssertionError: If label format is unexpected
        """
        label_elements = await self.page.locator(self.locators.LABEL_BADGE).all()
        labels = {}
        for element in label_elements:
            label_text = await element.inner_text()
            if label_text and "=" in label_text:
                key, value = label_text.split("=", 1)
                labels[key.strip()] = value.strip()
            elif label_text:
                self.logger.warning(f"Label has unexpected format: '{label_text}'")
        return labels

    async def get_annotations_count(self) -> int:
        """
        Get the count of annotations from the annotations button text.
        Uses inner_text() which automatically waits for visibility.

        :return: int: Number of annotations
        :raises AssertionError: If button text is empty or has unexpected format
        """
        button_text = await self.page.inner_text(self.locators.ANNOTATIONS_COUNT)
        if not button_text:
            raise AssertionError("Annotations button text is empty")

        match = re.search(r"(\d+)\s+annotation", button_text)
        if not match:
            raise AssertionError(f"Unexpected annotations button format: '{button_text}'")

        return int(match.group(1))
