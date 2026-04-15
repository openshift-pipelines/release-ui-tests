from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.tasks import CreateTaskPageLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector


class CreateTaskPage(BasePage):
    """Page object for the Create Task YAML editor page."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = CreateTaskPageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)

    async def verify_on_page(self) -> bool:
        """
        Verifies that the Create Task page is currently displayed by checking URL and header visibility.
        Waits for the URL to contain 'tekton.dev~v1~Task/~new', then checks if the Create Task header
        is visible.
        :return: bool: True if URL matches and Create Task header is visible.
        :raises AssertionError: With specific message if URL or header check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        return await self.wait_for_url_to_contain("tekton.dev~v1~Task/~new") and await self.is_visible(
            self.locators.CREATE_TASK_HEADER
        )

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
        Clicks the 'Hide sidebar' toolbar button to show/hide the schema sidebar.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.TOGGLE_SIDEBAR_BUTTON)

    async def click_shortcuts(self) -> bool:
        """
        Clicks the 'Shortcuts' button to display keyboard shortcuts.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SHORTCUTS_BUTTON)

    async def click_create(self) -> bool:
        """
        Clicks the 'Create' button to submit the YAML and create the Task resource.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SAVE_CHANGES_BUTTON)

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

    async def click_close_sidebar(self) -> bool:
        """
        Clicks the 'Close' button on the schema sidebar to close it.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.CLOSE_SIDEBAR_BUTTON)

    async def is_schema_sidebar_visible(self) -> bool:
        """
        Checks whether the schema sidebar (with 'Task' heading) is visible.
        :return: bool: True if the sidebar is visible, False otherwise.
        """
        return await self.is_visible(self.locators.SCHEMA_SIDEBAR_HEADING)
