"""
TaskRun CRUD Operations Test Steps.

BDD step definitions for creating, viewing, and deleting Tekton taskruns.
Follows SOLID principles with helper functions and reusable components.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

from pytest_bdd import parsers, scenarios, then, when

from framework.cli.openshift_cli import OpenShiftCLI
from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_loader import YamlLoader

# Register all scenarios from the taskrun_crud_operations feature file
FEATURE_FILE = Path(__file__).parent.parent / "features" / "taskrun_crud_operations.feature"
scenarios(FEATURE_FILE)


@when(parsers.parse('the user creates a task via cli from YAML file "{task_yaml_file}"'))
def create_task_via_cli(
    task_yaml_file: str, openshift_cli: OpenShiftCLI, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Create a Tekton Task via OpenShift CLI by loading YAML from test data.

    This step creates the prerequisite Task resource that a TaskRun will reference.
    The Task is applied to the current project/namespace using oc apply.

    :param str task_yaml_file: Name of task YAML file in test_data/tasks/
    :param OpenShiftCLI openshift_cli: CLI wrapper instance
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task creation fails
    """

    async def _step() -> None:
        # Load task YAML content using helper
        yaml_content = YamlLoader.load_task_yaml(task_yaml_file)

        # Apply the task YAML via CLI
        success = await openshift_cli.apply_yaml(yaml_content)
        assert success, f"Failed to create task from YAML file '{task_yaml_file}' via CLI"

        # Extract task name from YAML for logging
        metadata = YamlLoader.get_task_metadata(yaml_content)
        task_name = metadata.get("name", "unknown")

        # Log successful creation
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Successfully created task '{task_name}' via CLI")

    run_async(playwright_event_loop, _step())


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


@when(parsers.parse('the taskrun "{taskrun_name}" should appear in the taskruns list'))
@then(parsers.parse('the taskrun "{taskrun_name}" should appear in the taskruns list'))
def verify_taskrun_in_list(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a TaskRun with the given name appears in the TaskRuns list.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name prefix of the TaskRun to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if TaskRun is not visible in list
    """

    async def _step() -> None:
        # Verify TaskRun appears in list
        taskrun_visible = await page["tasks"].runs.verify_taskrun_in_list(taskrun_name)
        assert taskrun_visible, f"TaskRun '{taskrun_name}' does not appear in TaskRuns list"

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


@then(parsers.parse('the taskrun "{taskrun_name}" should not appear in the taskruns list'))
def verify_taskrun_not_in_list(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a TaskRun with the given name does NOT appear in the TaskRuns list.

    :param Dict[str, Any] page: Page object dictionary
    :param str taskrun_name: Name prefix of the TaskRun to verify absence
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if TaskRun is still visible in list
    """

    async def _step() -> None:
        # Wait for TaskRuns list to reload after deletion
        data_loaded = await page["tasks"].runs.verify_task_runs_tab_data_load()
        assert data_loaded, "TaskRuns list failed to reload after deletion"

        # Verify TaskRun does NOT appear in list
        taskrun_not_visible = await page["tasks"].runs.verify_taskrun_not_in_list(taskrun_name)
        assert taskrun_not_visible, f"TaskRun '{taskrun_name}' still appears in TaskRuns list after deletion"

    run_async(playwright_event_loop, _step())
