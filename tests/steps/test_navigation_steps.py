"""
Navigation Test Steps.

This module contains BDD step definitions for left navigation bar interactions
and high-level navigation to main sections (Pipelines, Tasks, Triggers, Overview).
Follows Single Responsibility Principle - handles only navigation-related steps.
"""

import asyncio
from typing import Any, Dict

from pytest_bdd import given, parsers, then, when

from framework.fixtures.async_bridge import run_async


@given("Validate Pipelines button is visible in the left navigation bar")
@when("Validate Pipelines button is visible in the left navigation bar")
@then("Validate Pipelines button is visible in the left navigation bar")
def validate_pipelines_button_visible(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for validating that the Pipelines button is visible in the left navigation bar.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises AssertionError if Pipelines button is not visible, TimeoutError if operations timeout.
    """
    assert run_async(playwright_event_loop, page["nav"].verify_pipelines_button_visible()), (
        "Pipelines button is not visible in left navigation bar."
    )


@given("the user clicks on Pipelines button")
@when("the user clicks on Pipelines button")
def user_navigates_to_pipelines_section(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Pipelines section (toggles without checking state).
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation elements are not clickable within the timeout.
    """
    assert run_async(playwright_event_loop, page["nav"].click_pipelines_button())


@given("the user expands Pipelines in left navigation bar")
@when("the user expands Pipelines in left navigation bar")
def user_expands_pipelines_menu(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Expands the Pipelines menu in left navigation bar if not already expanded.
    Checks aria-expanded attribute of Pipelines button. If not expanded, clicks Pipelines button to expand.
    If already expanded, does nothing.

    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution.
    :return: None
    """
    import logging
    import time

    logger = logging.getLogger(__name__)

    async def _step() -> None:
        step_start = time.time()
        logger.info("[EXPAND PIPELINES STEP] Starting expand Pipelines step")

        # Check if menu is already expanded using aria-expanded attribute
        check_start = time.time()
        is_expanded = await page["nav"].is_pipelines_menu_expanded()
        check_elapsed = (time.time() - check_start) * 1000
        logger.info(f"[EXPAND PIPELINES STEP] Expansion check took {check_elapsed:.0f}ms, is_expanded={is_expanded}")

        # If not expanded, click Pipelines button to expand
        if not is_expanded:
            click_start = time.time()
            logger.info("[EXPAND PIPELINES STEP] Menu not expanded, clicking Pipelines button...")
            await page["nav"].click_pipelines_button()
            click_elapsed = (time.time() - click_start) * 1000
            logger.info(f"[EXPAND PIPELINES STEP] Click took {click_elapsed:.0f}ms")

            wait_start = time.time()
            await page["raw_page"].wait_for_timeout(500)  # Wait for menu animation
            wait_elapsed = (time.time() - wait_start) * 1000
            logger.info(f"[EXPAND PIPELINES STEP] Post-click wait took {wait_elapsed:.0f}ms")
        else:
            logger.info("[EXPAND PIPELINES STEP] Menu already expanded, skipping click")

        total_elapsed = (time.time() - step_start) * 1000
        logger.info(f"[EXPAND PIPELINES STEP] COMPLETED - Total time: {total_elapsed:.0f}ms")

    run_async(playwright_event_loop, _step())


@given("the user shrinks Pipelines in left navigation bar")
@when("the user shrinks Pipelines in left navigation bar")
def user_shrinks_pipelines_menu(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Shrinks (collapses) the Pipelines menu in left navigation bar if currently expanded.
    Checks aria-expanded attribute of Pipelines button. If expanded, clicks Pipelines button to shrink.
    If already collapsed, does nothing.

    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution.
    :return: None
    """

    async def _step() -> None:
        # Check if menu is expanded using aria-expanded attribute
        is_expanded = await page["nav"].is_pipelines_menu_expanded()

        # If expanded, click Pipelines button to shrink
        if is_expanded:
            await page["nav"].click_pipelines_button()
            await page["raw_page"].wait_for_timeout(500)  # Wait for menu animation

    run_async(playwright_event_loop, _step())


@when("the user navigates to the Pipelines page")
@then("the user navigates to the Pipelines page")
def user_navigates_to_pipelines(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Pipelines page and verifying successful navigation.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation elements are not clickable within the timeout.
    Raises AssertionError if navigation verification fails.
    """
    assert run_async(playwright_event_loop, page["nav"].navigate_to_pipelines()), (
        "Failed to navigate to Pipelines page."
    )
    assert run_async(playwright_event_loop, page["pipelines"].list.verify_on_page()), (
        "Pipelines page verification failed."
    )
    assert run_async(playwright_event_loop, page["pipelines"].list.verify_data_load(tab_name="Pipelines tab"))


@when("the user navigates to PipelineRuns tab")
@then("the user navigates to PipelineRuns tab")
def user_navigates_to_pipeline_runs_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the PipelineRuns tab on the Pipelines page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["pipelines"].list.navigate_to_pipeline_runs_tab()), (
        "Failed to navigate to PipelineRuns tab."
    )
    assert run_async(playwright_event_loop, page["pipelines"].list.verify_data_load(tab_name="PipelineRuns tab"))


@when("the user navigates to the Overview page")
@then("the user navigates to the Overview page")
def user_navigates_to_overview(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Pipelines Overview page and verifying successful navigation.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation elements are not clickable within the timeout.
    Raises AssertionError if navigation verification fails.
    """
    assert run_async(playwright_event_loop, page["nav"].navigate_to_overview()), "Failed to navigate to Overview page."
    assert run_async(playwright_event_loop, page["pipelines"].overview.verify_on_page()), (
        "Pipelines Overview page verification failed."
    )


@when("the user navigates to the Tasks page")
@then("the user navigates to the Tasks page")
def user_navigates_to_tasks(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Tasks page and verifying successful navigation.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation elements are not clickable within the timeout.
    Raises AssertionError if navigation verification fails.
    """
    assert run_async(playwright_event_loop, page["nav"].navigate_to_tasks()), "Failed to navigate to Tasks page."
    assert run_async(playwright_event_loop, page["tasks"].list.verify_on_page()), "Tasks page verification failed."
    assert run_async(playwright_event_loop, page["tasks"].list.verify_data_load(tab_name="Tasks tab"))


@when("the user navigates to the Triggers page")
@then("the user navigates to the Triggers page")
def user_navigates_to_triggers(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Triggers page and verifying successful navigation.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation elements are not clickable within the timeout.
    Raises AssertionError if navigation verification fails.
    """
    assert run_async(playwright_event_loop, page["nav"].navigate_to_triggers()), "Failed to navigate to Triggers page."
    assert run_async(playwright_event_loop, page["triggers"].list.verify_on_page()), (
        "Triggers page verification failed."
    )
    assert run_async(playwright_event_loop, page["triggers"].list.verify_data_load(tab_name="Triggers tab"))


@then(parsers.parse("Verify the following {links} are available under Pipelines button"))
def verify_links_available_under_pipelines_button(
    page: Dict[str, Any], links: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    step for verifying that a specific link is available under the Pipelines button in the left navigation bar.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :param str links: The name of the link to verify (e.g., "Overview", "Pipelines", "Tasks", "Triggers").
    :return: None: Raises AssertionError if the link is not visible or if an invalid link name is provided.
    """
    assert run_async(playwright_event_loop, page["nav"].verify_link_available_under_pipelines_button(links)), (
        f"Link '{links}' is not available under Pipelines button."
    )


@when("the user navigates to Tasks tab")
@then("the user navigates to Tasks tab")
def user_navigates_to_tasks_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Tasks tab on the Tasks page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["tasks"].list.navigate_to_tasks_tab()), (
        "Failed to navigate to Tasks tab."
    )
    assert run_async(playwright_event_loop, page["tasks"].list.verify_data_load(tab_name="Tasks tab"))


@when("the user navigates to TaskRuns tab")
@then("the user navigates to TaskRuns tab")
def user_navigates_to_task_runs_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the TaskRuns tab on the Tasks page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["tasks"].list.navigate_to_task_runs_tab()), (
        "Failed to navigate to TaskRuns tab."
    )
    assert run_async(playwright_event_loop, page["tasks"].list.verify_data_load(tab_name="TaskRuns tab"))


@then("the tasks page should be visible")
def tasks_page_visible(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for verifying that the Tasks page is visible.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises AssertionError if Tasks page is not visible, TimeoutError if URL doesn't match.
    """
    assert run_async(playwright_event_loop, page["tasks"].list.verify_on_page()), "Tasks page header not visible."
