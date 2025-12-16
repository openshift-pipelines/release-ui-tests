from framework.ui_components.base_page import BasePage


class PipelinesPage(BasePage):
    PIPELINES_HEADER = 'h1:has-text("Pipelines")'

    def verify_on_page(self) -> bool:
        """
        Verifies that the Pipelines page is currently displayed by checking URL and header visibility.
        First waits for URL to end with "pipelines/all-namespaces", then checks if the Pipelines
        header is visible. Both conditions must be true for verification to pass.
        :return: bool: True if URL matches and Pipelines header is visible, False otherwise.
        Raises TimeoutError if URL doesn't match within the timeout.
        """
        return self.wait_for_url_to_endwith("pipelines/all-namespaces") and self.is_visible(self.PIPELINES_HEADER)
