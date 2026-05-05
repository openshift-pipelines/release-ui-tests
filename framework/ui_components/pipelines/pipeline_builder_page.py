from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import PipelineBuilderPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.project_selector import ProjectSelector
from framework.ui_components.console_url_patterns import PIPELINE_BUILDER_URL
from framework.ui_components.pipeline_builder.builder_view import BuilderView
from framework.ui_components.pipeline_builder.yaml_view import YamlView


class PipelineBuilderPage(BasePage):
    """
    Page object for the Pipeline Builder page.

    This page has two distinct views/modes on the same URL:
    - Builder View: Visual form-based pipeline creation
    - YAML View: Direct YAML editing with Monaco editor

    The page composes separate view objects for each mode following the Composition Pattern,
    allowing clean separation of view-specific functionality while maintaining common page actions.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = PipelineBuilderPageLocators()

        # Compose shared components
        self.project_selector = ProjectSelector(page, config)

        # Compose view-specific components (Composition Pattern for view hierarchy)
        self.builder_view = BuilderView(page, config)
        self.yaml_view = YamlView(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Pipeline Builder page is currently displayed by checking URL and header visibility.
        Waits for the URL to match the pipeline builder pattern, then checks if the header is visible.
        :return: bool: True if URL matches and header is visible.
        :raises AssertionError: With specific message if URL or header check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(
            PIPELINE_BUILDER_URL, self.locators.PIPELINE_BUILDER_HEADER, "Pipeline Builder page"
        )

    async def switch_to_yaml_view(self) -> bool:
        """
        Switches from Pipeline builder to YAML view by clicking the YAML view radio button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.YAML_VIEW_RADIO)

    async def switch_to_builder_view(self) -> bool:
        """
        Switches from YAML view to Pipeline builder by clicking the Pipeline builder radio button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.PIPELINE_BUILDER_RADIO)

    async def click_create(self) -> bool:
        """
        Clicks the 'Create' button to create the pipeline.
        Note: This button is disabled until the form is valid (e.g., at least one task is added).
        Used in CREATE workflow (new pipeline).
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CREATE_BUTTON)

    async def click_save(self) -> bool:
        """
        Clicks the 'Save' button to save changes to an existing pipeline.
        Used in EDIT workflow (editing existing pipeline).
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SAVE_BUTTON)

    async def click_cancel(self) -> bool:
        """
        Clicks the 'Cancel' button to cancel pipeline creation and return to the previous page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CANCEL_BUTTON)

    async def is_create_button_enabled(self) -> bool:
        """
        Checks if the Create button is enabled (form is valid).
        :return: bool: True if Create button is enabled.
        """
        return await self.is_element_enabled(self.locators.CREATE_BUTTON)
