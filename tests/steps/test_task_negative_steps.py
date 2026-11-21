"""BDD step definitions for Task validation and cancellation scenarios."""

import asyncio
from pathlib import Path
from typing import Any, Dict, Iterable

from pytest_bdd import parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_loader import YamlLoader
from framework.locators.commons import AlertLocators

FEATURE_FILE = Path(__file__).parent.parent / "features" / "task_negative.feature"
scenarios(FEATURE_FILE)


async def _open_create_task(page: Dict[str, Any]) -> None:
    assert await page["tasks"].list.click_create_button(), "Failed to open the Create menu"
    assert await page["tasks"].list.click_create_task_menu_item(), "Failed to open the Create Task page"
    assert await page["tasks"].create.verify_on_page(), "Create Task page did not appear"


async def _assert_alert(page: Dict[str, Any], fragments: Iterable[str] = ()) -> None:
    alert = page["raw_page"].locator(AlertLocators.ERROR_ALERT).last
    await alert.wait_for(state="visible")
    alert_text = (await alert.inner_text()).strip()
    assert alert_text, "Validation alert was displayed without an error message"
    for fragment in fragments:
        assert fragment in alert_text, f"Expected alert to contain {fragment!r}, but received {alert_text!r}"


@when(parsers.parse('the user submits task YAML file "{yaml_file}"'))
def submit_task_yaml(page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Submit a Task YAML file from the Create Task page."""

    async def _step() -> None:
        await _open_create_task(page)
        yaml_content = YamlLoader.load_task_yaml(yaml_file)
        assert await page["tasks"].create.monaco_editor.set_content(yaml_content), "Failed to set task YAML"
        assert await page["tasks"].create.click_create(), "Failed to submit task YAML"

    run_async(playwright_event_loop, _step())


@then(parsers.parse("a task validation error alert is displayed"))
def verify_task_validation_error(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Verify the Create or Edit Task page displays a validation error."""
    run_async(playwright_event_loop, _assert_alert(page))


@when(parsers.parse('the user creates a valid task from YAML file "{yaml_file}"'))
def create_valid_task(page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Create the task that later negative scenarios operate on."""

    async def _step() -> None:
        await _open_create_task(page)
        yaml_content = YamlLoader.load_task_yaml(yaml_file)
        assert await page["tasks"].create.monaco_editor.set_content(yaml_content), "Failed to set task YAML"
        assert await page["tasks"].create.click_create(), "Failed to create the valid task"
        assert await page["tasks"].task.details.verify_on_page(), "Task details page did not appear after creation"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user edits task "{task_name}" with invalid YAML file "{yaml_file}"'))
def edit_task_with_invalid_yaml(
    page: Dict[str, Any], task_name: str, yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Replace a task's editor content with invalid YAML and attempt to save it."""

    async def _step() -> None:
        assert await page["tasks"].list.click_task_kebab_menu(task_name), f"Failed to open actions for '{task_name}'"
        assert await page["tasks"].list.click_edit_task_menu_item(), f"Failed to open YAML for '{task_name}'"
        assert await page["tasks"].task.yaml.verify_on_page(), "Task YAML page did not appear"
        yaml_content = YamlLoader.load_task_yaml(yaml_file)
        assert await page["tasks"].task.yaml.monaco_editor.set_content(yaml_content), "Failed to set invalid task YAML"
        assert await page["tasks"].task.yaml.click_save(), "Failed to submit invalid task YAML"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user opens the Edit annotations dialog for task "{task_name}"'))
def open_annotations_dialog(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open the selected task's Edit annotations dialog from its kebab menu."""

    async def _step() -> None:
        assert await page["tasks"].list.click_task_kebab_menu(task_name), f"Failed to open actions for '{task_name}'"
        assert await page["tasks"].list.open_edit_annotations_dialog(), "Edit annotations dialog did not appear"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user submits invalid annotation "{key}" with value "{value}"'))
def submit_invalid_annotation(
    page: Dict[str, Any], key: str, value: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Add an invalid annotation key and submit the annotations dialog."""
    run_async(playwright_event_loop, page["tasks"].list.annotations_modal.add_annotations({key: value}))


@then(parsers.parse('an annotations validation error alert is displayed for "{key}"'))
def verify_annotations_validation_error(
    page: Dict[str, Any], key: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Verify the annotations validation error identifies the invalid key."""
    run_async(playwright_event_loop, _assert_alert(page, (f'Invalid value: "{key}"', "metadata.annotations")))


@then(parsers.parse("the user closes the edit annotations dialog"))
def close_annotations_dialog(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Close the Edit annotations dialog after a rejected save."""
    run_async(playwright_event_loop, page["tasks"].list.annotations_modal.close_annotations_dialog())


@when(parsers.parse('the user opens the Edit labels dialog for task "{task_name}"'))
def open_labels_dialog(page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Open the selected task's Edit labels dialog from its kebab menu."""

    async def _step() -> None:
        assert await page["tasks"].list.click_task_kebab_menu(task_name), f"Failed to open actions for '{task_name}'"
        assert await page["tasks"].list.open_edit_labels_dialog(), "Edit labels dialog did not appear"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user submits invalid label "{key}" with value "{value}"'))
def submit_invalid_label(
    page: Dict[str, Any], key: str, value: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Enter an invalid label key and submit the labels dialog."""
    run_async(playwright_event_loop, page["tasks"].list.labels_modal.add_labels({key: value}))


@then(parsers.parse('a labels validation error alert is displayed for "{key}"'))
def verify_labels_validation_error(
    page: Dict[str, Any], key: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Verify the labels validation error identifies the invalid key."""
    run_async(playwright_event_loop, _assert_alert(page, (f'Invalid value: "{key}"', "metadata.labels")))


@then(parsers.parse("the user closes the edit labels dialog"))
def close_labels_dialog(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Close the Edit labels dialog after a rejected save."""
    run_async(playwright_event_loop, page["tasks"].list.labels_modal.close_labels_dialog())


@when(parsers.parse('the user enters task YAML file "{yaml_file}" and cancels creation'))
def enter_yaml_and_cancel_creation(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Enter task YAML, cancel instead of creating, and return to the Tasks list."""

    async def _step() -> None:
        await _open_create_task(page)
        yaml_content = YamlLoader.load_task_yaml(yaml_file)
        assert await page["tasks"].create.monaco_editor.set_content(yaml_content), "Failed to set task YAML"
        assert await page["tasks"].create.click_cancel(), "Failed to cancel task creation"
        assert await page["tasks"].list.verify_data_load(), "Tasks list did not appear after cancelling creation"

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task "{task_name}" should not appear in the tasks list'))
def verify_task_absent(page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Verify a task that was never created is absent from the Tasks list."""

    async def _step() -> None:
        assert await page["tasks"].list.verify_task_not_in_list(task_name), (
            f"Task '{task_name}' appears in the Tasks list"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user starts deletion of task "{task_name}" and cancels it'))
def start_and_cancel_task_deletion(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open a task deletion confirmation and cancel it."""

    async def _step() -> None:
        assert await page["tasks"].list.click_task_kebab_menu(task_name), f"Failed to open actions for '{task_name}'"
        assert await page["tasks"].list.click_delete_task_menu_item(), f"Failed to start deletion for '{task_name}'"
        assert await page["modal"].is_modal_visible(), "Delete confirmation dialog did not appear"
        assert await page["modal"].click_cancel(), "Failed to cancel task deletion"

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the task "{task_name}" should appear in the tasks list'))
def verify_task_present(page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Verify a task remains listed after cancelling deletion."""

    async def _step() -> None:
        assert await page["tasks"].list.verify_data_load(), "Tasks list failed to load"
        assert await page["tasks"].list.verify_task_in_list(task_name), (
            f"Task '{task_name}' is missing from the Tasks list"
        )

    run_async(playwright_event_loop, _step())
