"""
Task CRUD Operations Test Steps.

BDD step definitions for creating, viewing, editing, and deleting Tekton tasks.
Follows SOLID principles with helper functions and reusable components.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict

from pytest_bdd import parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_field_extractor import YamlFieldExtractor
from framework.helpers.yaml_loader import YamlLoader

# Register all scenarios from the task_crud_operations feature file
FEATURE_FILE = Path(__file__).parent.parent / "features" / "task_crud_operations.feature"
scenarios(FEATURE_FILE)


@when(parsers.parse('the user creates a task from YAML file "{yaml_file}"'))
def create_task_from_yaml(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop, config: object
) -> None:
    """
    Create a task by loading YAML from test data and submitting via UI.

    Always navigates to Tasks list page first to ensure consistent starting state
    (browser session is shared between scenarios, so we don't know which page we're on).

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/tasks/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if creation fails
    """

    async def _step() -> None:
        # Load YAML content using helper
        yaml_content = YamlLoader.load_task_yaml(yaml_file)

        # Click Create button
        create_clicked = await page["tasks"].list.click_create_button()
        assert create_clicked, "Failed to click Create button on Tasks list page"

        # Wait for dropdown menu to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Task" option from dropdown
        task_option_clicked = await page["tasks"].list.click_create_task_menu_item()
        assert task_option_clicked, "Failed to click 'Task' menu item from Create dropdown"

        # Wait for Create Task page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Fill YAML editor using MonacoEditor component directly
        yaml_filled = await page["tasks"].create.monaco_editor.set_content(yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{yaml_file}'"

        # Click Create button to submit
        create_submitted = await page["tasks"].create.click_create()
        assert create_submitted, "Failed to click Create button to submit task YAML"

        # Wait for redirect to task details page
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user navigates to task details page for task "{task_name}"'))
def navigate_to_task_details_page_for_given_task(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a task with the given name appears in the tasks list.

    :param Dict[str, Any] page: Page object dictionary
    :param str task_name: Name of the task to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task is not visible in list
    """

    async def _step() -> None:
        await page["tasks"].list.click_on_given_task_in_list(task_name)

        # Wait for task details page to load
        await page["raw_page"].wait_for_load_state("networkidle")

        # Verify we're on the task details page
        on_page = await page["tasks"].task.details.verify_on_page()
        assert on_page, f"Failed to navigate to task details page for '{task_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the task "{task_name}" should appear in the tasks list'))
@then(parsers.parse('the task "{task_name}" should appear in the tasks list'))
def verify_task_in_list(page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that a task with the given name appears in the tasks list.

    :param Dict[str, Any] page: Page object dictionary
    :param str task_name: Name of the task to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task is not visible in list
    """

    async def _step() -> None:
        # Verify task appears in list
        task_visible = await page["tasks"].list.verify_task_in_list(task_name)
        assert task_visible, f"Task '{task_name}' does not appear in tasks list"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('validate user is redirected to task details page for task "{task_name}"'))
@then(parsers.parse('validate user is redirected to task details page for task "{task_name}"'))
def validate_task_details(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Validate user is redirected to the task details page after creating task.
    :param Dict[str, Any] page: Page object dictionary
    :param str task_name: Name of the task to open
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if navigation fails
    """

    async def _step() -> None:
        # Wait for task details page to load
        await page["raw_page"].wait_for_load_state("networkidle")

        # Verify we're on the task details page
        on_page = await page["tasks"].task.details.verify_on_page()
        assert on_page, f"Failed to navigate to task details page for '{task_name}'"

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task details page should display heading with task name as "{expected_name}"'))
def verify_task_details_heading_name(
    page: Dict[str, Any], expected_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task details page displays the correct task name.

    :param Dict[str, Any] page: Page object dictionary
    :param str expected_name: Expected task name to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if name does not match
    """

    async def _step() -> None:
        # Get displayed task name
        displayed_name = await page["tasks"].task.details.get_task_heading_name()

        # Verify it matches expected name
        assert displayed_name == expected_name, (
            f"Task details page displays name '{displayed_name}' but expected '{expected_name}'"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the task details page should display the task name as "{expected_name}"'))
@then(parsers.parse('the task details page should display the task name as "{expected_name}"'))
def verify_task_details_name(
    page: Dict[str, Any], expected_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task details page displays the correct task name.

    :param Dict[str, Any] page: Page object dictionary
    :param str expected_name: Expected task name to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if name does not match
    """

    async def _step() -> None:
        # Get displayed task name
        displayed_name = await page["tasks"].task.details.get_task_name()

        # Verify it matches expected name
        assert displayed_name == expected_name, (
            f"Task details page displays name '{displayed_name}' but expected '{expected_name}'"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user edits the task "{task_name}" with YAML file "{updated_yaml_file}"'))
def edit_task_yaml(
    page: Dict[str, Any],
    task_name: str,
    updated_yaml_file: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
    config: object,
) -> None:
    """
    Edit a task's YAML definition using the kebab menu and YAML editor.

    :param Dict[str, Any] page: Page object dictionary
    :param str task_name: Name of the task to edit
    :param str updated_yaml_file: Name of updated YAML file in test_data/tasks/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if edit fails
    """

    async def _step() -> None:
        # Load updated YAML template using helper
        updated_yaml_template = YamlLoader.load_task_yaml(updated_yaml_file)

        # Click kebab menu for the task
        kebab_clicked = await page["tasks"].list.click_task_kebab_menu(task_name)
        assert kebab_clicked, f"Failed to click kebab menu for task '{task_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Edit Task" menu item
        edit_clicked = await page["tasks"].list.click_edit_task_menu_item()
        assert edit_clicked, f"Failed to click 'Edit Task' menu item for '{task_name}'"

        # Wait for YAML editor page to load
        await page["raw_page"].wait_for_timeout(1000)

        # Verify we're on the task YAML page
        on_yaml_page = await page["tasks"].task.yaml.verify_on_page()
        assert on_yaml_page, f"Failed to navigate to YAML editor for task '{task_name}'"

        # Wait for YAML editor to fully load and populate with existing content
        await page["raw_page"].wait_for_timeout(5000)

        # Extract existing YAML content from editor (BEFORE clearing it)
        # This contains Kubernetes-generated fields like resourceVersion, uid, etc.
        import logging

        logger = logging.getLogger(__name__)

        existing_yaml = await page["tasks"].task.yaml.monaco_editor.get_content()

        # Log extracted content for debugging
        logger.info(f"Extracted YAML content length: {len(existing_yaml)} characters")
        if existing_yaml:
            # Log first 200 chars to verify it's the right content
            logger.debug(f"YAML preview: {existing_yaml[:200]}...")

        assert existing_yaml, f"Failed to extract existing YAML for task '{task_name}'"

        # Define fields to preserve from existing YAML
        # These are Kubernetes-managed fields that must match the existing resource
        fields_to_preserve = [
            "metadata.resourceVersion",
            "metadata.uid",
        ]

        # Extract field values from existing YAML
        extracted_values = YamlFieldExtractor.get_multiple_fields(existing_yaml, fields_to_preserve)

        # Log extracted values for debugging
        logger.info(f"Extracted values from existing task YAML: {extracted_values}")

        # Verify extraction succeeded
        assert extracted_values, (
            f"Failed to extract required fields {fields_to_preserve} from existing YAML. "
            "Ensure the task exists and has been persisted by Kubernetes."
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
        yaml_filled = await page["tasks"].task.yaml.monaco_editor.set_content(updated_yaml_content)
        assert yaml_filled, f"Failed to fill YAML editor with content from '{updated_yaml_file}'"

        # Click Save button
        save_clicked = await page["tasks"].task.yaml.click_save()
        assert save_clicked, f"Failed to click Save button for task '{task_name}'"

        # Wait for save to complete
        await page["raw_page"].wait_for_timeout(2000)

    run_async(playwright_event_loop, _step())


@then(parsers.parse("the user navigates to task details tab"))
def navigate_to_task_details_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Navigate to the Details tab of the current task."""

    async def _step() -> None:
        await page["tasks"].task.details.navigate_to_details_tab()
        # Wait for task details page to load
        await page["raw_page"].wait_for_load_state("networkidle")

        # Verify we're on the task details page
        on_page = await page["tasks"].task.details.verify_on_page()
        assert on_page, "Failed to navigate to task details tab for"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user deletes the task "{task_name}"'))
def delete_task(page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Delete a task using the kebab menu and confirmation modal.

    :param Dict[str, Any] page: Page object dictionary
    :param str task_name: Name of the task to delete
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if deletion fails
    """

    async def _step() -> None:
        # Navigate to tasks list
        # Check if Tasks link is visible; if not, click Pipelines button to expand menu
        tasks_link_visible = await page["nav"].verify_link_available_under_pipelines_button("Tasks")
        if not tasks_link_visible:
            await page["nav"].click_pipelines_button()
            await page["raw_page"].wait_for_timeout(500)  # Wait for menu to expand

        await page["nav"].navigate_to_tasks()

        # Wait for tasks list to load
        data_loaded = await page["tasks"].list.verify_data_load()
        assert data_loaded, "Tasks list failed to load data before deletion"

        # Click kebab menu for the task
        kebab_clicked = await page["tasks"].list.click_task_kebab_menu(task_name)
        assert kebab_clicked, f"Failed to click kebab menu for task '{task_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        # Click "Delete Task" menu item
        delete_clicked = await page["tasks"].list.click_delete_task_menu_item()
        assert delete_clicked, f"Failed to click 'Delete Task' menu item for '{task_name}'"

        # Wait for confirmation modal to appear and confirm deletion using modal component
        confirmation_success = await page["modal"].confirm_deletion(task_name)
        assert confirmation_success, f"Failed to confirm deletion of task '{task_name}'"

        # Wait for deletion to complete
        await page["raw_page"].wait_for_timeout(2000)

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task "{task_name}" should not appear in the tasks list'))
def verify_task_not_in_list(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that a task with the given name does NOT appear in the tasks list.

    :param Dict[str, Any] page: Page object dictionary
    :param str task_name: Name of the task to verify absence
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task is still visible in list
    """

    async def _step() -> None:
        # Wait for tasks list to reload after deletion
        data_loaded = await page["tasks"].list.verify_data_load()
        assert data_loaded, "Tasks list failed to reload after deletion"

        # Verify task does NOT appear in list
        task_not_visible = await page["tasks"].list.verify_task_not_in_list(task_name)
        assert task_not_visible, f"Task '{task_name}' still appears in tasks list after deletion"

    run_async(playwright_event_loop, _step())


@then(parsers.parse("the task details page should display namespace"))
def verify_task_namespace(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the task details page displays the correct namespace.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if namespace does not match
    """

    async def _step() -> None:
        # Get displayed task name
        displayed_name = await page["tasks"].task.details.get_namespace_value()

        # Verify it matches expected name
        assert "release-ui-test" in displayed_name, (
            f"Task details page namespace value should contain release-ui-test but found '{displayed_name}'"
        )

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task details page should contain labels with value "{labels}"'))
def verify_task_labels(page: Dict[str, Any], labels: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the task details page displays the specified label.

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
        displayed_labels_value = await page["tasks"].task.details.get_labels_value()
        normalized_labels_value = re.sub(r"\s*=\s*", "=", displayed_labels_value)
        missing_labels = [
            f"{key}={value}"
            for key, value in expected_labels.items()
            if f"{key}={value}" not in normalized_labels_value
        ]
        assert not missing_labels, (
            f"Task details page labels missing {missing_labels}; displayed labels were '{displayed_labels_value}'"
        )

    run_async(playwright_event_loop, _step())


@then(
    parsers.parse(
        'the task details page should contain appropriate count of annotations value with "{annotations_value}"'
    )
)
def verify_annotations_count(
    page: Dict[str, Any], annotations_value: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task details page displays the expected annotation count.

    :param Dict[str, Any] page: Page object dictionary
    :param str annotations_value: JSON object containing the expected annotations
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if the annotation count does not match
    """

    async def _step() -> None:
        try:
            expected_annotations = json.loads(annotations_value)
        except json.JSONDecodeError as error:
            raise AssertionError(f"Invalid expected annotations JSON '{annotations_value}': {error.msg}") from error

        assert isinstance(expected_annotations, dict), (
            f"Expected annotations must be a JSON object, but received '{annotations_value}'"
        )

        annotations_count_value = await page["tasks"].task.details.get_annotations_count_value()
        count_match = re.search(r"\d+", annotations_count_value)
        assert count_match, f"Could not extract an annotation count from '{annotations_count_value}'"

        displayed_count = int(count_match.group())
        expected_count = len(expected_annotations)
        assert displayed_count == expected_count, (
            f"Task details page displays {displayed_count} annotations, "
            f"but expected {expected_count}: {list(expected_annotations)}"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse("the user navigates to edit annotations dialog from task details page"))
def navigate_to_edit_annotations_dialog(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Open the Edit annotations dialog from the task details page.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if the dialog does not open
    """

    async def _step() -> None:
        annotations_dialog_open = await page["tasks"].task.details.open_annotations_dialog()
        assert annotations_dialog_open, "Edit annotations dialog did not appear on the task details page"

    run_async(playwright_event_loop, _step())


@then(parsers.parse("the user closes the edit annotations dialog"))
def close_edit_annotations_dialog(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Close the Edit annotations dialog without saving changes."""

    async def _step() -> None:
        dialog_closed = await page["tasks"].task.details.annotations_modal.close_annotations_dialog()
        assert dialog_closed, "Failed to close the Edit annotations dialog"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user opens Edit labels dialog using Edit task option for task "{task_name}"'))
def open_edit_labels_dialog(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open the Edit labels dialog for the specified task."""

    async def _step() -> None:
        # Click kebab menu for the task
        kebab_clicked = await page["tasks"].list.click_task_kebab_menu(task_name)
        assert kebab_clicked, f"Failed to click kebab menu for task '{task_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        await page["tasks"].list.open_edit_labels_dialog()

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user adds labels to task "{task_name}" with labels "{labels}"'))
def add_task_labels(
    page: Dict[str, Any], task_name: str, labels: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Append JSON label pairs to the open Edit labels dialog."""

    async def _step() -> None:
        try:
            new_labels = json.loads(labels)
        except json.JSONDecodeError as error:
            raise AssertionError(f"Invalid labels JSON '{labels}': {error.msg}") from error

        assert isinstance(new_labels, dict), f"Expected labels must be a JSON object, but received '{labels}'"
        labels_saved = await page["tasks"].list.labels_modal.add_labels(new_labels)
        assert labels_saved, f"Failed to add labels to task '{task_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user opens Edit annotations dialog using Edit annotations option for task "{task_name}"'))
def open_edit_annotations_dialog(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open the Edit annotations dialog for the specified task."""

    async def _step() -> None:
        # Click kebab menu for the task
        kebab_clicked = await page["tasks"].list.click_task_kebab_menu(task_name)
        assert kebab_clicked, f"Failed to click kebab menu for task '{task_name}'"

        # Wait for kebab menu dropdown to appear
        await page["raw_page"].wait_for_timeout(500)

        await page["tasks"].list.open_edit_annotations_dialog()

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user adds new annotations to task "{task_name}" with annotations "{annotations}"'))
def add_task_annotations(
    page: Dict[str, Any], task_name: str, annotations: str, playwright_event_loop: asyncio.AbstractEventLoop
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
        annotations_saved = await page["tasks"].list.annotations_modal.add_annotations(new_annotations)
        assert annotations_saved, f"Failed to add annotations to task '{task_name}'"

    run_async(playwright_event_loop, _step())


@then(
    parsers.parse(
        'the annotations dialog of task details page should contain annotations with value "{annotation_value}"'
    )
)
def verify_task_annotations(
    page: Dict[str, Any], annotation_value: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the Edit annotations dialog contains the expected annotations.

    :param Dict[str, Any] page: Page object dictionary
    :param str annotation_value: JSON object containing the annotations to verify
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if an annotation is not present
    """

    async def _step() -> None:
        try:
            expected_annotations = json.loads(annotation_value)
        except json.JSONDecodeError as error:
            raise AssertionError(f"Invalid expected annotations JSON '{annotation_value}': {error.msg}") from error

        assert isinstance(expected_annotations, dict), (
            f"Expected annotations must be a JSON object, but received '{annotation_value}'"
        )

        displayed_annotations = await page["tasks"].task.details.get_annotations_dialog_field_values()

        missing_annotations = [
            f"{key}={value}"
            for key, value in expected_annotations.items()
            if displayed_annotations.get(str(key)) != str(value)
        ]
        assert not missing_annotations, (
            f"Edit annotations dialog is missing {missing_annotations}; dialog annotations were {displayed_annotations}"
        )

    run_async(playwright_event_loop, _step())
