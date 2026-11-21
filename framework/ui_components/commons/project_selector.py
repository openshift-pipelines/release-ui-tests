import logging

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.commons import ProjectSelectorLocators
from framework.ui_components.base_page import BasePage


class ProjectSelector(BasePage):
    """Shared component for the project selector dropdown that appears across pages."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = ProjectSelectorLocators()
        self.logger = logging.getLogger(__name__)

    async def click_project_selector(self) -> bool:
        """
        Clicks the project selector dropdown button to open the project list.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.PROJECT_SELECTOR_BUTTON)

    async def is_project_selector_visible(self) -> bool:
        """
        Checks whether the project selector button is visible on the page.
        :return: bool: True if the project selector is visible, False otherwise.
        """
        return await self.is_visible(self.locators.PROJECT_SELECTOR_BUTTON)

    async def select_project(
        self,
        project_name: str,
        max_retries: int = 3,
        refresh_rounds: int = 2,
    ) -> bool:
        """
        Selects a specific project from the project selector dropdown with retry logic.

        Handles flakiness by:
        - Retrying the dropdown interaction up to ``max_retries`` times per round
        - Explicitly waiting for dropdown menu to appear
        - Waiting for project menu item to be visible before clicking
        - Verifying project was actually switched
        - If the namespace still does not appear in the filter after a round (known
          console watch staleness), reloading the page and retrying up to
          ``refresh_rounds`` rounds

        :param str project_name: Name of the project to select
        :param int max_retries: Dropdown attempts per refresh round (default: 3)
        :param int refresh_rounds: Full rounds including a page reload between them
            (default: 2 → try, reload once, try again)
        :return: bool: True if project selected successfully, False otherwise
        """
        for round_num in range(1, refresh_rounds + 1):
            self.logger.info(
                f"[SELECT PROJECT] Refresh round {round_num}/{refresh_rounds}: selecting project '{project_name}'"
            )
            if await self._try_select_project(project_name, max_retries=max_retries):
                return True

            if round_num < refresh_rounds:
                self.logger.warning(
                    f"[SELECT PROJECT] Project '{project_name}' not found after "
                    f"{max_retries} attempts; reloading page before round {round_num + 1}"
                )
                if not await self._refresh_for_project_retry():
                    self.logger.error("[SELECT PROJECT] Page reload did not restore the project selector; giving up")
                    return False

        self.logger.error(
            f"[SELECT PROJECT] Failed to select project '{project_name}' after "
            f"{refresh_rounds} refresh round(s) × {max_retries} attempts"
        )
        return False

    async def _refresh_for_project_retry(self) -> bool:
        """
        Reload the page and wait for the project selector to be interactable again.

        Uses domcontentloaded (not networkidle — console websockets never go idle)
        then waits for the selector button we are about to click.
        """
        try:
            await self.page.keyboard.press("Escape")
        except Exception:
            pass

        try:
            await self.page.reload(wait_until="domcontentloaded")
        except Exception as reload_error:
            self.logger.error(f"[SELECT PROJECT] page.reload failed: {reload_error}")
            return False

        # Wait for the control we will touch next — not a proxy for "page loaded".
        ready = await self.is_visible(self.locators.PROJECT_SELECTOR_BUTTON)
        if not ready:
            self.logger.error("[SELECT PROJECT] Project selector not visible after reload")
        return ready

    async def _try_select_project(self, project_name: str, max_retries: int = 3) -> bool:
        """One refresh-round of dropdown open / filter / click / verify attempts."""
        for attempt in range(1, max_retries + 1):
            try:
                self.logger.info(
                    f"[SELECT PROJECT] Attempt {attempt}/{max_retries}: Selecting project '{project_name}'"
                )

                # Click project selector to open dropdown
                click_success = await self.click_project_selector()
                if not click_success:
                    self.logger.warning(f"[SELECT PROJECT] Attempt {attempt}: Failed to click project selector button")
                    await self.page.wait_for_timeout(1000 * attempt)  # Exponential backoff
                    continue

                # Wait for dropdown menu to appear (use role=menu as indicator)
                try:
                    await self.page.wait_for_selector("role=menu", state="visible", timeout=5000)
                    self.logger.info(f"[SELECT PROJECT] Attempt {attempt}: Dropdown menu appeared")
                except Exception as menu_error:
                    self.logger.warning(
                        f"[SELECT PROJECT] Attempt {attempt}: Dropdown menu did not appear: {menu_error}"
                    )
                    await self.page.wait_for_timeout(1000 * attempt)
                    continue

                # Filter the list when the console shows a search box (long project lists).
                try:
                    await self.page.locator(self.locators.PROJECT_FILTER_INPUT).first.fill(project_name, timeout=2000)
                    await self.page.wait_for_timeout(500)
                except Exception:
                    pass

                # Wait for the specific project menu item to be visible
                project_locator = self.locators.PROJECT_MENU_ITEM.format(project_name=project_name)
                try:
                    await self.page.wait_for_selector(project_locator, state="visible", timeout=10000)
                    self.logger.info(
                        f"[SELECT PROJECT] Attempt {attempt}: Project menu item '{project_name}' is visible"
                    )
                except Exception as item_error:
                    self.logger.warning(
                        f"[SELECT PROJECT] Attempt {attempt}: Project menu item '{project_name}' "
                        f"not found: {item_error}"
                    )
                    # Close dropdown by clicking elsewhere and retry
                    await self.page.keyboard.press("Escape")
                    await self.page.wait_for_timeout(1000 * attempt)
                    continue

                # Click the project menu item
                click_item_success = await self.click_element(project_locator)
                if not click_item_success:
                    self.logger.warning(
                        f"[SELECT PROJECT] Attempt {attempt}: Failed to click project menu item '{project_name}'"
                    )
                    await self.page.wait_for_timeout(1000 * attempt)
                    continue

                # Wait for page to reload with new project context
                await self.page.wait_for_timeout(2000)

                # Verify project was actually switched by checking the button text
                current_project = await self.get_current_project()
                if current_project == project_name:
                    self.logger.info(
                        f"[SELECT PROJECT] Attempt {attempt}: Successfully switched to project '{project_name}'"
                    )
                    return True
                else:
                    self.logger.warning(
                        f"[SELECT PROJECT] Attempt {attempt}: Expected project '{project_name}' but "
                        f"current project is '{current_project}'"
                    )
                    await self.page.wait_for_timeout(1000 * attempt)
                    continue

            except Exception as e:
                self.logger.error(f"[SELECT PROJECT] Attempt {attempt}: Unexpected error: {e}")
                await self.page.wait_for_timeout(1000 * attempt)
                continue

        return False

    async def get_current_project(self) -> str:
        """
        Gets the current selected project name from the project selector button text.

        :return: str: Current project name (empty string if selector not visible or error)
        """
        try:
            button_text = await self.page.text_content(self.locators.PROJECT_SELECTOR_BUTTON)
            # Button text is like "Project: ui-test" - extract project name
            if button_text and "Project:" in button_text:
                return button_text.replace("Project:", "").strip()
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get current project: {e}")
            return ""
