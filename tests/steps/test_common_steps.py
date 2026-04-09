import asyncio
from typing import Any, Dict

from pytest_bdd import given, parsers, then, when

from framework.config.config import Config
from framework.fixtures.async_bridge import run_async


@given("the user is logged into openshift console with auth kube:admin")
def user_logged_into_openshift_kube_admin(
    page: Dict[str, Any],
    config: Config,
    playwright_event_loop: asyncio.AbstractEventLoop,
    bdd_openshift_console_session: Dict[str, Any],
) -> None:
    """
    Logs in once per feature file (module-scoped browser + session flag), then for later
    scenarios reloads the console and returns to Overview so steps do not depend on the prior
    scenario's last URL.
    """

    async def _ensure_logged_in() -> None:
        if not bdd_openshift_console_session.get("kube_admin_logged_in"):
            assert await page["login"].goto()
            assert await page["login"].verify_successful_navigation_to_login_page()
            assert await page["login"].choose_login_auth_type("kube:admin")
            assert await page["login"].login()
            assert await page["overview"].verify_on_page()
            bdd_openshift_console_session["kube_admin_logged_in"] = True
            return

        await page["raw_page"].goto(config.base_url)
        if "oauth" in page["raw_page"].url.lower():
            bdd_openshift_console_session["kube_admin_logged_in"] = False
            await _ensure_logged_in()
            return

        assert await page["overview"].verify_on_page()

    run_async(playwright_event_loop, _ensure_logged_in())


@given("the user is on the OpenShift login page")
def user_on_login_page(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to and verifying the OpenShift login page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation or verification fails.
    """

    async def _step() -> None:
        assert await page["login"].goto() and await page["login"].verify_successful_navigation_to_login_page()

    run_async(playwright_event_loop, _step())


@when(parsers.parse("user chooses to login with {auth_type}"))
def user_to_chose_login_auth_type(
    page: Dict[str, Any], auth_type: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    step for choosing the authentication type.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :param str auth_type: the type of authentication user chosen for login
    :return: None: Raises AssertionError if login verification fails, TimeoutError if operations timeout.
    """
    run_async(playwright_event_loop, page["login"].choose_login_auth_type(auth_type))


@when("the user logs in with valid credentials")
def user_logs_in(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for performing login with valid credentials.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises AssertionError if login verification fails, TimeoutError if operations timeout.
    """

    async def _step() -> None:
        await page["login"].login()
        await page["overview"].verify_on_page()

    run_async(playwright_event_loop, _step())


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
    step for navigating to the Pipelines section.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation elements are not clickable within the timeout.
    """
    assert run_async(playwright_event_loop, page["nav"].click_pipelines_button())


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
    assert run_async(playwright_event_loop, page["pipelines"].verify_on_page()), "Pipelines page verification failed."
    assert run_async(playwright_event_loop, page["pipelines"].verify_data_load(tab_name="Pipelines tab"))


@when("the user navigates to Pipelines tab")
@then("the user navigates to Pipelines tab")
def user_navigates_to_pipelines_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Pipelines tab on the Pipelines page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["pipelines"].navigate_to_pipelines_tab()), (
        "Failed to navigate to Pipelines tab."
    )
    assert run_async(playwright_event_loop, page["pipelines"].verify_data_load(tab_name="Pipelines tab"))


@when("the user navigates to PipelineRuns tab")
@then("the user navigates to PipelineRuns tab")
def user_navigates_to_pipeline_runs_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the PipelineRuns tab on the Pipelines page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["pipelines"].navigate_to_pipeline_runs_tab()), (
        "Failed to navigate to PipelineRuns tab."
    )
    assert run_async(playwright_event_loop, page["pipelines"].verify_data_load(tab_name="PipelineRuns tab"))


@when("the user navigates to Repositories tab")
@then("the user navigates to Repositories tab")
def user_navigates_to_repositories_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Repositories tab on the Pipelines page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["pipelines"].navigate_to_repositories_tab()), (
        "Failed to navigate to Repositories tab."
    )
    assert run_async(playwright_event_loop, page["pipelines"].verify_data_load(tab_name="Repositories tab"))


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
    assert run_async(playwright_event_loop, page["pipelines_overview"].verify_on_page()), (
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
    assert run_async(playwright_event_loop, page["tasks"].verify_on_page()), "Tasks page verification failed."
    assert run_async(playwright_event_loop, page["tasks"].verify_data_load(tab_name="Tasks tab"))


@when("the user navigates to Tasks tab")
@then("the user navigates to Tasks tab")
def user_navigates_to_tasks_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the Tasks tab on the Tasks page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["tasks"].navigate_to_tasks_tab()), "Failed to navigate to Tasks tab."
    assert run_async(playwright_event_loop, page["tasks"].verify_data_load(tab_name="Tasks tab"))


@when("the user navigates to TaskRuns tab")
@then("the user navigates to TaskRuns tab")
def user_navigates_to_task_runs_tab(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    step for navigating to the TaskRuns tab on the Tasks page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["tasks"].navigate_to_task_runs_tab()), (
        "Failed to navigate to TaskRuns tab."
    )
    assert run_async(playwright_event_loop, page["tasks"].verify_data_load(tab_name="TaskRuns tab"))


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
    assert run_async(playwright_event_loop, page["triggers"].verify_on_page()), "Triggers page verification failed."
    assert run_async(playwright_event_loop, page["triggers"].verify_data_load(tab_name="Triggers tab"))


@when("the user navigates to EventListeners tab")
@then("the user navigates to EventListeners tab")
def user_navigates_to_event_listeners_tab(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    step for navigating to the EventListeners tab on the Triggers page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["triggers"].navigate_to_event_listeners_tab()), (
        "Failed to navigate to EventListeners tab."
    )
    assert run_async(playwright_event_loop, page["triggers"].verify_data_load(tab_name="EventListeners tab"))


@when("the user navigates to TriggerTemplates tab")
@then("the user navigates to TriggerTemplates tab")
def user_navigates_to_trigger_templates_tab(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    step for navigating to the TriggerTemplates tab on the Triggers page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["triggers"].navigate_to_trigger_templates_tab()), (
        "Failed to navigate to TriggerTemplates tab."
    )
    assert run_async(playwright_event_loop, page["triggers"].verify_data_load(tab_name="TriggerTemplates tab"))


@when("the user navigates to TriggerBindings tab")
@then("the user navigates to TriggerBindings tab")
def user_navigates_to_trigger_bindings_tab(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    step for navigating to the TriggerBindings tab on the Triggers page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["triggers"].navigate_to_trigger_bindings_tab()), (
        "Failed to navigate to TriggerBindings tab."
    )
    assert run_async(playwright_event_loop, page["triggers"].verify_data_load(tab_name="TriggerBindings tab"))


@when("the user navigates to ClusterTriggerBindings tab")
@then("the user navigates to ClusterTriggerBindings tab")
def user_navigates_to_cluster_trigger_templates_tab(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    step for navigating to the ClusterTriggerBindings tab on the Triggers page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if tab element is not clickable within the timeout.
    Raises AssertionError if navigation fails.
    """
    assert run_async(playwright_event_loop, page["triggers"].navigate_to_cluster_trigger_bindings_tab()), (
        "Failed to navigate to ClusterTriggerBindings tab."
    )
    assert run_async(playwright_event_loop, page["triggers"].verify_data_load(tab_name="ClusterTriggerBindings tab"))
