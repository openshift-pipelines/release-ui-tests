"""
PipelineRun CRUD Operations Test Steps.

BDD step definitions for creating, viewing, and deleting Tekton pipelineruns.
Follows SOLID principles with helper functions and reusable components.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

from pytest_bdd import parsers, scenarios, then, when

from framework.cli.openshift_cli import OpenShiftCLI
from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_loader import YamlLoader

# Register all scenarios from the pipelinerun_crud_operations feature file
FEATURE_FILE = Path(__file__).parent.parent / "features" / "pipelinerun_crud_operations.feature"
scenarios(FEATURE_FILE)


@when(parsers.parse('the user creates a pipeline via cli from YAML file "{pipeline_yaml_file}"'))
def create_pipeline_via_cli(
    pipeline_yaml_file: str, openshift_cli: OpenShiftCLI, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Create a Tekton Pipeline via OpenShift CLI by loading YAML from test data.

    This step creates the prerequisite Pipeline resource that a PipelineRun will reference.
    The Pipeline is applied to the current project/namespace using oc apply.

    :param str pipeline_yaml_file: Name of pipeline YAML file in test_data/pipelines/
    :param OpenShiftCLI openshift_cli: CLI wrapper instance
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if pipeline creation fails
    """

    async def _step() -> None:
        # Load pipeline YAML content using helper
        yaml_content = YamlLoader.load_pipeline_yaml(pipeline_yaml_file)

        # Apply the pipeline YAML via CLI
        success = await openshift_cli.apply_yaml(yaml_content)
        assert success, f"Failed to create pipeline from YAML file '{pipeline_yaml_file}' via CLI"

        # Extract pipeline name from YAML for logging
        metadata = YamlLoader.get_pipeline_metadata(yaml_content)
        pipeline_name = metadata.get("name", "unknown")

        # Log successful creation
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Successfully created pipeline '{pipeline_name}' via CLI")

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user creates a pipelinerun from YAML file "{yaml_file}"'))
def create_pipelinerun_from_yaml(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop, config: object
) -> None:
    """
    Create a PipelineRun by loading YAML from test data and submitting via UI.

    Always navigates to PipelineRuns page first to ensure consistent starting state
    (browser session is shared between scenarios, so we don't know which page we're on).

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/pipelineruns/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if creation fails
    """

    async def _step() -> None:
        # Load YAML content using helper
        yaml_content = YamlLoader.load_pipelinerun_yaml(yaml_file)

        # Wait for PipelineRuns tab data to load
        data_loaded = await page["pipelines"].runs.verify_pipeline_runs_tab_data_load()
        assert data_loaded, "PipelineRuns tab failed to load before creating PipelineRun"

        # Click Create button and select PipelineRun from dropdown (combo method)
        create_clicked = await page["pipelines"].list.click_create_pipeline_run()
        assert create_clicked, "Failed to open Create dropdown and click PipelineRun option"

        # Wait for Create PipelineRun page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Verify we're on the Create PipelineRun page
        on_create_page = await page["pipelines"].create_run.verify_on_page()
        assert on_create_page, "Failed to navigate to Create PipelineRun page"

        # Fill YAML editor using MonacoEditor component directly
        yaml_filled = await page["pipelines"].create_run.monaco_editor.set_content(yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{yaml_file}'"

        # Wait a moment for YAML validation
        await page["raw_page"].wait_for_timeout(1000)

        # Click Create button to submit
        create_submitted = await page["pipelines"].create_run.click_create()
        assert create_submitted, "Failed to click Create button to submit PipelineRun YAML"

        # Wait for redirect to PipelineRun details page
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

        # Debug: Log current URL after submission
        import logging

        logger = logging.getLogger(__name__)
        current_url = page["raw_page"].url
        logger.info(f"[DEBUG] Current URL after Create click: {current_url}")

    run_async(playwright_event_loop, _step())


@then(parsers.parse('validate user is redirected to pipelinerun details page for pipelinerun "{pipelinerun_name}"'))
def validate_pipelinerun_details(
    page: Dict[str, Any], pipelinerun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Validate user is redirected to the PipelineRun details page after creating PipelineRun.

    Note: pipelinerun_name may be a partial name prefix (e.g., "simple-pipelinerun-") when using generateName.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipelinerun_name: Name prefix of the PipelineRun to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if navigation fails
    """

    async def _step() -> None:
        # Wait for PipelineRun details page to load
        await page["raw_page"].wait_for_load_state("networkidle")

        # Verify we're on the PipelineRun details page
        on_page = await page["pipelines"].pipelinerun.details.verify_on_page()
        assert on_page, f"Failed to navigate to PipelineRun details page for '{pipelinerun_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the pipelinerun details page should display the pipelinerun name as "{expected_name}"'))
@then(parsers.parse('the pipelinerun details page should display the pipelinerun name as "{expected_name}"'))
def verify_pipelinerun_details_name(
    page: Dict[str, Any], expected_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the PipelineRun details page displays the correct PipelineRun name.

    Supports partial name matching for generateName resources (e.g., "simple-pipelinerun-" prefix).

    :param Dict[str, Any] page: Page object dictionary
    :param str expected_name: Expected PipelineRun name or name prefix to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if name does not match
    """

    async def _step() -> None:
        # Get displayed PipelineRun name
        displayed_name = await page["pipelines"].pipelinerun.details.get_pipelinerun_name()

        # For generateName resources, check if displayed name starts with expected prefix
        if expected_name.endswith("-"):
            assert displayed_name.startswith(expected_name), (
                f"PipelineRun details page displays name '{displayed_name}' but expected prefix '{expected_name}'"
            )
        else:
            # Exact match for regular names
            assert displayed_name == expected_name, (
                f"PipelineRun details page displays name '{displayed_name}' but expected '{expected_name}'"
            )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the pipelinerun "{pipelinerun_name}" should appear in the pipelineruns list'))
@then(parsers.parse('the pipelinerun "{pipelinerun_name}" should appear in the pipelineruns list'))
def verify_pipelinerun_in_list(
    page: Dict[str, Any], pipelinerun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a PipelineRun with the given name appears in the PipelineRuns list.

    Supports partial name matching for generateName resources.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipelinerun_name: Name or name prefix of the PipelineRun to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if PipelineRun is not visible in list
    """

    async def _step() -> None:
        # Verify PipelineRun appears in list
        pipelinerun_visible = await page["pipelines"].runs.verify_pipelinerun_in_list(pipelinerun_name)
        assert pipelinerun_visible, f"PipelineRun '{pipelinerun_name}' does not appear in PipelineRuns list"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the pipelinerun "{pipelinerun_name}" is executed with status "{pipelinerun_status}"'))
@then(parsers.parse('the pipelinerun "{pipelinerun_name}" is executed with status "{pipelinerun_status}"'))
def verify_pipelinerun_status_of_given_pipeline_name(
    page: Dict[str, Any],
    pipelinerun_name: str,
    pipelinerun_status: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    """
    Verify that a PipelineRun with the given name appears with given status in the PipelineRuns list.

    Polls the PipelineRun status for up to 60 seconds with 20-second intervals to handle
    asynchronous execution. Waits for status to change from "Running" to expected status.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipelinerun_name: Name or name prefix of the PipelineRun
    :param str pipelinerun_status: Expected status (e.g., "Succeeded", "Failed", "Running")
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if PipelineRun status does not match expected within timeout
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
            # Wait for PipelineRuns list data to load
            data_loaded = await page["pipelines"].runs.verify_pipeline_runs_tab_data_load()
            assert data_loaded, "PipelineRuns list failed to load before checking status"

            # Get the status of the PipelineRun
            actual_status = await page["pipelines"].runs.get_pipelinerun_status(pipelinerun_name)

            logger.info(
                f"Attempt {attempt}/{max_attempts}: PipelineRun '{pipelinerun_name}' status is '{actual_status}'"
            )

            # Check if status matches expected (case-insensitive)
            if actual_status.lower() == pipelinerun_status.lower():
                logger.info(f"PipelineRun '{pipelinerun_name}' reached expected status '{pipelinerun_status}'")
                return  # Success - status matches

            # If not the last attempt and status is still Running, wait and retry
            if attempt < max_attempts:
                logger.info(
                    f"Status is '{actual_status}', expected '{pipelinerun_status}'. "
                    f"Waiting {retry_interval_seconds}s before retry..."
                )
                await asyncio.sleep(retry_interval_seconds)

        # All attempts exhausted - status still doesn't match
        assert False, (
            f"PipelineRun '{pipelinerun_name}' has status '{actual_status}' after {max_wait_seconds}s, "
            f"but expected '{pipelinerun_status}'"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user deletes the pipelinerun "{pipelinerun_name}"'))
def delete_pipelinerun(
    page: Dict[str, Any], pipelinerun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Delete a PipelineRun using the kebab menu and confirmation modal.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipelinerun_name: Name or name prefix of the PipelineRun to delete
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if deletion fails
    """

    async def _step() -> None:
        # Click kebab menu for the PipelineRun
        kebab_clicked = await page["pipelines"].runs.click_pipelinerun_kebab_menu(pipelinerun_name)
        assert kebab_clicked, f"Failed to click kebab menu for PipelineRun '{pipelinerun_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Delete PipelineRun" menu item
        delete_clicked = await page["pipelines"].runs.click_delete_pipelinerun_menu_item()
        assert delete_clicked, f"Failed to click 'Delete PipelineRun' menu item for '{pipelinerun_name}'"

        # Wait for confirmation modal to appear and confirm deletion using modal component
        confirmation_success = await page["modal"].confirm_deletion(pipelinerun_name)
        assert confirmation_success, f"Failed to confirm deletion of PipelineRun '{pipelinerun_name}'"

        # Wait for deletion to complete
        await page["raw_page"].wait_for_timeout(2000)

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the pipelinerun "{pipelinerun_name}" should not appear in the pipelineruns list'))
def verify_pipelinerun_not_in_list(
    page: Dict[str, Any], pipelinerun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a PipelineRun with the given name does NOT appear in the PipelineRuns list.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipelinerun_name: Name or name prefix of the PipelineRun to verify absence
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if PipelineRun is still visible in list
    """

    async def _step() -> None:
        # Verify PipelineRun does NOT appear in list
        pipelinerun_not_visible = await page["pipelines"].runs.verify_pipelinerun_not_in_list(pipelinerun_name)
        assert pipelinerun_not_visible, (
            f"PipelineRun '{pipelinerun_name}' still appears in PipelineRuns list after deletion"
        )

    run_async(playwright_event_loop, _step())
