"""
Monaco Editor Component - Shared interaction logic for Monaco code editor.

This component encapsulates all Monaco editor-specific interactions following
the Single Responsibility Principle. Page objects should compose this component
rather than duplicating Monaco interaction logic.

Design Principles:
- Single Responsibility: Handles only Monaco editor interactions
- DRY: Single source of truth for Monaco operations
- Composition over Inheritance: Page objects compose this component
- Testability: Can be unit tested independently
"""

import logging
from typing import Optional

from playwright.async_api import Page

from framework.config.config import Config


class MonacoEditor:
    """
    Handles interactions with Monaco Editor instances used throughout the console.

    Monaco Editor is the same code editor used in VS Code and requires special
    handling beyond standard input elements. This component provides reliable
    methods for reading and writing editor content.

    Usage:
        editor = MonacoEditor(page, config)
        await editor.set_content(yaml_string)
        content = await editor.get_content()
    """

    # Data attribute set by console's CodeEditor when Monaco is fully mounted
    MONACO_MOUNTED_SELECTOR = '[data-test="code-editor"]'

    # Monaco editor container
    MONACO_CONTAINER_SELECTOR = ".monaco-editor"

    # Monaco textarea (for focus/keyboard interactions)
    MONACO_TEXTAREA_SELECTOR = ".monaco-editor textarea"

    def __init__(self, page: Page, config: Config, custom_selector: Optional[str] = None) -> None:
        """
        Initialize Monaco Editor component.

        :param page: Playwright page instance
        :param config: Framework configuration
        :param custom_selector: Optional custom selector if Monaco is in a specific container
        """
        self.page = page
        self.config = config
        self.selector = custom_selector or self.MONACO_CONTAINER_SELECTOR
        self.logger = logging.getLogger(__name__)

    async def wait_for_editor_ready(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for Monaco editor to be fully initialized and ready for interaction.

        OpenShift Console's CodeEditor component sets data-test="code-editor" when
        Monaco is mounted and ready. However, not all pages use this attribute
        (e.g., Pipeline Builder YAML view). In such cases, we fall back to waiting
        for the .monaco-editor container itself.

        :param timeout: Optional timeout in milliseconds (uses config default if not provided)
        :return: True if editor is ready
        :raises TimeoutError: If editor doesn't become ready within timeout
        """
        timeout_ms = timeout or self.config.timeout_ms
        try:
            # Try primary selector first (most reliable when available)
            try:
                await self.page.wait_for_selector(
                    self.MONACO_MOUNTED_SELECTOR,
                    timeout=5000,  # Short timeout for primary selector
                    state="visible",
                )
                self.logger.debug("Monaco editor is ready (via data-test attribute)")
                return True
            except Exception:
                # Fallback: Some pages don't set data-test="code-editor"
                # Use the Monaco container selector instead
                await self.page.wait_for_selector(
                    self.selector,  # Use custom selector if provided, else MONACO_CONTAINER_SELECTOR
                    timeout=timeout_ms,
                    state="visible",
                )
                # Additional wait for Monaco to fully initialize
                await self.page.wait_for_timeout(1000)
                self.logger.debug(f"Monaco editor is ready (via {self.selector})")
                return True
        except Exception as e:
            self.logger.error(f"Monaco editor failed to become ready: {e}")
            raise

    async def set_content(self, content: str, timeout: Optional[int] = None) -> bool:
        """
        Set the content of the Monaco editor using Monaco's JavaScript API.

        This is the most reliable method (Option 1 from our analysis) as it:
        - Uses Monaco's native setValue() API
        - Single atomic operation (no timing issues)
        - Preserves all formatting, newlines, and special characters
        - Same approach used by console's own Cypress tests

        Based on: frontend/packages/integration-tests/views/yaml-editor.ts:13-21

        :param content: Text content to set in the editor
        :param timeout: Optional timeout for editor readiness
        :return: True if content was set successfully
        :raises Exception: If Monaco API is not available or setValue fails
        """
        try:
            # Wait for Monaco to be fully mounted
            await self.wait_for_editor_ready(timeout)

            # Use Monaco's API to set the value
            # This matches the console's own Cypress test implementation
            success = await self.page.evaluate(
                """
                (content) => {
                    // Access Monaco's editor models (same as Cypress tests)
                    if (window.monaco && window.monaco.editor) {
                        const models = window.monaco.editor.getModels();
                        if (models && models.length > 0) {
                            models[0].setValue(content);
                            return true;
                        }
                    }

                    // Fallback: try alternative access methods
                    const editorElement = document.querySelector('.monaco-editor');
                    if (editorElement && editorElement._editor) {
                        editorElement._editor.setValue(content);
                        return true;
                    }

                    throw new Error('Monaco editor API not available');
                }
                """,
                content,
            )

            if success:
                self.logger.debug(f"Successfully set Monaco editor content ({len(content)} chars)")
                # Small delay to allow Monaco to process the content
                await self.page.wait_for_timeout(300)
                return True

            raise Exception("Monaco setValue did not return success")

        except Exception as e:
            self.logger.error(f"Failed to set Monaco editor content: {e}")
            raise

    async def get_content(self, timeout: Optional[int] = None) -> str:
        """
        Get the current content from the Monaco editor using Monaco's JavaScript API.

        Uses Monaco's getValue() API which is the most reliable method for reading
        editor content. Falls back to alternative methods if Monaco API is unavailable.

        Based on: frontend/packages/integration-tests/views/yaml-editor.ts:3-11

        :param timeout: Optional timeout for editor readiness
        :return: Current content from the editor as a string
        """
        try:
            # Wait for Monaco to be ready
            await self.wait_for_editor_ready(timeout)

            # Use Monaco's API to get the value (matches Cypress implementation)
            content = await self.page.evaluate(
                """
                () => {
                    // Primary method: Use Monaco's getModels() API
                    if (window.monaco && window.monaco.editor) {
                        const models = window.monaco.editor.getModels();
                        if (models && models.length > 0) {
                            return models[0].getValue();
                        }
                    }

                    // Fallback 1: Try to access via editor instance
                    const editorElement = document.querySelector('.monaco-editor');
                    if (editorElement && editorElement._editor) {
                        return editorElement._editor.getValue();
                    }

                    // Fallback 2: Extract from view lines (last resort, may be incomplete)
                    const viewLines = document.querySelectorAll('.view-line');
                    if (viewLines && viewLines.length > 0) {
                        const lines = [];
                        viewLines.forEach(line => {
                            const spans = line.querySelectorAll('span');
                            let lineText = '';
                            spans.forEach(span => {
                                lineText += span.textContent || '';
                            });
                            lines.push(lineText);
                        });
                        return lines.join('\\n');
                    }

                    return '';
                }
                """
            )

            self.logger.debug(f"Retrieved Monaco editor content ({len(content)} chars)")
            return content or ""

        except Exception as e:
            self.logger.error(f"Failed to get Monaco editor content: {e}")
            return ""

    async def is_editor_visible(self) -> bool:
        """
        Check if the Monaco editor is visible on the page.

        :return: True if editor container is visible
        """
        try:
            return await self.page.locator(self.MONACO_CONTAINER_SELECTOR).is_visible()
        except Exception:
            return False

    async def focus(self) -> bool:
        """
        Focus the Monaco editor to enable keyboard interactions.

        :return: True if focus was successful
        """
        try:
            await self.wait_for_editor_ready()
            textarea = self.page.locator(self.MONACO_TEXTAREA_SELECTOR).first
            await textarea.focus()
            self.logger.debug("Monaco editor focused")
            return True
        except Exception as e:
            self.logger.error(f"Failed to focus Monaco editor: {e}")
            return False

    async def clear(self) -> bool:
        """
        Clear all content from the Monaco editor.

        :return: True if content was cleared successfully
        """
        try:
            return await self.set_content("")
        except Exception as e:
            self.logger.error(f"Failed to clear Monaco editor: {e}")
            return False
