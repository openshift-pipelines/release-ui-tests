"""
Shared Test Steps.

Contains BDD step definitions that are reused across multiple feature files.
These steps provide common operations (e.g., creating resources via CLI/UI)
to avoid duplication and maintain a single source of truth.

This file follows the separation of concerns principle:
- Feature-specific steps belong in their respective test_*_steps.py files
- Shared/reusable steps across features belong here

Following DRY (Don't Repeat Yourself) principle for better maintainability.
"""

import asyncio
import logging
from typing import Any, Dict

from pytest_bdd import given, parsers, then, when

from framework.cli.openshift_cli import OpenShiftCLI
from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_loader import YamlLoader

logger = logging.getLogger(__name__)


@when(parsers.parse('the user creates a task via cli from YAML file "{task_yaml_file}"'))
def create_task_via_cli(
    task_yaml_file: str, openshift_cli: OpenShiftCLI, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Create a Tekton Task via OpenShift CLI by loading YAML from test data.

    Shared by TaskRun CRUD and TaskRun negative features so the step is always
    available via pytest_plugins, even when CRUD scenarios are deselected.
    """

    async def _step() -> None:
        yaml_content = YamlLoader.load_task_yaml(task_yaml_file)
        success = await openshift_cli.apply_yaml(yaml_content)
        assert success, f"Failed to create task from YAML file '{task_yaml_file}' via CLI"
        metadata = YamlLoader.get_task_metadata(yaml_content)
        task_name = metadata.get("name", "unknown")
        logger.info(f"Successfully created task '{task_name}' via CLI")

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the taskrun "{taskrun_name}" should appear in the taskruns list'))
@then(parsers.parse('the taskrun "{taskrun_name}" should appear in the taskruns list'))
def verify_taskrun_in_list(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Verify that a TaskRun with the given name appears in the TaskRuns list."""

    async def _step() -> None:
        taskrun_visible = await page["tasks"].runs.verify_taskrun_in_list(taskrun_name)
        assert taskrun_visible, f"TaskRun '{taskrun_name}' does not appear in TaskRuns list"

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the taskrun "{taskrun_name}" should not appear in the taskruns list'))
def verify_taskrun_not_in_list(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Verify that a TaskRun with the given name does NOT appear in the TaskRuns list."""

    async def _step() -> None:
        data_loaded = await page["tasks"].runs.verify_task_runs_tab_data_load()
        assert data_loaded, "TaskRuns list failed to reload after deletion"
        taskrun_not_visible = await page["tasks"].runs.verify_taskrun_not_in_list(taskrun_name)
        assert taskrun_not_visible, f"TaskRun '{taskrun_name}' still appears in TaskRuns list after deletion"

    run_async(playwright_event_loop, _step())


@given(parsers.parse('the user creates a pipeline via cli from YAML file "{pipeline_yaml_file}"'))
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
        logger.info(f"Loaded Pipeline YAML from '{pipeline_yaml_file}'")

        # Apply the pipeline YAML via CLI
        success = await openshift_cli.apply_yaml(yaml_content)
        assert success, f"Failed to create pipeline from YAML file '{pipeline_yaml_file}' via CLI"

        # Extract pipeline name from YAML for logging
        metadata = YamlLoader.get_pipeline_metadata(yaml_content)
        pipeline_name = metadata.get("name", "unknown")

        # Log successful creation
        logger.info(f"Successfully created pipeline '{pipeline_name}' via CLI")

    run_async(playwright_event_loop, _step())


@given(parsers.parse('the user creates a pipelinerun from YAML file "{yaml_file}"'))
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
        logger.info(f"Loaded YAML content from '{yaml_file}'")

        # Wait for PipelineRuns tab data to load
        data_loaded = await page["pipelines"].runs.verify_pipeline_runs_tab_data_load()
        assert data_loaded, "PipelineRuns tab failed to load before creating PipelineRun"

        # Click Create button and select PipelineRun from dropdown (combo method)
        create_clicked = await page["pipelines"].list.click_create_pipeline_run()
        assert create_clicked, "Failed to open Create dropdown and click PipelineRun option"

        # Wait for Create PipelineRun page to load - Monaco editor should be visible
        await page["raw_page"].wait_for_selector(".monaco-editor", state="visible", timeout=15000)

        # Verify we're on the Create PipelineRun page
        on_create_page = await page["pipelines"].create_run.verify_on_page()
        assert on_create_page, "Failed to navigate to Create PipelineRun page"

        # Fill YAML editor using MonacoEditor component directly
        yaml_filled = await page["pipelines"].create_run.monaco_editor.set_content(yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{yaml_file}'"

        # Wait for Create button to become enabled (YAML validation completes)
        await page["raw_page"].wait_for_selector('button:has-text("Create"):not([disabled])', timeout=15000)

        # Click Create button to submit
        create_submitted = await page["pipelines"].create_run.click_create()
        assert create_submitted, "Failed to click Create button to submit PipelineRun YAML"

        # Wait for redirect to PipelineRun details page
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

        # Log current URL after submission for debugging
        current_url = page["raw_page"].url
        logger.info(f"PipelineRun created successfully. Current URL: {current_url}")

    run_async(playwright_event_loop, _step())
