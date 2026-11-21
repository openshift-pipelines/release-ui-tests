"""Shared Page Object component for the Edit labels modal."""

from typing import Dict

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.commons import LabelsModalLocators
from framework.ui_components.base_page import BasePage


class LabelsModal(BasePage):
    """Provides interactions with the Edit labels modal shared by resource detail pages."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = LabelsModalLocators()

    async def is_visible(self) -> bool:
        """Wait for and report whether the Edit labels modal is visible."""
        return await super().is_visible(self.locators.MODAL_DIALOG, timeout=self.config.timeout_ms)

    async def add_labels(self, labels: Dict[str, str]) -> bool:
        """Add labels as text to the labels input and save the modal."""
        modal = self.page.locator(self.locators.MODAL_DIALOG)
        await modal.wait_for(state="visible")

        labels_text = ",".join(f"{key}={value}" for key, value in labels.items())
        await modal.locator(self.locators.LABEL_INPUT).fill(labels_text)
        await modal.locator(self.locators.SAVE_BUTTON).click()
        return True

    async def close_labels_dialog(self) -> bool:
        """Close the labels modal without saving changes."""
        modal = self.page.locator(self.locators.MODAL_DIALOG)
        await modal.wait_for(state="visible")
        await modal.locator(self.locators.CLOSE_BUTTON).click()
        return True
