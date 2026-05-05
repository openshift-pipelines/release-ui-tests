from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import PipelineDetailsPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.actions_menu import ActionsMenu
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector
from framework.ui_components.console_url_patterns import PIPELINE_DETAILS_URL


class PipelineDetailsPage(BasePage):
    """
    Page object for the Pipeline Details page.
    Displays comprehensive information about a specific Pipeline resource including
    visualization, metadata, tabs for YAML, Parameters, Metrics, and PipelineRuns.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = PipelineDetailsPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)
        self.actions_menu = ActionsMenu(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Pipeline Details page is currently displayed by checking URL and header.
        Waits for the URL to match the pipeline details pattern, then checks if the pipeline name
        heading is visible.
        :return: bool: True if URL matches and heading is visible.
        :raises AssertionError: With specific message if URL or header check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(
            PIPELINE_DETAILS_URL, self.locators.PIPELINE_NAME_HEADING, "Pipeline Details page"
        )

    async def click_breadcrumb_pipelines(self) -> bool:
        """
        Clicks the 'Pipelines' link in the breadcrumb to navigate back to Pipelines list.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.BREADCRUMB_PIPELINES_LINK)

    async def click_details_tab(self) -> bool:
        """
        Clicks the 'Details' tab to view pipeline details and visualization.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DETAILS_TAB)

    async def click_yaml_tab(self) -> bool:
        """
        Clicks the 'YAML' tab to view the pipeline YAML definition.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.YAML_TAB)

    async def click_parameters_tab(self) -> bool:
        """
        Clicks the 'Parameters' tab to view pipeline parameters.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.PARAMETERS_TAB)

    async def click_metrics_tab(self) -> bool:
        """
        Clicks the 'Metrics' tab to view pipeline metrics and statistics.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.METRICS_TAB)

    async def click_pipelineruns_tab(self) -> bool:
        """
        Clicks the 'PipelineRuns' tab to view list of pipeline runs.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.PIPELINERUNS_TAB)

    async def click_zoom_in(self) -> bool:
        """
        Clicks the 'Zoom in' button to zoom into the pipeline visualization.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.ZOOM_IN_BUTTON)

    async def click_zoom_out(self) -> bool:
        """
        Clicks the 'Zoom out' button to zoom out of the pipeline visualization.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.ZOOM_OUT_BUTTON)

    async def click_fit_to_screen(self) -> bool:
        """
        Clicks the 'Fit to screen' button to fit the pipeline visualization to screen.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.FIT_TO_SCREEN_BUTTON)

    async def click_reset_view(self) -> bool:
        """
        Clicks the 'Reset view' button to reset the pipeline visualization to default view.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.RESET_VIEW_BUTTON)

    async def click_namespace_link(self) -> bool:
        """
        Clicks the namespace link to navigate to the namespace details page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.NAMESPACE_LINK)

    async def click_edit_labels(self) -> bool:
        """
        Clicks the 'Edit' button next to Labels to edit pipeline labels.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDIT_LABELS_BUTTON)

    async def get_pipeline_name(self) -> str:
        """
        Gets the pipeline name from the page heading.
        :return: str: The pipeline name.
        """
        return await self.page.locator(self.locators.PIPELINE_NAME_HEADING).inner_text()
