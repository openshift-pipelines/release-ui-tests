"""
Pipeline CRUD Operations Test Steps.

BDD step definitions for creating, viewing, editing, and deleting Tekton pipelines.
Follows SOLID principles with helper functions and reusable components.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

from pytest_bdd import parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_field_extractor import YamlFieldExtractor
from framework.helpers.yaml_loader import YamlLoader

# Register all scenarios from the pipeline_crud_operations feature file
FEATURE_FILE = Path(__file__).parent.parent / "features" / "pipeline_crud_operations.feature"
scenarios(FEATURE_FILE)


@when(parsers.parse('the user creates a pipeline from YAML file "{yaml_file}"'))
def create_pipeline_from_yaml(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop, config: object
) -> None:
    """
    Create a pipeline by loading YAML from test data and submitting via UI.

    Always navigates to Pipelines list page first to ensure consistent starting state
    (browser session is shared between scenarios, so we don't know which page we're on).

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/pipelines/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if creation fails
    """

    async def _step() -> None:
        # Load YAML content using helper
        yaml_content = YamlLoader.load_pipeline_yaml(yaml_file)

        # Click Create button
        create_clicked = await page["pipelines"].list.click_create_button()
        assert create_clicked, "Failed to click Create button on Pipelines list page"

        # Wait for dropdown menu to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Pipeline" option from dropdown
        pipeline_option_clicked = await page["pipelines"].list.click_create_pipeline_menu_item()
        assert pipeline_option_clicked, "Failed to click 'Pipeline' menu item from Create dropdown"

        # Wait for Pipeline Builder page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Verify we're on the Pipeline Builder page
        on_builder_page = await page["pipelines"].builder.verify_on_page()
        assert on_builder_page, "Failed to navigate to Pipeline Builder page"

        # Switch to YAML view
        yaml_view_switched = await page["pipelines"].builder.switch_to_yaml_view()
        assert yaml_view_switched, "Failed to switch to YAML view in Pipeline Builder"

        # Wait for YAML editor to fully load
        # MonacoEditor component will handle waiting for editor readiness
        await page["raw_page"].wait_for_timeout(1000)

        # Fill YAML editor using MonacoEditor component directly
        yaml_filled = await page["pipelines"].builder.yaml_view.monaco_editor.set_content(yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{yaml_file}'"

        # Click Create button to submit (on builder page level, not yaml_view)
        create_submitted = await page["pipelines"].builder.click_create()
        assert create_submitted, "Failed to click Create button to submit pipeline YAML"

        # Wait for redirect to pipeline details page
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

    run_async(playwright_event_loop, _step())


@then(parsers.parse('validate user is redirected to pipeline details page for pipeline "{pipeline_name}"'))
def validate_pipeline_details(
    page: Dict[str, Any], pipeline_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Validate user is redirected to the pipeline details page after creating pipeline.
    :param Dict[str, Any] page: Page object dictionary
    :param str pipeline_name: Name of the pipeline to open
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if navigation fails
    """

    async def _step() -> None:
        # Wait for pipeline details page to load
        await page["raw_page"].wait_for_load_state("networkidle")

        # Verify we're on the pipeline details page
        on_page = await page["pipelines"].pipeline.details.verify_on_page()
        assert on_page, f"Failed to navigate to pipeline details page for '{pipeline_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the pipeline details page should display the pipeline name as "{expected_name}"'))
@then(parsers.parse('the pipeline details page should display the pipeline name as "{expected_name}"'))
def verify_pipeline_details_name(
    page: Dict[str, Any], expected_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the pipeline details page displays the correct pipeline name.

    :param Dict[str, Any] page: Page object dictionary
    :param str expected_name: Expected pipeline name to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if name does not match
    """

    async def _step() -> None:
        # Get displayed pipeline name
        displayed_name = await page["pipelines"].pipeline.details.get_pipeline_name()

        # Verify it matches expected name
        assert displayed_name == expected_name, (
            f"Pipeline details page displays name '{displayed_name}' but expected '{expected_name}'"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the pipeline "{pipeline_name}" should appear in the pipelines list'))
@then(parsers.parse('the pipeline "{pipeline_name}" should appear in the pipelines list'))
def verify_pipeline_in_list(
    page: Dict[str, Any], pipeline_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a pipeline with the given name appears in the pipelines list.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipeline_name: Name of the pipeline to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if pipeline is not visible in list
    """

    async def _step() -> None:
        # Verify pipeline appears in list
        pipeline_visible = await page["pipelines"].list.verify_pipeline_in_list(pipeline_name)
        assert pipeline_visible, f"Pipeline '{pipeline_name}' does not appear in pipelines list"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user edits the pipeline "{pipeline_name}" with YAML file "{updated_yaml_file}"'))
def edit_pipeline_yaml(
    page: Dict[str, Any],
    pipeline_name: str,
    updated_yaml_file: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
    config: object,
) -> None:
    """
    Edit a pipeline's YAML definition using the kebab menu and YAML editor.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipeline_name: Name of the pipeline to edit
    :param str updated_yaml_file: Name of updated YAML file in test_data/pipelines/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if edit fails
    """

    async def _step() -> None:
        # Load updated YAML template using helper
        updated_yaml_template = YamlLoader.load_pipeline_yaml(updated_yaml_file)

        # Click kebab menu for the pipeline
        kebab_clicked = await page["pipelines"].list.click_pipeline_kebab_menu(pipeline_name)
        assert kebab_clicked, f"Failed to click kebab menu for pipeline '{pipeline_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Edit Pipeline" menu item (opens Pipeline Builder page)
        edit_clicked = await page["pipelines"].list.click_edit_pipeline_menu_item()
        assert edit_clicked, f"Failed to click 'Edit Pipeline' menu item for '{pipeline_name}'"

        # Wait for Pipeline Builder page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Switch to YAML view in Pipeline Builder (Edit Pipeline opens Builder page)
        yaml_view_switched = await page["pipelines"].builder.switch_to_yaml_view()
        assert yaml_view_switched, f"Failed to switch to YAML view for pipeline '{pipeline_name}'"

        # Wait for YAML editor to load
        await page["raw_page"].wait_for_timeout(1000)

        # Verify we're on the Pipeline Builder page (in YAML view)
        on_builder_page = await page["pipelines"].builder.verify_on_page()
        assert on_builder_page, f"Failed to stay on Pipeline Builder page for '{pipeline_name}'"

        # Wait for YAML editor to be ready (confirms YAML view loaded)
        yaml_editor_ready = await page["pipelines"].builder.yaml_view.monaco_editor.wait_for_editor_ready()
        assert yaml_editor_ready, f"YAML editor not ready for pipeline '{pipeline_name}'"

        # Wait for YAML editor to fully load and populate with existing content
        await page["raw_page"].wait_for_timeout(5000)

        # Extract existing YAML content from editor (BEFORE clearing it)
        # This contains Kubernetes-generated fields like resourceVersion, uid, etc.
        import logging

        logger = logging.getLogger(__name__)

        existing_yaml = await page["pipelines"].builder.yaml_view.monaco_editor.get_content()

        # Log extracted content for debugging
        logger.info(f"Extracted YAML content length: {len(existing_yaml)} characters")
        if existing_yaml:
            # Log first 200 chars to verify it's the right content
            logger.debug(f"YAML preview: {existing_yaml[:200]}...")

        assert existing_yaml, f"Failed to extract existing YAML for pipeline '{pipeline_name}'"

        # Define fields to preserve from existing YAML
        # These are Kubernetes-managed fields that must match the existing resource
        fields_to_preserve = [
            "metadata.resourceVersion",
            "metadata.uid",
        ]

        # Extract field values from existing YAML
        extracted_values = YamlFieldExtractor.get_multiple_fields(existing_yaml, fields_to_preserve)

        # Log extracted values for debugging
        logger.info(f"Extracted values from existing pipeline YAML: {extracted_values}")

        # Verify extraction succeeded
        assert extracted_values, (
            f"Failed to extract required fields {fields_to_preserve} from existing YAML. "
            "Ensure the pipeline exists and has been persisted by Kubernetes."
        )

        # Replace placeholders in new YAML with extracted values
        updated_yaml_content = YamlFieldExtractor.replace_placeholders(updated_yaml_template, extracted_values)

        # Verify placeholders were replaced
        for field_path in fields_to_preserve:
            placeholder = f"{{{{{field_path}}}}}"
            assert placeholder not in updated_yaml_content, (
                f"Placeholder '{placeholder}' was not replaced in updated YAML. "
                f"Ensure template has correct placeholder format and extraction succeeded."
            )

        logger.info(f"Successfully replaced {len(extracted_values)} placeholders in updated YAML")

        # Fill YAML editor with updated content (with preserved fields)
        yaml_filled = await page["pipelines"].builder.yaml_view.monaco_editor.set_content(updated_yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{updated_yaml_file}'"

        # Click Save button to save changes (edit workflow uses "Save", create workflow uses "Create")
        save_clicked = await page["pipelines"].builder.click_save()
        assert save_clicked, f"Failed to click Save button for pipeline '{pipeline_name}'"

        # Wait for save to complete
        await page["raw_page"].wait_for_timeout(2000)

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user deletes the pipeline "{pipeline_name}"'))
def delete_pipeline(page: Dict[str, Any], pipeline_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Delete a pipeline using the kebab menu and confirmation modal.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipeline_name: Name of the pipeline to delete
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if deletion fails
    """

    async def _step() -> None:
        # Navigate to pipelines list
        # Check if Pipelines link is visible; if not, click Pipelines button to expand menu
        pipelines_link_visible = await page["nav"].verify_link_available_under_pipelines_button("Pipelines")
        if not pipelines_link_visible:
            await page["nav"].click_pipelines_button()
            await page["raw_page"].wait_for_timeout(500)  # Wait for menu to expand

        await page["nav"].navigate_to_pipelines()

        # Wait for pipelines list to load
        data_loaded = await page["pipelines"].list.verify_data_load()
        assert data_loaded, "Pipelines list failed to load data before deletion"

        # Click kebab menu for the pipeline
        kebab_clicked = await page["pipelines"].list.click_pipeline_kebab_menu(pipeline_name)
        assert kebab_clicked, f"Failed to click kebab menu for pipeline '{pipeline_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Delete Pipeline" menu item
        delete_clicked = await page["pipelines"].list.click_delete_pipeline_menu_item()
        assert delete_clicked, f"Failed to click 'Delete Pipeline' menu item for '{pipeline_name}'"

        # Wait for confirmation modal to appear and confirm deletion using modal component
        confirmation_success = await page["modal"].confirm_deletion(pipeline_name)
        assert confirmation_success, f"Failed to confirm deletion of pipeline '{pipeline_name}'"

        # Wait for deletion to complete
        await page["raw_page"].wait_for_timeout(2000)

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the pipeline "{pipeline_name}" should not appear in the pipelines list'))
def verify_pipeline_not_in_list(
    page: Dict[str, Any], pipeline_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a pipeline with the given name does NOT appear in the pipelines list.

    :param Dict[str, Any] page: Page object dictionary
    :param str pipeline_name: Name of the pipeline to verify absence
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if pipeline is still visible in list
    """

    async def _step() -> None:
        # Wait for pipelines list to reload after deletion
        data_loaded = await page["pipelines"].list.verify_data_load()
        assert data_loaded, "Pipelines list failed to reload after deletion"

        # Verify pipeline does NOT appear in list
        pipeline_not_visible = await page["pipelines"].list.verify_pipeline_not_in_list(pipeline_name)
        assert pipeline_not_visible, f"Pipeline '{pipeline_name}' still appears in pipelines list after deletion"

    run_async(playwright_event_loop, _step())
