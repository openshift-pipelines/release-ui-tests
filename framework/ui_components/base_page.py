from typing import Optional, Pattern

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from framework.config.config import Config


class BasePage:
    def __init__(self, page: Page, config: Config) -> None:
        self.page = page
        self.config = config
        self.default_timeout = self.config.timeout_ms

    async def click_element(self, locator: str, timeout: Optional[int] = None) -> bool:
        """
        Uses locator.click() to click an element. Waits up to the specified timeout (or default
        timeout set on page) for the element to be actionable (visible, enabled, stable).
        The default timeout is configured via page.set_default_timeout() in the fixture using
        framework's APP_TIMEOUT.
        :param str locator: name of the locator
        :param Optional[int] timeout: Optional timeout in milliseconds. If not provided, uses the
            default timeout set on the page.
        :return: bool: True if the element with mentioned locator is clickable, raises TimeoutError otherwise.
        """
        loc = self.page.locator(locator)
        if timeout is not None:
            await loc.click(timeout=timeout)
        else:
            await loc.click()
        return True

    async def click_element_fast(self, locator: str, timeout: int = 5000) -> bool:
        """
        Fast click optimized for stable, visible elements (e.g., navigation buttons).

        Uses reduced timeout and skips some actionability checks for performance.
        Best for elements that are:
        - Already visible on page load
        - Not animated or moving
        - Stable navigation elements (sidebars, menus, etc.)

        Performance optimizations:
        - Shorter timeout (default 5s vs 90s)
        - no_wait_after=True (doesn't wait for navigation/network)
        - Force option available if needed

        Follows Single Responsibility: optimized for fast, stable clicks only.

        :param str locator: Element locator
        :param int timeout: Timeout in milliseconds (default 5000ms = 5s)
        :return: bool: True if click succeeds
        """
        import logging
        import time

        logger = logging.getLogger(__name__)

        start_time = time.time()
        logger.info(f"[FAST CLICK] Starting fast click for locator: {locator} with timeout: {timeout}ms")

        try:
            loc = self.page.locator(locator)

            # Quick visibility check first with short timeout
            visibility_start = time.time()
            await loc.wait_for(state="visible", timeout=timeout)
            visibility_elapsed = (time.time() - visibility_start) * 1000
            logger.info(f"[FAST CLICK] Element visible after {visibility_elapsed:.0f}ms")

            # Click with no_wait_after for speed (navigation elements don't need wait)
            click_start = time.time()
            await loc.click(timeout=timeout, no_wait_after=True)
            click_elapsed = (time.time() - click_start) * 1000

            total_elapsed = (time.time() - start_time) * 1000
            logger.info(
                f"[FAST CLICK] SUCCESS - Click completed in {click_elapsed:.0f}ms, total: {total_elapsed:.0f}ms"
            )
            return True
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.warning(
                f"[FAST CLICK] FAILED after {elapsed:.0f}ms - {type(e).__name__}: {str(e)}. "
                f"Falling back to regular click with {self.default_timeout}ms timeout"
            )
            # Fallback to regular click if fast click fails
            fallback_start = time.time()
            result = await self.click_element(locator, timeout=self.default_timeout)
            fallback_elapsed = (time.time() - fallback_start) * 1000
            logger.warning(f"[FAST CLICK] Fallback click took {fallback_elapsed:.0f}ms")
            return result

    async def fill_input(self, locator: str, value: str, timeout: Optional[int] = None) -> bool:
        """
        Uses locator.fill(value) to fill an input element. Waits up to the specified timeout (or
        default timeout set on page) for the element to be fillable (visible, enabled, stable).
        The default timeout is configured via page.set_default_timeout() in the fixture using
        framework's APP_TIMEOUT.
        :param str locator: The locator string to identify the input element.
        :param str value: The text value to fill into the input element.
        :param Optional[int] timeout: Optional timeout in milliseconds. If not provided, uses the
            default timeout set on the page.
        :return: bool: True if the element with mentioned locator is fillable, raises TimeoutError otherwise.
        """
        loc = self.page.locator(locator)
        if timeout is not None:
            await loc.fill(value, timeout=timeout)
        else:
            await loc.fill(value)
        return True

    async def is_visible(self, locator: str, timeout: Optional[int] = None) -> bool:
        """
        Uses locator.wait_for(state="visible") to check if an element is visible. Waits up to the
        specified timeout (or default timeout set on page) for the element to become visible.
        The default timeout is configured via page.set_default_timeout() in the fixture using
        framework's APP_TIMEOUT. Returns False if timeout occurs instead of raising an exception.
        :param str locator: The locator string to identify the element.
        :param Optional[int] timeout: Optional timeout in milliseconds. If not provided, uses the
            default timeout set on the page.
        :return: bool: True if the element becomes visible within the timeout, False if timeout occurs.
        """
        try:
            loc = self.page.locator(locator)
            if timeout is not None:
                await loc.wait_for(state="visible", timeout=timeout)
            else:
                await loc.wait_for(state="visible")
            return True
        except PlaywrightTimeoutError:
            return False

    async def wait_for_url_to_endwith(self, page_suffix: str, timeout: Optional[int] = None) -> bool:
        """
        Uses page.wait_for_url(pattern) to wait for the URL to match the specified pattern (ending
        with the provided page path). Waits up to the specified timeout (or default timeout set on
        page). The default timeout is configured via page.set_default_timeout() in the fixture using
        framework's APP_TIMEOUT. Raises TimeoutError if URL doesn't match within the timeout.
        :param str page_suffix: The page path that the URL should end with (e.g., "pipelines/all-namespaces").
        :param Optional[int] timeout: Optional timeout in milliseconds. If not provided, uses the
            default timeout set on the page.
        :return: bool: True if URL matches within timeout, raises TimeoutError otherwise.
        """
        if timeout is not None:
            await self.page.wait_for_url(f"**/{page_suffix}", timeout=timeout)
        else:
            await self.page.wait_for_url(f"**/{page_suffix}")
        return True

    async def wait_for_url_matching(self, pattern: Pattern[str], timeout: Optional[int] = None) -> bool:
        """
        Waits until the current URL matches the given regular expression (full URL is matched).
        :param pattern: Compiled regex, e.g. re.compile(r".*/pipelines/ns/[^/?#]+")
        :param timeout: Optional timeout in milliseconds.
        """
        if timeout is not None:
            await self.page.wait_for_url(pattern, timeout=timeout)
        else:
            await self.page.wait_for_url(pattern)
        return True

    async def wait_for_url_to_contain(self, page_fragment: str, timeout: Optional[int] = None) -> bool:
        """
        Uses page.wait_for_function() to wait for a JavaScript function to return a truthy value,
        checking if the current URL contains the specified page string. Waits up to the specified
        timeout (or default timeout set on page). The default timeout is configured via
        page.set_default_timeout() in the fixture using framework's APP_TIMEOUT. Raises
        TimeoutError if condition isn't met within the timeout.
        :param str page_fragment: The page string that should be contained in the URL (e.g., "oauth").
        :param Optional[int] timeout: Optional timeout in milliseconds. If not provided, uses the
            default timeout set on the page.
        :return: bool: True if URL contains the specified page string within timeout, raises TimeoutError otherwise.
        """
        if timeout is not None:
            await self.page.wait_for_function(
                f"() => window.location.href.includes('{page_fragment}')", timeout=timeout
            )
        else:
            await self.page.wait_for_function(f"() => window.location.href.includes('{page_fragment}')")
        return True

    async def _verify_page(self, expected_url_suffix: str, header_locator: str, page_name: str) -> bool:
        """
        Common verification method for page objects. Verifies that a page is currently displayed
        by checking URL pattern and header visibility
        :param str expected_url_suffix: The URL suffix that the page URL should end with
            (e.g., "dashboards", "pipelines/all-namespaces").
        :param str header_locator: The locator string for the page header element to verify visibility.
        :param str page_name: The name of the page for error messages (e.g., "Overview page",
            "Pipelines page").
        :return: bool: True if both URL and header checks pass.
        :raises AssertionError: With specific message if URL or header check fails.
        :raises TimeoutError: If URL doesn't match within the timeout.
        """
        if not await self.wait_for_url_to_endwith(expected_url_suffix):
            raise AssertionError(
                f"{page_name} verification failed: URL does not end with '{expected_url_suffix}'. "
                f"Current URL: {self.page.url}"
            )
        if not await self.is_visible(header_locator):
            raise AssertionError(
                f"{page_name} verification failed: Header element ({header_locator}) is not visible on the page."
            )
        return True

    async def _verify_page_regex(self, url_pattern: Pattern[str], header_locator: str, page_name: str) -> bool:
        """
        Like _verify_page but matches the URL against a regex (Playwright matches the full URL string).
        """
        try:
            await self.wait_for_url_matching(url_pattern)
        except PlaywrightTimeoutError:
            raise AssertionError(
                f"{page_name} verification failed: URL does not match pattern {url_pattern.pattern!r}. "
                f"Current URL: {self.page.url}"
            ) from None
        if not await self.is_visible(header_locator):
            raise AssertionError(
                f"{page_name} verification failed: Header element ({header_locator}) is not visible on the page."
            )
        return True

    async def _verify_data_load(self, locator: str, tab_name: str, no_data_locator: str = None) -> bool:
        """
        Common verification method for page objects to verify that data has finished loading.
        Waits until data is loaded by checking if the specified locator is visible.
        This method implements the Template Method pattern to avoid code duplication.
        First checks if a "no data" element is visible (if provided), which is a valid state.
        If no data element is visible, returns True immediately. Otherwise, continues with
        normal data load verification.
        :param str locator: Locator string for the data element to verify.
        :param str tab_name: Tab or page name for error messages (e.g., "Pipelines tab",
            "PipelineRuns tab", "Pipelines Overview page").
        :param str no_data_locator: Optional locator string for the "no data" element.
            If provided and visible, method returns True immediately (no data is a valid state).
            Uses a 10-second timeout for this check.
        :return: bool: True if data element becomes visible within the timeout, or if no data element is visible.
        :raises AssertionError: With specific message if data does not load within the timeout.
        :raises TimeoutError: If data element doesn't become visible within the timeout.
        """
        if no_data_locator is not None:
            try:
                await self.page.locator(no_data_locator).wait_for(state="visible", timeout=10000)
                return True
            except PlaywrightTimeoutError:
                pass

        if not await self.is_visible(locator):
            raise AssertionError(
                f"Data load verification failed for {tab_name}: Data element ({locator}) "
                f"did not become visible within the timeout."
            )
        return True
