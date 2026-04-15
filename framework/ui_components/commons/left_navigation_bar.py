from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.commons import LeftNavigationBarLocators
from framework.ui_components.base_page import BasePage


class LeftNavigationBar(BasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = LeftNavigationBarLocators()

    async def verify_pipelines_button_visible(self) -> bool:
        """
        Verifies that the Pipelines button is visible in the left navigation bar.
        Uses is_visible() which waits up to the configured timeout for the element to become visible.
        Returns False if the button is not visible within the timeout.
        :return: bool: True if Pipelines button is visible, False if not visible within timeout.
        """
        return await self.is_visible(self.locators.PIPELINES_BUTTON)

    async def is_pipelines_menu_expanded(self) -> bool:
        """
        Checks if the Pipelines menu is currently expanded by reading the aria-expanded attribute.
        This is much faster than waiting for child elements to appear.
        :return: bool: True if menu is expanded (aria-expanded="true"), False otherwise.
        """
        try:
            aria_expanded = await self.page.get_attribute(self.locators.PIPELINES_BUTTON, "aria-expanded")
            return aria_expanded == "true"
        except Exception:
            return False

    async def verify_link_available_under_pipelines_button(self, link_name: str) -> bool:
        """
        Verifies that a specific link is available under the Pipelines button in the left navigation bar.
        Maps the link name to the appropriate locator and checks if the link is visible.
        :param str link_name: The name of the link to verify (e.g., "Overview", "Pipelines", "Tasks", "Triggers").
        :return: bool: True if the link is visible, False if not visible within timeout.
        Raises AssertionError if an invalid link name is provided.
        """
        link_locator_map = {
            "Overview": self.locators.NAV_OVERVIEW_LINK,
            "Pipelines": self.locators.NAV_PIPELINES_LINK,
            "Tasks": self.locators.NAV_TASKS_LINK,
            "Triggers": self.locators.NAV_TRIGGERS_LINK,
        }

        if link_name not in link_locator_map:
            raise AssertionError(
                f"Invalid link name '{link_name}' provided. Valid options: {list(link_locator_map.keys())}"
            )

        return await self.is_visible(link_locator_map[link_name])

    async def click_pipelines_button(self) -> bool:
        """
        Clicks the Pipelines button to expand/collapse the submenu.

        Uses fast click optimization since the Pipelines button is:
        - Always visible in the navigation bar
        - Static (doesn't animate or move)
        - Doesn't trigger page navigation (just expands/collapses menu)

        Performance: ~5s timeout vs 90s, no wait after click.

        :return: bool: True if click succeeds, False if any click fails or raises TimeoutError.
        """
        return await self.click_element_fast(self.locators.PIPELINES_BUTTON)

    async def navigate_to_pipelines(self) -> bool:
        """
        Navigates to the Pipelines page by clicking on the Pipelines link.

        Uses standard click (not fast) because navigation links trigger page loads,
        so we want Playwright's full actionability checks and navigation wait.

        :return: bool: True if navigation click succeeds, False if click fails or raises TimeoutError.
        """
        return await self.click_element(self.locators.NAV_PIPELINES_LINK)

    async def navigate_to_overview(self) -> bool:
        """
        Navigates to the Pipelines Overview page by clicking on the Overview link.

        Uses standard click (not fast) because navigation links trigger page loads,
        so we want Playwright's full actionability checks and navigation wait.

        :return: bool: True if navigation click succeeds, False if click fails or raises TimeoutError.
        """
        return await self.click_element(self.locators.NAV_OVERVIEW_LINK)

    async def navigate_to_tasks(self) -> bool:
        """
        Navigates to the Tasks page by clicking on the Tasks link.

        Uses standard click (not fast) because navigation links trigger page loads,
        so we want Playwright's full actionability checks and navigation wait.

        :return: bool: True if navigation click succeeds, False if click fails or raises TimeoutError.
        """
        return await self.click_element(self.locators.NAV_TASKS_LINK)

    async def navigate_to_triggers(self) -> bool:
        """
        Navigates to the Triggers page by clicking on the Triggers link.

        Uses standard click (not fast) because navigation links trigger page loads,
        so we want Playwright's full actionability checks and navigation wait.

        :return: bool: True if navigation click succeeds, False if click fails or raises TimeoutError.
        """
        return await self.click_element(self.locators.NAV_TRIGGERS_LINK)
