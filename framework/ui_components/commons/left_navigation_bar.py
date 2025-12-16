from framework.ui_components.base_page import BasePage


class LeftNavigationBar(BasePage):
    PIPELINES_BUTTON = '[data-test="nav-pipelines"]'
    NAV_PIPELINES_LINK = 'a:has-text("Pipelines")'
    KUBE_ADMIN_MENU = 'button[aria-label="User menu"]'

    def verify_successful_login(self) -> bool:
        """
        Verifies that login was successful by checking URL and user menu visibility.
        First waits for URL to end with "dashboards", then checks if the KubeAdmin user menu
        is visible. Returns False if the menu is not visible within the timeout.
        :return: bool: True if URL matches and user menu is visible, False if menu is not visible.
        Raises TimeoutError if URL doesn't match within the timeout.
        """
        return self.wait_for_url_to_endwith("dashboards") and self.is_visible(self.KUBE_ADMIN_MENU)

    def navigate_to_pipelines(self) -> bool:
        """
        Navigates to the Pipelines page by clicking the Pipelines button and then the Pipelines link.
        Uses click_element() for both actions, which waits up to the configured timeout for elements
        to be clickable. This is a two-step navigation process. Returns True only if both clicks succeed.
        :return: bool: True if both navigation clicks succeed, False if any click fails or raises TimeoutError.
        """
        return self.click_element(self.PIPELINES_BUTTON) and self.click_element(self.NAV_PIPELINES_LINK)
