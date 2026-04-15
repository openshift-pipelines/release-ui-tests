from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import TaskYamlPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.actions_menu import ActionsMenu
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector
from framework.ui_components.console_url_patterns import TASK_YAML_URL


class TaskYamlPage(BasePage):
    """Page object for the Task YAML editor tab."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = TaskYamlPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)
        self.actions_menu = ActionsMenu(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Task YAML tab is currently displayed by checking URL and
        YAML editor visibility.
        :return: bool: True if URL matches and YAML editor is visible.
        :raises AssertionError: With specific message if URL or editor check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self._verify_page_regex(TASK_YAML_URL, self.locators.YAML_EDITOR, "Task YAML page")

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
        Switches to the YAML tab.
        :return: bool: True if tab click succeeds.
        """
        return await self.click_element(self.locators.YAML_TAB)

    async def click_breadcrumb_tasks(self) -> bool:
        """
        Clicks the 'Tasks' breadcrumb link to navigate back to the Tasks list page.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.BREADCRUMB_TASKS_LINK)

    async def is_yaml_editor_visible(self) -> bool:
        """
        Checks whether the Monaco YAML editor is visible on the page.
        :return: bool: True if the editor is visible, False otherwise.
        """
        return await self.is_visible(self.locators.YAML_EDITOR)

    async def get_yaml_content(self) -> str:
        """
        Extracts the current YAML content from the Monaco editor.

        Uses JavaScript to access Monaco's internal model to get the exact content.
        This is more reliable than trying to read from the textarea.

        :return: str: Current YAML content in the editor
        """
        try:
            # Wait for editor to be visible
            await self.page.wait_for_selector(self.locators.YAML_EDITOR, timeout=self.config.timeout_ms)

            # Use JavaScript to get Monaco editor content
            yaml_content = await self.page.evaluate(
                """
                () => {
                    const editor = document.querySelector('.monaco-editor');
                    if (editor && editor.querySelector('textarea')) {
                        const textarea = editor.querySelector('textarea');
                        return textarea.value;
                    }
                    return '';
                }
                """
            )

            return yaml_content or ""

        except Exception as e:
            self.logger.error(f"Failed to extract YAML content from editor: {e}")
            return ""

    async def fill_yaml_editor(self, yaml_content: str) -> bool:
        """
        Fill the Monaco YAML editor with the provided YAML content.

        Uses clipboard paste approach for reliability. This is the most dependable
        method for multi-line content in Monaco editor because:
        - Preserves all newlines, indentation, and special characters
        - Single atomic operation (no timing/race conditions)
        - Monaco's paste handler processes content correctly

        Follows Single Responsibility Principle: delegates to Monaco's paste handler
        rather than manually managing keyboard events.

        :param str yaml_content: YAML content string to fill into the editor
        :return: bool: True if editor was filled successfully
        """
        try:
            # Wait for editor to be visible and ready
            await self.page.wait_for_selector(self.locators.YAML_EDITOR, timeout=self.config.timeout_ms)

            # Click into the editor to focus it
            await self.page.click(self.locators.YAML_EDITOR)
            await self.page.wait_for_timeout(300)

            # Select all existing content
            await self.page.keyboard.press("Control+A")
            await self.page.wait_for_timeout(100)

            # Use evaluate to set clipboard content and paste
            # This is more reliable than pyperclip or external clipboard managers
            await self.page.evaluate(
                """
                async (yamlContent) => {
                    // Write to clipboard using Clipboard API
                    await navigator.clipboard.writeText(yamlContent);
                }
                """,
                yaml_content,
            )

            # Wait for clipboard to be set
            await self.page.wait_for_timeout(200)

            # Paste using Ctrl+V
            await self.page.keyboard.press("Control+V")

            # Wait for Monaco to process the paste and render the content
            await self.page.wait_for_timeout(800)

            return True

        except Exception as e:
            self.logger.error(f"Failed to fill YAML editor: {e}")
            return False

    async def click_copy_code(self) -> bool:
        """
        Clicks the 'Copy code to clipboard' toolbar button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.COPY_CODE_BUTTON)

    async def click_editor_settings(self) -> bool:
        """
        Clicks the 'Editor settings' toolbar button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.EDITOR_SETTINGS_BUTTON)

    async def click_toggle_fullscreen(self) -> bool:
        """
        Clicks the 'Toggle fullscreen mode' toolbar button.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TOGGLE_FULLSCREEN_BUTTON)

    async def click_toggle_sidebar(self) -> bool:
        """
        Clicks the sidebar toggle button to show/hide the schema sidebar.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TOGGLE_SIDEBAR_BUTTON)

    async def click_shortcuts(self) -> bool:
        """
        Clicks the 'Shortcuts' button to display keyboard shortcuts.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SHORTCUTS_BUTTON)

    async def click_save(self) -> bool:
        """
        Clicks the 'Save' button to save the YAML changes.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SAVE_BUTTON)

    async def click_reload(self) -> bool:
        """
        Clicks the 'Reload' button to discard local edits and reload the YAML from the server.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.RELOAD_BUTTON)

    async def click_cancel(self) -> bool:
        """
        Clicks the 'Cancel' button to discard changes and navigate back.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CANCEL_BUTTON)

    async def click_download(self) -> bool:
        """
        Clicks the 'Download' button to download the current YAML content as a file.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.DOWNLOAD_BUTTON)
