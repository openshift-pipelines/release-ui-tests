"""BDD step definitions for TaskRun validation and cancellation scenarios."""

import asyncio
from pathlib import Path
from typing import Any, Dict, Iterable

from pytest_bdd import parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async
from framework.helpers.yaml_loader import YamlLoader
from framework.locators.commons import AlertLocators

FEATURE_FILE = Path(__file__).parent.parent / "features" / "taskrun_negative.feature"
scenarios(FEATURE_FILE)


async def _open_create_taskrun(page: Dict[str, Any]) -> None:
    assert await page["tasks"].list.click_create_button(), "Failed to open the Create menu"
    assert await page["tasks"].list.click_create_task_run_menu_item(), "Failed to open the Create TaskRun page"
    assert await page["tasks"].create_run.verify_on_page(), "Create TaskRun page did not appear"


async def _navigate_to_taskruns_tab(page: Dict[str, Any]) -> None:
    assert await page["tasks"].list.navigate_to_task_runs_tab(), "Failed to navigate to the TaskRuns tab"
    assert await page["tasks"].runs.verify_task_runs_tab_data_load(), "TaskRuns list failed to load"


async def _assert_alert(page: Dict[str, Any], fragments: Iterable[str] = ()) -> None:
    alert = page["raw_page"].locator(AlertLocators.ERROR_ALERT).last
    await alert.wait_for(state="visible")
    alert_text = (await alert.inner_text()).strip()
    assert alert_text, "Validation alert was displayed without an error message"
    for fragment in fragments:
        assert fragment in alert_text, f"Expected alert to contain {fragment!r}, but received {alert_text!r}"


@when(parsers.parse('the user submits taskrun YAML file "{yaml_file}"'))
def submit_taskrun_yaml(page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Submit a TaskRun YAML file from the Create TaskRun page."""

    async def _step() -> None:
        await _navigate_to_taskruns_tab(page)
        await _open_create_taskrun(page)
        yaml_content = YamlLoader.load_taskrun_yaml(yaml_file)
        assert await page["tasks"].create_run.monaco_editor.set_content(yaml_content), "Failed to set taskrun YAML"
        assert await page["tasks"].create_run.click_create(), "Failed to submit taskrun YAML"

    run_async(playwright_event_loop, _step())


@then(parsers.parse("a taskrun validation error alert is displayed"))
def verify_taskrun_validation_error(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Verify the Create or Edit TaskRun page displays a validation error."""
    run_async(playwright_event_loop, _assert_alert(page))


@when(parsers.parse('the user creates a valid taskrun from YAML file "{yaml_file}"'))
def create_valid_taskrun(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Create the TaskRun that later negative scenarios operate on."""

    async def _step() -> None:
        await _navigate_to_taskruns_tab(page)
        await _open_create_taskrun(page)
        yaml_content = YamlLoader.load_taskrun_yaml(yaml_file)
        assert await page["tasks"].create_run.monaco_editor.set_content(yaml_content), "Failed to set taskrun YAML"
        assert await page["tasks"].create_run.click_create(), "Failed to create the valid taskrun"
        assert await page["tasks"].taskrun.details.verify_on_page(), (
            "TaskRun details page did not appear after creation"
        )

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the user should not find save button for taskrun "{taskrun_name}" in taskrun yaml page'))
def validate_user_cannot_edit_existing_taskrun(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open the TaskRun YAML tab and assert Save is absent (completed TaskRuns are read-only)."""

    async def _step() -> None:
        assert await page["tasks"].runs.click_on_given_taskrun_in_list(taskrun_name), (
            f"Failed to open TaskRun '{taskrun_name}' from the list"
        )
        assert await page["tasks"].taskrun.details.verify_on_page(), (
            f"TaskRun details page did not appear for '{taskrun_name}'"
        )
        assert await page["tasks"].taskrun.details.navigate_to_yaml_tab(), (
            f"Failed to open YAML tab for '{taskrun_name}'"
        )
        assert await page["tasks"].taskrun.yaml.verify_on_page(), "TaskRun YAML page did not appear"

        # Short timeout: Save must not appear on a completed (read-only) TaskRun.
        save_visible = await page["tasks"].taskrun.yaml.is_save_button_visible(timeout=5000)
        assert not save_visible, f"Save button unexpectedly appeared on the YAML page for TaskRun '{taskrun_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user opens the Edit annotations dialog for taskrun "{taskrun_name}"'))
def open_taskrun_annotations_dialog(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open Edit annotations from the TaskRun details page (list kebab has no annotations action)."""

    async def _step() -> None:
        await _navigate_to_taskruns_tab(page)
        assert await page["tasks"].runs.click_on_given_taskrun_in_list(taskrun_name), (
            f"Failed to open TaskRun '{taskrun_name}' from the list"
        )
        assert await page["tasks"].taskrun.details.verify_on_page(), (
            f"TaskRun details page did not appear for '{taskrun_name}'"
        )
        assert await page["tasks"].taskrun.details.click_edit_annotations(), "Edit annotations dialog did not appear"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user opens the Edit labels dialog for taskrun "{taskrun_name}"'))
def open_taskrun_labels_dialog(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open Edit labels from the TaskRun details page (list kebab has no labels action)."""

    async def _step() -> None:
        await _navigate_to_taskruns_tab(page)
        assert await page["tasks"].runs.click_on_given_taskrun_in_list(taskrun_name), (
            f"Failed to open TaskRun '{taskrun_name}' from the list"
        )
        assert await page["tasks"].taskrun.details.verify_on_page(), (
            f"TaskRun details page did not appear for '{taskrun_name}'"
        )
        assert await page["tasks"].taskrun.details.click_edit_labels(), "Edit labels dialog did not appear"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user submits invalid taskrun annotation "{key}" with value "{value}"'))
def submit_invalid_taskrun_annotation(
    page: Dict[str, Any], key: str, value: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Add an invalid annotation key and submit the TaskRun annotations dialog."""
    run_async(playwright_event_loop, page["tasks"].taskrun.details.annotations_modal.add_annotations({key: value}))


@then(parsers.parse('a taskrun annotations validation error alert is displayed for "{key}"'))
def verify_taskrun_annotations_validation_error(
    page: Dict[str, Any], key: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Verify the annotations validation error identifies the invalid key."""
    run_async(playwright_event_loop, _assert_alert(page, (f'Invalid value: "{key}"', "metadata.annotations")))


@then(parsers.parse("the user closes the taskrun edit annotations dialog"))
def close_taskrun_annotations_dialog(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Close the TaskRun Edit annotations dialog after a rejected save."""
    run_async(playwright_event_loop, page["tasks"].taskrun.details.annotations_modal.close_annotations_dialog())


@when(parsers.parse('the user submits invalid taskrun label "{key}" with value "{value}"'))
def submit_invalid_taskrun_label(
    page: Dict[str, Any], key: str, value: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Enter an invalid label key and submit the TaskRun labels dialog."""
    run_async(playwright_event_loop, page["tasks"].taskrun.details.labels_modal.add_labels({key: value}))


@then(parsers.parse('a taskrun labels validation error alert is displayed for "{key}"'))
def verify_taskrun_labels_validation_error(
    page: Dict[str, Any], key: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Verify the labels validation error identifies the invalid key."""
    run_async(playwright_event_loop, _assert_alert(page, (f'Invalid value: "{key}"', "metadata.labels")))


@then(parsers.parse("the user closes the taskrun edit labels dialog"))
def close_taskrun_labels_dialog(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Close the TaskRun Edit labels dialog after a rejected save."""
    run_async(playwright_event_loop, page["tasks"].taskrun.details.labels_modal.close_labels_dialog())


@when(parsers.parse('the user enters taskrun YAML file "{yaml_file}" and cancels creation'))
def enter_taskrun_yaml_and_cancel_creation(
    page: Dict[str, Any], yaml_file: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Enter TaskRun YAML, cancel instead of creating, and return to the TaskRuns list."""

    async def _step() -> None:
        await _navigate_to_taskruns_tab(page)
        await _open_create_taskrun(page)
        yaml_content = YamlLoader.load_taskrun_yaml(yaml_file)
        assert await page["tasks"].create_run.monaco_editor.set_content(yaml_content), "Failed to set taskrun YAML"
        assert await page["tasks"].create_run.click_cancel(), "Failed to cancel taskrun creation"
        assert await page["tasks"].runs.verify_task_runs_tab_data_load(), (
            "TaskRuns list did not appear after cancelling creation"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user starts deletion of taskrun "{taskrun_name}" and cancels it'))
def start_and_cancel_taskrun_deletion(
    page: Dict[str, Any], taskrun_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Open a TaskRun deletion confirmation and cancel it."""

    async def _step() -> None:
        await _navigate_to_taskruns_tab(page)
        assert await page["tasks"].runs.click_taskrun_kebab_menu(taskrun_name), (
            f"Failed to open actions for '{taskrun_name}'"
        )
        assert await page["tasks"].runs.click_delete_taskrun_menu_item(), (
            f"Failed to start deletion for '{taskrun_name}'"
        )
        assert await page["modal"].is_modal_visible(), "Delete confirmation dialog did not appear"
        assert await page["modal"].click_cancel(), "Failed to cancel taskrun deletion"

    run_async(playwright_event_loop, _step())
