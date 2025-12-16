from framework.ui_components.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = "[id='inputUsername']"
    PASSWORD_INPUT = "[id='inputPassword']"
    LOGIN_BUTTON = 'button:has-text("Log in")'
    # LOGIN_BUTTON = "button[id='co-login-button']"

    def goto(self) -> bool:
        """
        Navigates to the login page using the base URL from configuration.
        Uses page.goto() to navigate to the configured CONSOLE_URL.
        :return: bool: True if navigation is successful.
        """
        self.page.goto(self.config.base_url)
        return True

    def verify_successful_navigation_to_login_page(self) -> bool:
        """
        Verifies that navigation to the login page was successful by checking if the URL
        contains "oauth". Uses wait_for_url_to_contain() which waits up to the configured
        timeout for the URL to contain the specified string. Raises TimeoutError if not found.
        :return: bool: True if URL contains "oauth" within the timeout, raises TimeoutError otherwise.
        """
        return self.wait_for_url_to_contain("oauth")

    def login(self) -> bool:
        """
        Performs login action by filling username and password fields, then clicking the login button.
        Uses fill_input() to enter credentials from configuration, then click_element() to submit.
        All operations wait up to the configured timeout for elements to be actionable.
        Returns True only if all three operations (username fill, password fill, button click) succeed.
        :return: bool: True if all login operations succeed, False if any operation fails or raises TimeoutError.
        """
        return (
            self.fill_input(self.USERNAME_INPUT, self.config.username)
            and self.fill_input(self.PASSWORD_INPUT, self.config.password)
            and self.click_element(self.LOGIN_BUTTON)
        )
