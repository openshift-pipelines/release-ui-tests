"""
TaskRun CRUD Operations Test Steps.

BDD step definitions for creating, viewing, and deleting Tekton taskruns.
Follows SOLID principles with helper functions and reusable components.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict

from pytest_bdd import parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_loader import YamlLoader
from framework.utils.retry import retry_on_exception

# Register all scenarios from the taskrun_crud_operations feature file
FEATURE_FILE = Path(__file__).parent.parent / "features" / "taskrun_crud_operations.feature"
scenarios(FEATURE_FILE)

# Shared steps (create task via CLI, TaskRun list presence) live in test_shared_steps.py


@when(parsers.parse('the user creates a taskrun from YAML file "{yaml_file}"'))
def create_taskrun_from_yaml(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop, config: object
) -> None:
    """
    Create a TaskRun by loading YAML from test data and submitting via UI.

    Always navigates to TaskRuns tab first to ensure consistent starting state
    (browser session is shared between scenarios, so we don't know which page we're on).

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/taskruns/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if creation fails
    """

    async def _step() -> None:
        # Load YAML content using helper
        yaml_content = YamlLoader.load_taskrun_yaml(yaml_file)

        # Navigate to TaskRuns tab first (session is shared between scenarios)
        # Check if Pipelines menu is expanded
        is_expanded = await page["nav"].is_pipelines_menu_expanded()
        if not is_expanded:
            await page["nav"].click_pipelines_button()
            await page["raw_page"].wait_for_timeout(500)

        # Navigate to Tasks page
        await page["nav"].navigate_to_tasks()

        # Wait for Tasks page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Navigate to TaskRuns tab
        await page["tasks"].list.navigate_to_task_runs_tab()

        # Wait for TaskRuns tab data to load
        data_loaded = await page["tasks"].runs.verify_task_runs_tab_data_load()
        assert data_loaded, "TaskRuns list failed to load before creating TaskRun"

        # Click Create button
        create_clicked = await page["tasks"].list.click_create_button()
        assert create_clicked, "Failed to click Create button on TaskRuns tab"

        # Wait for dropdown menu to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "TaskRun" option from dropdown
        taskrun_option_clicked = await page["tasks"].list.click_create_task_run_menu_item()
        assert taskrun_option_clicked, "Failed to click 'TaskRun' menu item from Create dropdown"

        # Wait for Create TaskRun page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Verify we're on the Create TaskRun page
        on_create_page = await page["tasks"].create_run.verify_on_page()
        assert on_create_page, "Failed to navigate to Create TaskRun page"

        # Fill YAML editor using MonacoEditor component directly
        yaml_filled = await page["tasks"].create_run.monaco_editor.set_content(yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{yaml_file}'"

        # Click Create button to submit
        create_submitted = await page["tasks"].create_run.click_create()
        assert create_submitted, "Failed to click Create button to submit TaskRun YAML"

        # Wait for redirect to TaskRun details page
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

    run_async(playwright_event_loop, _step())


@then(parsers.parse('validate user is redirected to taskrun details page for taskrun "{taskrun_name}"'))
def validate_taskrun_details(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Validate user is redirected to the TaskRun details page after creating TaskRun.

    Note: taskrun_name may be a partial name prefix (e.g., "simple-taskrun-") when using generateName.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name prefix of the TaskRun to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if navigation fails
    """

    async def _step() -> None:
        # Wait for TaskRun details page to load
        await page["raw_page"].wait_for_load_state("networkidle")

        # Verify we're on the TaskRun details page
        on_page = await page["tasks"].taskrun.details.verify_on_page()
        assert on_page, f"Failed to navigate to TaskRun details page for '{taskrun_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user navigates to taskrun details page for taskrun "{taskrun_name}"'))
def navigate_to_task_details_page_for_given_task(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a task with the given name appears in the tasks list.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name of the task to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task is not visible in list
    """

    async def _step() -> None:
        await page["tasks"].taskrun.list.click_on_given_taskrun_in_list(taskrun_name=taskrun_name)

        # Wait for task details page to load
        await page["raw_page"].wait_for_load_state("networkidle")

        # Verify we're on the task details page
        on_page = await page["tasks"].taskrun.details.verify_on_page()
        assert on_page, f"Failed to navigate to taskrun details page for '{taskrun_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the taskrun details page should display heading with taskrun name as "{taskrun_name}"'))
@then(parsers.parse('the taskrun details page should display heading with taskrun name as "{taskrun_name}"'))
def verify_task_run_details_heading_name(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task run details page displays the correct task name.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Expected task run name to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if name does not match
    """

    async def _step() -> None:
        # Get displayed task name
        displayed_name = await page["tasks"].taskrun.details.get_taskrun_heading_name()

        # Verify it starts with the expected prefix (for generateName resources)
        assert displayed_name.startswith(taskrun_name.rstrip("-")), (
            f"TaskRun details page displays name '{displayed_name}' but expected name starting with '{taskrun_name}'"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the taskrun details page should display the taskrun name as "{taskrun_name}"'))
@then(parsers.parse('the taskrun details page should display the taskrun name as "{taskrun_name}"'))
def verify_task_run_details_name(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task run details page displays the correct task name.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Expected task run name to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if name does not match
    """

    async def _step() -> None:
        # Get displayed task name
        displayed_name = await page["tasks"].taskrun.details.get_taskrun_name()

        # Verify it starts with the expected prefix (for generateName resources)
        assert displayed_name.startswith(taskrun_name.rstrip("-")), (
            f"TaskRun details page displays name '{displayed_name}' but expected name starting with '{taskrun_name}'"
        )

    run_async(playwright_event_loop, _step())


@then(parsers.parse("the taskrun details page should display namespace"))
def verify_task_namespace(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the task details page displays the correct namespace.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if namespace does not match
    """

    async def _step() -> None:
        # Get displayed task name
        displayed_name = await page["tasks"].taskrun.details.get_namespace()

        # Verify it matches expected name
        assert "release-ui-test" in displayed_name, (
            f"TaskRun details page namespace value should contain release-ui-test but found '{displayed_name}'"
        )

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the taskrun details page should contain labels with value "{labels}"'))
@retry_on_exception(retries=3, delay_seconds=2.0)
def verify_taskrun_labels(page: Dict[str, Any], labels: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the task details page displays the specified label.

    Retries briefly so the details pane can catch up after a labels save.

    :param Dict[str, Any] page: Page object dictionary
    :param str labels: JSON object containing the labels to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if label is not found
    """

    async def _step() -> None:
        try:
            expected_labels = json.loads(labels)
        except json.JSONDecodeError as error:
            raise AssertionError(f"Invalid expected labels JSON '{labels}': {error.msg}") from error

        assert isinstance(expected_labels, dict), f"Expected labels must be a JSON object, but received '{labels}'"

        # inner_text() can contain newlines or spaces around the equals sign.
        displayed_labels_value = await page["tasks"].taskrun.details.get_labels_value()
        normalized_labels_value = re.sub(r"\s*=\s*", "=", displayed_labels_value)
        missing_labels = [
            f"{key}={value}"
            for key, value in expected_labels.items()
            if f"{key}={value}" not in normalized_labels_value
        ]
        assert not missing_labels, (
            f"TaskRun details page labels missing {missing_labels}; displayed labels were '{displayed_labels_value}'"
        )

    run_async(playwright_event_loop, _step())


@then(
    parsers.parse(
        'the taskrun details page should contain appropriate count of annotations value as "{annotations_count}"'
    )
)
@retry_on_exception(retries=3, delay_seconds=2.0)
def verify_taskrun_annotations_count(
    page: Dict[str, Any], annotations_count: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task details page displays the expected annotation count.

    Retries briefly so the details pane can catch up after an annotations save.

    :param Dict[str, Any] page: Page object dictionary
    :param str annotations_count: count of the expected annotations
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if the annotation count does not match
    """

    async def _step() -> None:

        annotations_count_value = await page["tasks"].taskrun.details.get_annotations_count_value()
        count_match = re.search(r"\d+", annotations_count_value)
        assert count_match, f"Could not extract an annotation count from '{annotations_count_value}'"

        displayed_count = int(count_match.group())
        expected_count = int(annotations_count)
        assert displayed_count >= expected_count, (
            f"TaskRun details page displays {displayed_count} annotations, "
            f"but expected to be greater then {expected_count}"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the taskrun "{taskrun_name}" is executed with status "{taskrun_status}"'))
@then(parsers.parse('the taskrun "{taskrun_name}" is executed with status "{taskrun_status}"'))
def verify_taskrun_status_of_given_task_name(
    page: Dict[str, Any], taskrun_name: str, taskrun_status: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a TaskRun with the given name appears with given status in the TaskRuns list.

    Polls the TaskRun status for up to 60 seconds with 20-second intervals to handle
    asynchronous execution. Waits for status to change from "Running" to expected status.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name of the TaskRun to verify
    :param str taskrun_status: Expected status of the TaskRun (e.g., 'Succeeded', 'Failed')
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if TaskRun status does not match expected within timeout
    """

    async def _step() -> None:
        import logging

        logger = logging.getLogger(__name__)

        # Retry configuration
        max_wait_seconds = 60
        retry_interval_seconds = 20
        max_attempts = (max_wait_seconds // retry_interval_seconds) + 1  # 3 attempts total

        actual_status = ""

        for attempt in range(1, max_attempts + 1):
            # Wait for TaskRuns list data to load
            data_loaded = await page["tasks"].runs.verify_task_runs_tab_data_load()
            assert data_loaded, "TaskRuns list failed to load before checking status"

            # Get the status of the TaskRun
            actual_status = await page["tasks"].runs.get_taskrun_status(taskrun_name)

            logger.info(f"Attempt {attempt}/{max_attempts}: TaskRun '{taskrun_name}' status is '{actual_status}'")

            # Check if status matches expected (case-insensitive)
            if actual_status.lower() == taskrun_status.lower():
                logger.info(f"TaskRun '{taskrun_name}' reached expected status '{taskrun_status}'")
                return  # Success - status matches

            # If not the last attempt and status is still Running, wait and retry
            if attempt < max_attempts:
                logger.info(
                    f"Status is '{actual_status}', expected '{taskrun_status}'. "
                    f"Waiting {retry_interval_seconds}s before retry..."
                )
                await asyncio.sleep(retry_interval_seconds)

        # All attempts exhausted - status still doesn't match
        assert False, (
            f"TaskRun '{taskrun_name}' has status '{actual_status}' after {max_wait_seconds}s, "
            f"but expected '{taskrun_status}'"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse("the user opens edits labels popup of taskrun from taskrun details page"))
def open_taskrun_edit_labels_popup(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Open the edit labels dialog on the already opened TaskRun details page.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if the labels popup cannot be opened
    """

    async def _step() -> None:
        taskrun_visible = await page["tasks"].taskrun.details.click_edit_labels()
        assert taskrun_visible, "Unable to open edit labels popup from TaskRun details page"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user adds labels to taskrun "{taskrun_name}" with labels "{labels}"'))
def add_task_labels(
    page: Dict[str, Any], taskrun_name: str, labels: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Append JSON label pairs to the open Edit labels dialog."""

    async def _step() -> None:
        try:
            new_labels = json.loads(labels)
        except json.JSONDecodeError as error:
            raise AssertionError(f"Invalid labels JSON '{labels}': {error.msg}") from error

        assert isinstance(new_labels, dict), f"Expected labels must be a JSON object, but received '{labels}'"
        labels_saved = await page["tasks"].taskrun.details.labels_modal.add_labels(new_labels)
        assert labels_saved, f"Failed to add labels to taskrun '{taskrun_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse("the user opens edits annotations popup of taskrun from taskrun details page"))
def open_taskrun_edit_annotations_popup(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Open the edit annotations dialog on the already opened TaskRun details page.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if the annotations popup cannot be opened
    """

    async def _step() -> None:
        taskrun_visible = await page["tasks"].taskrun.details.click_edit_annotations()
        assert taskrun_visible, "Unable to open annotations popup from TaskRun details page"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user adds new annotations to taskrun "{taskrun_name}" with annotations "{annotations}"'))
def add_task_annotations(
    page: Dict[str, Any], taskrun_name: str, annotations: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Append JSON annotation pairs to the open Edit annotations dialog."""

    async def _step() -> None:
        try:
            new_annotations = json.loads(annotations)
        except json.JSONDecodeError as error:
            raise AssertionError(f"Invalid annotations JSON '{annotations}': {error.msg}") from error

        assert isinstance(new_annotations, dict), (
            f"Expected annotations must be a JSON object, but received '{annotations}'"
        )
        annotations_saved = await page["tasks"].taskrun.details.annotations_modal.add_annotations(new_annotations)
        assert annotations_saved, f"Failed to add annotations to taskrun '{taskrun_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user deletes the taskrun "{taskrun_name}"'))
def delete_taskrun(page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Delete a TaskRun using the kebab menu and confirmation modal.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name prefix of the TaskRun to delete
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if deletion fails
    """

    async def _step() -> None:
        # Navigate to TaskRuns tab
        # Check if Pipelines menu is expanded first
        is_expanded = await page["nav"].is_pipelines_menu_expanded()
        if not is_expanded:
            await page["nav"].click_pipelines_button()
            await page["raw_page"].wait_for_timeout(500)

        # Navigate to Tasks page
        await page["nav"].navigate_to_tasks()

        # Wait for page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Navigate to TaskRuns tab
        await page["tasks"].list.navigate_to_task_runs_tab()

        # Wait for TaskRuns tab data to load
        data_loaded = await page["tasks"].runs.verify_task_runs_tab_data_load()
        assert data_loaded, "TaskRuns list failed to load data before deletion"

        # Click kebab menu for the TaskRun
        kebab_clicked = await page["tasks"].runs.click_taskrun_kebab_menu(taskrun_name)
        assert kebab_clicked, f"Failed to click kebab menu for TaskRun '{taskrun_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Delete TaskRun" menu item
        delete_clicked = await page["tasks"].runs.click_delete_taskrun_menu_item()
        assert delete_clicked, f"Failed to click 'Delete TaskRun' menu item for '{taskrun_name}'"

        # Wait for confirmation modal to appear and confirm deletion using modal component
        confirmation_success = await page["modal"].confirm_deletion(taskrun_name)
        assert confirmation_success, f"Failed to confirm deletion of TaskRun '{taskrun_name}'"

        # Wait for deletion to complete
        await page["raw_page"].wait_for_timeout(2000)

    run_async(playwright_event_loop, _step())
