from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from framework.config.config import Config


class BasePage:
    def __init__(self, page: Page, config: Config) -> None:
        self.page = page
        self.config = config
        self.default_timeout = self.config.timeout_ms

    def click_element(self, locator: str) -> bool:
        """
        Uses locator.click(timeout=...), Waits up to the timeout for the element to be
        actionable (visible, enabled, stable), Raises TimeoutError if not clickable within the timeout
        :param str locator: name of the locator
        :return: bool: True if the element with mentioned locator is clickable, raises TimeoutError otherwise.
        """
        self.page.locator(locator).click(timeout=self.default_timeout)
        return True

    def fill_input(self, locator: str, value: str) -> bool:
        """
        Uses locator.fill(value, timeout=...). Waits up to the timeout for the element to be
        fillable (visible, enabled, stable), Raises TimeoutError if not fillable within the timeout.
        :param str locator: The locator string to identify the input element.
        :param str value: The text value to fill into the input element.
        :return: bool: True if the element with mentioned locator is fillable, raises TimeoutError otherwise.
        """
        self.page.locator(locator).fill(value, timeout=self.default_timeout)
        return True

    def is_visible(self, locator: str) -> bool:
        """
        Uses locator.wait_for(state="visible", timeout=...). Waits up to the timeout for the element
        to become visible. Returns False if timeout occurs instead of raising an exception.
        :param str locator: The locator string to identify the element.
        :return: bool: True if the element becomes visible within the timeout, False if timeout occurs.
        """
        try:
            self.page.locator(locator).wait_for(state="visible", timeout=self.default_timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_for_url_to_endwith(self, page: str) -> bool:
        """
        Uses page.wait_for_url(pattern, timeout=...). Waits up to the timeout for the URL to match
        the specified pattern (ending with the provided page path). Raises TimeoutError if URL doesn't
        match within the timeout.
        :param str page: The page path that the URL should end with (e.g., "pipelines/all-namespaces").
        :return: bool: True if URL matches within timeout, raises TimeoutError otherwise.
        """
        self.page.wait_for_url(f"**/{page}", timeout=self.default_timeout)
        return True

    def wait_for_url_to_contain(self, page: str) -> bool:
        """
        Uses page.wait_for_function(timeout=...). Waits up to the timeout for the JavaScript function
        to return a truthy value, checking if the current URL contains the specified page string.
        Raises TimeoutError if condition isn't met within the timeout.
        :param str page: The page string that should be contained in the URL (e.g., "oauth").
        :return: bool: True if URL contains the specified page string within timeout, raises TimeoutError otherwise.
        """
        self.page.wait_for_function(f"() => window.location.href.includes('{page}')", timeout=self.default_timeout)
        return True
