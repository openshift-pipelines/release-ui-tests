"""Shared Page Object component for the Edit annotations modal."""

from typing import Dict

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.commons import AnnotationsModalLocators
from framework.ui_components.base_page import BasePage


class AnnotationsModal(BasePage):
    """Provides interactions with the Edit annotations modal shared by resource detail pages."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = AnnotationsModalLocators()

    async def is_visible(self) -> bool:
        """Wait for and report whether the Edit annotations modal is visible."""
        return await super().is_visible(self.locators.MODAL_DIALOG, timeout=self.config.timeout_ms)

    async def get_annotation_field_values(self) -> Dict[str, str]:
        """Return annotations as key/value pairs from the modal's pair-list rows."""
        modal = self.page.locator(self.locators.MODAL_DIALOG)
        await modal.wait_for(state="visible")
        annotation_rows = modal.locator(self.locators.PAIR_LIST_ROW)
        await annotation_rows.first.wait_for(state="visible")

        annotations = {}
        for index in range(await annotation_rows.count()):
            row = annotation_rows.nth(index)
            key = await row.locator(self.locators.KEY_INPUT).input_value()
            value = await row.locator(self.locators.VALUE_INPUT).input_value()
            annotations[key] = value

        return annotations

    async def save_annotations(self) -> bool:
        """Save the annotations currently entered in the modal."""
        modal = self.page.locator(self.locators.MODAL_DIALOG)
        await modal.wait_for(state="visible")
        await modal.locator(self.locators.SAVE_BUTTON).click()
        return True

    async def add_annotations(self, annotations: Dict[str, str]) -> bool:
        """Append annotation key/value pairs and save the modal."""
        modal = self.page.locator(self.locators.MODAL_DIALOG)
        await modal.wait_for(state="visible")

        for key, value in annotations.items():
            await modal.locator(self.locators.ADD_PAIR_BUTTON).click()
            new_row = modal.locator(self.locators.PAIR_LIST_ROW).last
            await new_row.locator(self.locators.KEY_INPUT).fill(str(key))
            await new_row.locator(self.locators.VALUE_INPUT).fill(str(value))

        await modal.locator(self.locators.SAVE_BUTTON).click()
        return True

    async def close_annotations_dialog(self) -> bool:
        """Close the annotations modal without saving changes."""
        modal = self.page.locator(self.locators.MODAL_DIALOG)
        await modal.wait_for(state="visible")
        await modal.locator(self.locators.CLOSE_BUTTON).click()
        return True
