import asyncio
from typing import Any, Dict

from pytest_bdd import scenarios, then

from framework.fixtures.async_bridge import run_async

scenarios("tasks_test.feature")


@then("the tasks page should be visible")
def pipelines_page_visible(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for verifying that the Pipelines page is visible.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises AssertionError if Pipelines page is not visible, TimeoutError if URL doesn't match.
    """
    assert run_async(playwright_event_loop, page["pipelines"].verify_on_page()), "Pipelines page header not visible."
