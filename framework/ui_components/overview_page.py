from framework.ui_components.base_page import BasePage


class OverViewPage(BasePage):
    OVERVIEW_HEADER = 'h1:has-text("Overview")'

    def verify_on_page(self) -> bool:
        """
        Verifies that the Overview page is currently displayed by checking URL and header visibility.
        First waits for URL to end with "dashboards", then checks if the Overview header is visible.
        Both conditions must be true for verification to pass.
        :return: bool: True if URL matches and Overview header is visible, False otherwise.
        Raises TimeoutError if URL doesn't match within the timeout.
        """
        return self.wait_for_url_to_endwith("dashboards") and self.is_visible(self.OVERVIEW_HEADER)
