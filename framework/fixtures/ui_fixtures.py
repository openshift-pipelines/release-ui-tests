import asyncio
from collections.abc import AsyncGenerator
from typing import Any, Dict

import pytest
import pytest_asyncio
from playwright.async_api import Browser, Page
from pytest import FixtureRequest

import framework.ui_components.overview_page as overview_page_module
from framework.config.config import Config
from framework.ui_components.commons.left_navigation_bar import LeftNavigationBar
from framework.ui_components.commons.login_page import LoginPage
from framework.ui_components.overview_page import OverViewPage
from framework.ui_components.pipelines_overview_page import PipelinesOverViewPage
from framework.ui_components.pipelines_page import PipelinesPage
from framework.ui_components.tasks_page import TasksPage
from framework.ui_components.triggers_page import TriggersPage


@pytest.fixture(scope="session")
def config(request: FixtureRequest) -> object:
    """
    fixture that creates and returns a Config singleton instance.
    :param FixtureRequest request: Pytest fixture request object
    :return: Config: A singleton Config object with application configuration.
    """
    return Config()


@pytest.fixture(scope="session")
def playwright_event_loop(request: FixtureRequest) -> asyncio.AbstractEventLoop:
    """
    Session event loop used by pytest-playwright-asyncio and synchronous BDD steps.
    """
    return request.getfixturevalue("_session_event_loop")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: Dict[str, Any], request: FixtureRequest) -> Dict[str, Any]:
    """
    fixture that configures browser context arguments,
    By default, SSL errors are ignored (True). Set --ignore-ssl-errors=false to disable.
    Also maximizes the browser window by setting a large viewport size (1920x1080).
    Note: Navigation timeout is set separately in the context fixture since it's not a valid
    parameter for browser.new_context().
    :param Dict[str, Any] browser_context_args: Default browser context arguments from Playwright.
    :param FixtureRequest request: Pytest fixture request object (automatically injected).
    :return: Dict[str, Any]: Updated browser context arguments with SSL and viewport configuration.
    """
    ignore_ssl = request.config.getoption("--ignore-ssl-errors", default=True)

    return {
        **browser_context_args,
        "ignore_https_errors": ignore_ssl,
        "viewport": {"width": 1920, "height": 1080},  # Maximize browser window
    }


@pytest.fixture(scope="module")
def bdd_openshift_console_session() -> Dict[str, Any]:
    """
    Per-module (feature-registration module) state for BDD steps.
    Used to run full OpenShift login only once per feature file when the Background step
    ``the user is logged into openshift console with auth kube:admin`` is used.
    """
    return {"kube_admin_logged_in": False}


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def playwright_page(
    browser: Browser,
    browser_context_args: Dict[str, Any],
) -> AsyncGenerator[Page, None]:
    """
    One Playwright Page (and its BrowserContext) per test module that registers scenarios.
    Reuse the session ``browser`` from pytest-playwright-asyncio; isolate cookies/storage per feature
    file by registering each ``.feature`` from its own step module (one ``scenarios(...)`` module
    per feature is the supported layout).

    Uses ``browser.new_context`` directly because the plugin's ``new_context`` fixture is
    function-scoped and cannot be requested from module-scoped fixtures.
    """
    context = await browser.new_context(**browser_context_args)
    pw_page = await context.new_page()
    try:
        yield pw_page
    finally:
        await context.close()


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def page(playwright_page: Page, config: Config) -> Dict[str, Any]:
    """
    fixture that injects custom application Page Objects.
    Scoped to the test module so all scenarios from the same feature registration share one
    browser context. Each module that calls ``scenarios()`` gets a new context.

    Sets default timeout for all page actions (click, fill, wait_for, etc.) and navigation
    operations (goto, reload, etc.) to use framework's configured timeout value (from APP_TIMEOUT
    env var, default 90000ms).
    :param Page playwright_page: Raw Playwright page for this module's browser context.
    :param Config config: Config object containing application configuration
    :return: Dict[str, Any]: Dictionary containing:
        - "raw_page": The raw Page object for direct access if needed.
        - "login": LoginPage instance for login-related operations.
        - "nav": LeftNavigationBar instance for navigation operations.
        - "overview": OverViewPage instance for overview page operations.
        - "pipelines_overview": PipelinesOverViewPage instance for pipelines overview page operations.
        - "pipelines": PipelinesPage instance for pipelines page operations.
        - "tasks": TasksPage instance for tasks page operations.
        - "triggers": TriggersPage instance for triggers page operations.
    """
    overview_page_module._tour_skipped = False

    playwright_page.set_default_timeout(config.timeout_ms)
    playwright_page.context.set_default_navigation_timeout(config.timeout_ms)

    return {
        "raw_page": playwright_page,
        "login": LoginPage(playwright_page, config),
        "nav": LeftNavigationBar(playwright_page, config),
        "overview": OverViewPage(playwright_page, config),
        "pipelines_overview": PipelinesOverViewPage(playwright_page, config),
        "pipelines": PipelinesPage(playwright_page, config),
        "tasks": TasksPage(playwright_page, config),
        "triggers": TriggersPage(playwright_page, config),
    }
