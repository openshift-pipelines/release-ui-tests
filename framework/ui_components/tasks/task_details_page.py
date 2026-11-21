from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskDetailsPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.actions_menu import ActionsMenu
from framework.ui_components.commons.annotations_modal import AnnotationsModal
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.labels_modal import LabelsModal
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
        self.annotations_modal = AnnotationsModal(page, config)
        self.labels_modal = LabelsModal(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Task Details page is currently displayed by checking URL and
        the Task details heading visibility.
        :return: bool: True if URL matches and Task details heading is visible.
        :raises AssertionError: With specific message if URL or heading check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(TASK_DETAILS_URL, self.locators.TASK_DETAILS_HEADING, "Task Details page")

    async def get_task_heading_name(self) -> str:
        """
        Returns the task name displayed in the h1 heading.
        :return: str: The text content of the task name heading.
        """
        return await self.page.locator(self.locators.TASK_NAME_HEADING).inner_text()

    async def get_task_name(self) -> str:
        """
        Returns the task name displayed in the h1 heading.
        :return: str: The text content of the task name heading.
        """
        return await self.page.locator(self.locators.TASK_NAME).inner_text()

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

    async def get_namespace_value(self) -> str:
        """
        Clicks the namespace link in the details section to navigate to the namespace page.
        :return: bool: True if click succeeds.
        """
        return await self.page.locator(self.locators.NAMESPACE_VALUE).inner_text()

    async def click_namespace_link(self) -> bool:
        """
        Clicks the namespace link in the details section to navigate to the namespace page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAMESPACE_LINK)

    async def get_labels_value(self) -> str:
        """
        Clicks the 'Edit' button next to Labels to open the labels editor.
        :return: bool: True if click succeeds.
        """
        return await self.page.locator(self.locators.LABELS_VALUE).inner_text()

    async def click_edit_labels(self) -> bool:
        """
        Clicks the 'Edit' button next to Labels to open the labels editor.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDIT_LABELS_BUTTON)

    async def open_labels_dialog(self) -> bool:
        """Open the Edit labels dialog and wait until it is visible."""
        await self.click_edit_labels()
        return await self.labels_modal.is_visible()

    async def get_annotations_count_value(self) -> str:
        """
        Returns the annotation count displayed in the details section.
        :return: The annotations count text.
        """
        return await self.page.locator(self.locators.ANNOTATIONS_COUNT_VALUE).inner_text()

    async def get_annotations_value(self) -> str:
        """
        Clicks the 'Edit' button next to Labels to open the labels editor.
        :return: bool: True if click succeeds.
        """
        return await self.page.locator(self.locators.LABELS_VALUE).inner_text()

    async def click_annotations(self) -> bool:
        """
        Clicks the Edit annotations button to open the annotations dialog.
        :return: True if the button is clicked successfully.
        """
        return await self.click_element(self.locators.EDIT_ANNOTATIONS_BUTTON)

    async def open_annotations_dialog(self) -> bool:
        """Open the Edit annotations dialog and wait until it is visible."""
        await self.click_annotations()
        return await self.annotations_modal.is_visible()

    async def get_annotations_dialog_field_values(self) -> dict[str, str]:
        """Return annotation key/value pairs from the open Edit annotations dialog."""
        return await self.annotations_modal.get_annotation_field_values()
