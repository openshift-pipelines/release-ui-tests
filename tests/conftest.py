"""
Test configuration and fixtures.

This module configures pytest for BDD test execution, registers step definition plugins,
and implements custom collection hooks for test skipping and artifact capture.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import pytest
from playwright.async_api import Page

from framework.config.config import Config
from framework.fixtures.async_bridge import run_async

# Import fixtures from framework
from framework.fixtures.operator_fixtures import *  # noqa: F403, F401
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


def _resolve_fixture(item: pytest.Item, name: str) -> Optional[object]:
    """Fetch an already-created fixture for a finished test.

    pytest-bdd step functions pull their fixtures via `request.getfixturevalue` at step
    time, so `item.funcargs` holds only `request` and friends - never `config` or
    `playwright_page`. Reading funcargs alone silently disabled this whole hook.
    """
    if name in item.funcargs:
        return item.funcargs[name]
    request = item.funcargs.get("request")
    if request is None:
        return None
    try:
        return request.getfixturevalue(name)
    except Exception:  # noqa: BLE001 - never let diagnostics break reporting
        return None


def _record_failure_context(
    config: Config,
    safe_name: str,
    nodeid: str,
    pw_page: Page,
    event_loop: asyncio.AbstractEventLoop,
) -> None:
    """Write where the test died, for `python -m framework.agent.diagnose` to re-probe."""
    failures_dir = os.path.join(config.artifacts_dir, "failures")
    try:
        os.makedirs(failures_dir, exist_ok=True)
        context = {
            "nodeid": nodeid,
            "url": pw_page.url,
            "title": run_async(event_loop, pw_page.title()),
            "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(os.path.join(failures_dir, f"{safe_name}.json"), "w") as fh:
            json.dump(context, fh, indent=2)
    except Exception as exc:  # noqa: BLE001 - never let diagnostics break the run
        logger.warning("Failed to record failure context: %s", exc)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """Capture a screenshot when a test fails during the 'call' phase."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    config = _resolve_fixture(item, "config")
    if config is None:
        return

    pw_page = _resolve_fixture(item, "playwright_page")
    event_loop = _resolve_fixture(item, "playwright_event_loop")
    if pw_page is None or event_loop is None:
        return

    safe_name = report.nodeid.replace("/", "_").replace("::", "__").replace(" ", "_")

    # Recorded unconditionally: the URL the test died on cannot be recovered from the
    # traceback afterwards, and diagnosis needs it to re-probe the failing locator.
    _record_failure_context(config, safe_name, report.nodeid, pw_page, event_loop)

    if not config.capture_screenshots:
        return

    screenshots_dir = os.path.join(config.artifacts_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshots_dir, f"{safe_name}.png")

    try:
        run_async(event_loop, pw_page.screenshot(path=screenshot_path, full_page=True))
        logger.info("Screenshot saved: %s", screenshot_path)
    except Exception as exc:
        logger.warning("Failed to capture screenshot: %s", exc)
