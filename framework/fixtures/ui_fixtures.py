from typing import Any, Dict

import pytest
from playwright.sync_api import Page
from pytest import FixtureRequest

from framework.config.config import Config
from framework.ui_components.commons.left_navigation_bar import LeftNavigationBar
from framework.ui_components.commons.login_page import LoginPage
from framework.ui_components.overview_page import OverViewPage
from framework.ui_components.pipelines_page import PipelinesPage


@pytest.fixture(scope="session")
def config(request: FixtureRequest) -> object:
    """
    fixture that creates and returns a Config singleton instance.
    :param FixtureRequest request: Pytest fixture request object
    :return: Config: A singleton Config object with application configuration.
    """
    return Config()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: Dict[str, Any], request: FixtureRequest) -> Dict[str, Any]:
    """
    fixture that configures browser context arguments,
    By default, SSL errors are ignored (True). Set --ignore-ssl-errors=false to disable.
    Also maximizes the browser window by setting a large viewport size (1920x1080).
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


@pytest.fixture(scope="function")
def page(page: Page, config: Config) -> Dict[str, Any]:
    """
    fixture that injects custom application Page Objects.
    :param Page page: Raw page object
    :param Config config: Config object containing application configuration
    :return: Dict[str, Any]: Dictionary containing:
        - "raw_page": The raw Page object for direct access if needed.
        - "login": LoginPage instance for login-related operations.
        - "nav": LeftNavigationBar instance for navigation operations.
        - "overview": OverViewPage instance for overview page operations.
        - "pipelines": PipelinesPage instance for pipelines page operations.
    """
    return {
        "raw_page": page,
        "login": LoginPage(page, config),
        "nav": LeftNavigationBar(page, config),
        "overview": OverViewPage(page, config),
        "pipelines": PipelinesPage(page, config),
    }
