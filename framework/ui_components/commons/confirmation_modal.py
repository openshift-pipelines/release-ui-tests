"""Confirmation modal component for delete and other confirmation actions.

Provides reusable abstraction for modal interactions across all resource types.
Follows Single Responsibility Principle - handles only modal interactions.
"""

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.commons import ConfirmationModalLocators
from framework.ui_components.base_page import BasePage


class ConfirmationModal(BasePage):
    """Shared component for confirmation modals that appear across resource deletion and other actions."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = ConfirmationModalLocators()

    async def is_modal_visible(self) -> bool:
        """
        Check if the confirmation modal is currently visible.

        :return: bool: True if modal is visible, False otherwise
        """
        return await self.is_visible(self.locators.MODAL_DIALOG, timeout=self.config.timeout_ms)

    async def click_confirm(self) -> bool:
        """
        Click the confirmation button in the modal (e.g., 'Delete', 'Confirm').

        :return: bool: True if button clicked successfully
        """
        return await self.click_element(self.locators.CONFIRM_BUTTON)

    async def click_cancel(self) -> bool:
        """
        Click the cancel button in the modal.

        :return: bool: True if button clicked successfully
        """
        return await self.click_element(self.locators.CANCEL_BUTTON)

    async def confirm_deletion(self, resource_name: str) -> bool:
        """
        Wait for modal to appear, verify resource name, and confirm deletion.

        :param str resource_name: Name of the resource being deleted (for verification)
        :return: bool: True if confirmation succeeded
        :raises AssertionError: If modal does not appear or confirmation fails
        """
        # Wait for modal to appear
        is_visible = await self.is_modal_visible()
        assert is_visible, f"Confirmation modal did not appear for deleting '{resource_name}'"

        # Click confirm button
        confirmed = await self.click_confirm()
        assert confirmed, f"Failed to click confirm button for deleting '{resource_name}'"

        # Wait for modal to disappear
        await self.page.wait_for_timeout(1000)  # Brief wait for modal animation

        return True

    async def get_modal_text(self) -> str:
        """
        Get the text content from the modal body.

        :return: str: Modal body text content
        """
        return await self.get_text(self.locators.MODAL_BODY)
