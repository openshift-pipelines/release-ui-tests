"""
Test configuration and fixtures.

This module configures pytest for BDD test execution, registers step definition plugins,
and implements custom collection hooks for test skipping and artifact capture.
"""

import logging
import os

import pytest

from framework.fixtures.async_bridge import run_async

# Import fixtures from framework
from framework.fixtures.ui_fixtures import *  # noqa: F403, F401

logger = logging.getLogger(__name__)

# Register step definition plugins
# test_shared_steps contains steps used across multiple feature files
pytest_plugins = [
    "tests.steps.test_auth_steps",
    "tests.steps.test_navigation_steps",
    "tests.steps.test_shared_steps",
]


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """
    Automatically skip test scenarios tagged with @skip or @known_bug in feature files.

    This hook runs after test collection and adds pytest.mark.skip to any scenario
    that has the @skip or @known_bug tag in the feature file. The skip reason is
    configured to point users to the feature file for bug details.

    :param config: pytest config object
    :param items: List of collected test items
    """
    for item in items:
        # Check if scenario has @skip tag
        if "skip" in item.keywords:
            item.add_marker(
                pytest.mark.skip(reason="Scenario skipped - see feature file comments for known bug details")
            )
        # Also handle @known_bug as alias for @skip
        elif "known_bug" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="Known bug - see feature file comments for tracking information"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Capture a screenshot when a test fails during the 'call' phase."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    config = item.funcargs.get("config")
    if config is None or not config.capture_screenshots:
        return

    pw_page = item.funcargs.get("playwright_page")
    event_loop = item.funcargs.get("playwright_event_loop")
    if pw_page is None or event_loop is None:
        return

    screenshots_dir = os.path.join(config.artifacts_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    safe_name = report.nodeid.replace("/", "_").replace("::", "__").replace(" ", "_")
    screenshot_path = os.path.join(screenshots_dir, f"{safe_name}.png")

    try:
        run_async(event_loop, pw_page.screenshot(path=screenshot_path, full_page=True))
        logger.info("Screenshot saved: %s", screenshot_path)
    except Exception as exc:
        logger.warning("Failed to capture screenshot: %s", exc)
