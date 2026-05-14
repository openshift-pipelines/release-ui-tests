"""
Task CRUD Operations Test Steps.

BDD step definitions for creating, viewing, editing, and deleting Tekton tasks.
Follows SOLID principles with helper functions and reusable components.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict

import yaml
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


@when(parsers.parse('the user navigates to task details page for task "{task_name}"'))
def navigate_to_task_details(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop, config: object
) -> None:
    """
    Navigate to the task details page by clicking on the task name in the tasks list.

    :param Dict[str, Any] page: Page object dictionary
    :param str task_name: Name of the task to navigate to
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if navigation fails
    """

    async def _step() -> None:
        # Click on the task name link
        click_success = await page["tasks"].list.click_task_name(task_name)
        assert click_success, f"Failed to click on task name '{task_name}'"

        # Wait for task details page to load
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

        # Verify we're on the task details page
        on_page = await page["tasks"].task.details.verify_on_page()
        assert on_page, f"Failed to navigate to task details page for '{task_name}'"

    run_async(playwright_event_loop, _step())


@then("the task details page should display namespace as current project")
def verify_task_namespace_is_current_project(
    page: Dict[str, Any], test_project: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task details page displays the current test project as the namespace.

    :param Dict[str, Any] page: Page object dictionary
    :param str test_project: Current test project name from fixture
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if namespace does not match current project
    """

    async def _step() -> None:
        displayed_namespace = await page["tasks"].task.details.get_namespace()
        assert displayed_namespace == test_project, (
            f"Task details page displays namespace '{displayed_namespace}' but expected '{test_project}'"
        )

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task details page should display labels from YAML file "{yaml_file}"'))
def verify_task_labels_from_yaml(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task details page displays labels matching the YAML file.

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/tasks/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if labels do not match
    """

    async def _step() -> None:
        # Load YAML content
        yaml_content = YamlLoader.load_task_yaml(yaml_file)

        # Extract expected labels from YAML
        metadata = YamlLoader.get_labels_and_annotations(yaml_content)
        expected_labels = metadata["labels"]

        # Get actual labels from page
        actual_labels = await page["tasks"].task.details.get_labels()

        # Verify all expected labels are present
        for key, value in expected_labels.items():
            assert key in actual_labels, f"Expected label '{key}' not found in task details"
            assert actual_labels[key] == value, f"Label '{key}' has value '{actual_labels[key]}' but expected '{value}'"

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task details page should display annotations from YAML file "{yaml_file}"'))
def verify_task_annotations_from_yaml(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task details page displays annotations count matching the YAML file.

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/tasks/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if annotation count does not match
    """

    async def _step() -> None:
        # Load YAML content
        yaml_content = YamlLoader.load_task_yaml(yaml_file)

        # Extract expected annotations from YAML
        metadata = YamlLoader.get_labels_and_annotations(yaml_content)
        expected_annotations = metadata["annotations"]
        expected_count = len(expected_annotations)

        # Get actual annotation count from page
        actual_count = await page["tasks"].task.details.get_annotations_count()

        assert actual_count == expected_count, (
            f"Task details page displays {actual_count} annotations but expected {expected_count} (from {yaml_file})"
        )

    run_async(playwright_event_loop, _step())


@when("the user navigates to YAML tab")
def navigate_to_yaml_tab(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop, config: object
) -> None:
    """
    Navigate from task details page to YAML tab.

    :param Dict[str, Any] page: Page object dictionary
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :param object config: Config object for timeout values
    :return: None: Raises AssertionError if navigation fails
    """

    async def _step() -> None:
        # Click YAML tab
        tab_clicked = await page["tasks"].task.details.navigate_to_yaml_tab()
        assert tab_clicked, "Failed to click YAML tab"

        # Wait for YAML editor to load
        await page["raw_page"].wait_for_timeout(2000)

        # Verify we're on the YAML page
        on_yaml_page = await page["tasks"].task.yaml.verify_on_page()
        assert on_yaml_page, "Failed to navigate to task YAML page"

        # Wait for Monaco editor to fully load content
        await page["raw_page"].wait_for_timeout(1000)

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task YAML page should display the task name as "{expected_name}"'))
def verify_yaml_page_task_name(
    page: Dict[str, Any], expected_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that the task YAML page displays the correct task name.

    :param Dict[str, Any] page: Page object dictionary
    :param str expected_name: Expected task name
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if name does not match
    """

    async def _step() -> None:
        displayed_name = await page["tasks"].task.yaml.get_task_name()
        assert displayed_name == expected_name, (
            f"Task YAML page displays name '{displayed_name}' but expected '{expected_name}'"
        )

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task YAML page should display content from YAML file "{yaml_file}"'))
def verify_yaml_content_from_file(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify that YAML editor content matches expected file structure.

    Compares key fields (name, labels, annotations) between the YAML editor
    and the expected YAML file. Ignores Kubernetes-generated fields like
    resourceVersion, uid, creationTimestamp.

    :param Dict[str, Any] page: Page object dictionary
    :param str yaml_file: Name of YAML file in test_data/tasks/
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if YAML content does not match
    """

    async def _step() -> None:
        # Get YAML content from Monaco editor
        yaml_from_editor = await page["tasks"].task.yaml.monaco_editor.get_content()
        assert yaml_from_editor, "YAML editor content is empty"

        # Load expected YAML from file
        expected_yaml_content = YamlLoader.load_task_yaml(yaml_file)

        # Parse both YAMLs
        editor_data = yaml.safe_load(yaml_from_editor)
        expected_data = yaml.safe_load(expected_yaml_content)

        # Validate metadata.name
        assert editor_data.get("metadata", {}).get("name") == expected_data.get("metadata", {}).get("name"), (
            f"YAML editor shows name '{editor_data.get('metadata', {}).get('name')}' "
            f"but expected '{expected_data.get('metadata', {}).get('name')}'"
        )

        # Validate labels (all expected labels must be present with correct values)
        expected_labels = expected_data.get("metadata", {}).get("labels", {})
        actual_labels = editor_data.get("metadata", {}).get("labels", {})

        for key, value in expected_labels.items():
            assert key in actual_labels, f"Expected label '{key}' not found in YAML editor"
            assert actual_labels[key] == value, f"Label '{key}' has value '{actual_labels[key]}' but expected '{value}'"

        # Validate annotations (all expected annotations must be present with correct values)
        expected_annotations = expected_data.get("metadata", {}).get("annotations", {})
        actual_annotations = editor_data.get("metadata", {}).get("annotations", {})

        for key, value in expected_annotations.items():
            assert key in actual_annotations, f"Expected annotation '{key}' not found in YAML editor"
            assert actual_annotations[key] == value, (
                f"Annotation '{key}' has value '{actual_annotations[key]}' but expected '{value}'"
            )

    run_async(playwright_event_loop, _step())
