"""
TaskRun Validation Test Steps.

BDD step definitions for validating TaskRun details, YAML, and logs pages.
Tests the display and visibility of TaskRun page elements and content.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

from pytest_bdd import parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async

# Register all scenarios from the taskrun_crud_operations feature file
FEATURE_FILE = Path(__file__).parent.parent / "features" / "taskrun_crud_operations.feature"
scenarios(FEATURE_FILE)

logger = logging.getLogger(__name__)


# ===========================
# Tab Navigation Steps
# ===========================


@when(parsers.parse('the user navigates to taskrun YAML tab for taskrun "{taskrun_name}"'))
def navigate_to_taskrun_yaml_tab(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Navigate to the YAML tab on TaskRun details page.

    Starting point: TaskRun details page (from previous scenario).
    Clicks the YAML tab to switch view.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name prefix of the TaskRun (used for context, not navigation)
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if tab navigation fails
    """

    async def _step() -> None:
        # Wait for details page to be fully loaded
        await page["raw_page"].wait_for_load_state("networkidle")

        # Navigate to YAML tab using base class method
        yaml_tab_clicked = await page["tasks"].taskrun.details.navigate_to_yaml_tab()
        assert yaml_tab_clicked, f"Failed to navigate to YAML tab for TaskRun '{taskrun_name}'"

        # Wait for YAML editor to load
        await page["raw_page"].wait_for_timeout(1000)

        logger.info(f"Navigated to YAML tab for TaskRun '{taskrun_name}'")

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user navigates to taskrun logs tab for taskrun "{taskrun_name}"'))
def navigate_to_taskrun_logs_tab(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Navigate to the Logs tab on TaskRun page.

    Starting point: TaskRun YAML page (from previous scenario).
    Clicks the Logs tab to switch view.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name prefix of the TaskRun (used for context, not navigation)
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if tab navigation fails
    """

    async def _step() -> None:
        # Wait for YAML page to be fully loaded
        await page["raw_page"].wait_for_load_state("networkidle")

        # Navigate to Logs tab using base class method
        logs_tab_clicked = await page["tasks"].taskrun.yaml.navigate_to_logs_tab()
        assert logs_tab_clicked, f"Failed to navigate to Logs tab for TaskRun '{taskrun_name}'"

        # Wait for logs content to load
        await page["raw_page"].wait_for_timeout(2000)

        logger.info(f"Navigated to Logs tab for TaskRun '{taskrun_name}'")

    run_async(playwright_event_loop, _step())


# ===========================
# Details Page Validation Steps
# ===========================


@then("the taskrun details page should display namespace")
def verify_taskrun_namespace_displayed(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the TaskRun details page displays a namespace.

    Checks that the namespace field is visible and contains a non-empty value.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if namespace is not displayed
    """

    async def _step() -> None:
        # Get namespace from details page
        namespace = await page["tasks"].taskrun.details.get_namespace()

        # Verify namespace is not empty
        assert namespace, "TaskRun details page does not display namespace (empty value)"
        assert len(namespace.strip()) > 0, "TaskRun details page namespace is empty or whitespace only"

        logger.info(f"TaskRun details page displays namespace: '{namespace}'")

    run_async(playwright_event_loop, _step())


@then("the taskrun details page should display status")
def verify_taskrun_status_displayed(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the TaskRun details page displays a status.

    Checks that the status field is visible and contains a non-empty value
    (e.g., "Succeeded", "Running", "Failed").

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if status is not displayed
    """

    async def _step() -> None:
        # Get status from details page
        status = await page["tasks"].taskrun.details.get_status()

        # Verify status is not empty
        assert status, "TaskRun details page does not display status (empty value)"
        assert len(status.strip()) > 0, "TaskRun details page status is empty or whitespace only"

        logger.info(f"TaskRun details page displays status: '{status}'")

    run_async(playwright_event_loop, _step())


@then("the taskrun details page should display labels")
def verify_taskrun_labels_displayed(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the TaskRun details page displays labels.

    Checks that the labels section is visible and contains at least one label.
    Labels are displayed as key=value badges.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if no labels are displayed
    """

    async def _step() -> None:
        # Get labels from details page
        labels = await page["tasks"].taskrun.details.get_labels()

        # Verify labels dictionary is not empty
        assert labels, "TaskRun details page does not display any labels (empty dictionary)"
        assert len(labels) > 0, "TaskRun details page has no labels displayed"

        logger.info(f"TaskRun details page displays {len(labels)} label(s): {list(labels.keys())}")

    run_async(playwright_event_loop, _step())


@then("the taskrun details page should display annotations count")
def verify_taskrun_annotations_displayed(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the TaskRun details page displays annotations count.

    Checks that the annotations section is visible with a count indicator.
    The count should be >= 0 (some TaskRuns may have no annotations).

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if annotations count is not displayed
    """

    async def _step() -> None:
        # Get annotations count from details page
        annotations_count = await page["tasks"].taskrun.details.get_annotations_count()

        # Verify count is a valid non-negative integer
        assert isinstance(annotations_count, int), (
            f"TaskRun details page annotations count is not an integer: {type(annotations_count)}"
        )
        assert annotations_count >= 0, f"TaskRun details page annotations count is negative: {annotations_count}"

        logger.info(f"TaskRun details page displays annotations count: {annotations_count}")

    run_async(playwright_event_loop, _step())


# ===========================
# YAML Page Validation Steps
# ===========================


@then("the taskrun YAML editor should be visible")
def verify_taskrun_yaml_editor_visible(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the YAML editor is visible on the TaskRun YAML page.

    Checks that the Monaco editor component is displayed and ready for interaction.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if YAML editor is not visible
    """

    async def _step() -> None:
        # Check if YAML editor is visible
        yaml_editor_visible = await page["tasks"].taskrun.yaml.is_yaml_editor_visible()

        # Verify YAML editor is visible
        assert yaml_editor_visible, "TaskRun YAML editor is not visible on YAML page"

        logger.info("TaskRun YAML editor is visible on YAML page")

    run_async(playwright_event_loop, _step())


# ===========================
# Logs Page Validation Steps
# ===========================


@then("the taskrun logs container should be visible")
def verify_taskrun_logs_container_visible(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the logs container is visible on the TaskRun logs page.

    Checks that the main logs content area is displayed.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if logs container is not visible
    """

    async def _step() -> None:
        # Check if logs container is visible
        logs_container_visible = await page["tasks"].taskrun.logs.is_logs_container_visible()

        # Verify logs container is visible
        assert logs_container_visible, "TaskRun logs container is not visible on logs page"

        logger.info("TaskRun logs container is visible on logs page")

    run_async(playwright_event_loop, _step())


@then("the taskrun step navigation should be visible")
def verify_taskrun_step_navigation_visible(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the step navigation sidebar is visible on the TaskRun logs page.

    The step navigation allows users to filter logs by individual task step.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if step navigation is not visible
    """

    async def _step() -> None:
        # Check if step navigation is visible
        step_navigation_visible = await page["tasks"].taskrun.logs.is_step_navigation_visible()

        # Verify step navigation is visible
        assert step_navigation_visible, "TaskRun step navigation sidebar is not visible on logs page"

        logger.info("TaskRun step navigation is visible on logs page")

    run_async(playwright_event_loop, _step())


@then(parsers.parse("the taskrun should have at least {count:d} step available"))
def verify_taskrun_steps_available(
    page: Dict[str, Any], count: int, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the TaskRun has at least N steps available in the logs navigation.

    Steps are displayed in the sidebar and correspond to the individual task steps
    that were executed.

    :param Dict[str, Any] page: Page object dictionary
    :param int count: Minimum number of steps expected
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if fewer than N steps are available
    """

    async def _step() -> None:
        # Get available steps from logs page
        available_steps = await page["tasks"].taskrun.logs.get_available_steps()

        # Verify we have at least the expected number of steps
        actual_count = len(available_steps)
        assert actual_count >= count, (
            f"TaskRun has {actual_count} step(s) available, but expected at least {count}. "
            f"Available steps: {available_steps}"
        )

        logger.info(f"TaskRun has {actual_count} step(s) available: {available_steps}")

    run_async(playwright_event_loop, _step())


@then("the taskrun logs content should not be empty")
def verify_taskrun_logs_content_not_empty(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the TaskRun logs content is not empty.

    Checks that the logs container contains actual log output from the executed steps.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if logs content is empty
    """

    async def _step() -> None:
        # Get logs content from logs page
        logs_content = await page["tasks"].taskrun.logs.get_logs_content()

        # Verify logs content is not empty
        assert logs_content, "TaskRun logs content is empty (no text)"
        assert len(logs_content.strip()) > 0, "TaskRun logs content contains only whitespace"

        # Log first 100 characters of logs for verification
        preview = logs_content.strip()[:100]
        logger.info(f"TaskRun logs content is not empty. Preview: '{preview}...'")

    run_async(playwright_event_loop, _step())
