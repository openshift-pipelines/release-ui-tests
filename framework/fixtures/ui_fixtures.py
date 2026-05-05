import asyncio
from collections.abc import AsyncGenerator
from typing import Any, Dict

import pytest
import pytest_asyncio
from playwright.async_api import Browser, Page
from pytest import FixtureRequest

import framework.ui_components.overview_page as overview_page_module
from framework.config.config import Config

# Import CLI fixtures to make them available when tests import ui_fixtures
from framework.fixtures.cli_fixtures import openshift_cli, test_project  # noqa: F401
from framework.ui_components.commons.confirmation_modal import ConfirmationModal
from framework.ui_components.commons.left_navigation_bar import LeftNavigationBar
from framework.ui_components.commons.login_page import LoginPage
from framework.ui_components.commons.project_selector import ProjectSelector
from framework.ui_components.overview_page import OverViewPage
from framework.ui_components.page_containers import PipelinesPages, TasksPages, TriggersPages


@pytest.fixture(scope="session")
def config(request: FixtureRequest) -> object:
    """
    fixture that creates and returns a Config singleton instance.
    :param FixtureRequest request: Pytest fixture request object
    :return: Config: A singleton Config object with application configuration.
    """
    return Config()


@pytest.fixture(scope="session")
def playwright_event_loop(request: FixtureRequest) -> asyncio.AbstractEventLoop:
    """
    Session event loop used by pytest-playwright-asyncio and synchronous BDD steps.
    """
    return request.getfixturevalue("_session_event_loop")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: Dict[str, Any], request: FixtureRequest) -> Dict[str, Any]:
    """
    fixture that configures browser context arguments,
    By default, SSL errors are ignored (True). Set --ignore-ssl-errors=false to disable.
    Also maximizes the browser window by setting a large viewport size (1920x1080).
    Note: Navigation timeout is set separately in the context fixture since it's not a valid
    parameter for browser.new_context().
    :param Dict[str, Any] browser_context_args: Default browser context arguments from Playwright.
    :param FixtureRequest request: Pytest fixture request object (automatically injected).
    :return: Dict[str, Any]: Updated browser context arguments with SSL and viewport configuration.
    """
    ignore_ssl = request.config.getoption("--ignore-ssl-errors", default=True)

    return {
        **browser_context_args,
        "ignore_https_errors": ignore_ssl,
        "viewport": {"width": 1920, "height": 1080},  # Maximize browser window
    }


@pytest.fixture(scope="module")
def bdd_openshift_console_session() -> Dict[str, Any]:
    """
    Per-module (feature-registration module) state for BDD steps.
    Used to run full OpenShift login only once per feature file when the Background step
    ``the user is logged into openshift console with auth kube:admin`` is used.
    """
    return {"kube_admin_logged_in": False}


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def playwright_page(
    browser: Browser,
    browser_context_args: Dict[str, Any],
) -> AsyncGenerator[Page, None]:
    """
    One Playwright Page (and its BrowserContext) per test module that registers scenarios.
    Reuse the session ``browser`` from pytest-playwright-asyncio; isolate cookies/storage per feature
    file by registering each ``.feature`` from its own step module (one ``scenarios(...)`` module
    per feature is the supported layout).

    Uses ``browser.new_context`` directly because the plugin's ``new_context`` fixture is
    function-scoped and cannot be requested from module-scoped fixtures.
    """
    context = await browser.new_context(**browser_context_args)
    pw_page = await context.new_page()
    try:
        yield pw_page
    finally:
        await context.close()


@pytest_asyncio.fixture(scope="module", loop_scope="session")
async def page(playwright_page: Page, config: Config) -> Dict[str, Any]:
    """
    fixture that injects hierarchical Page Object containers.
    Scoped to the test module so all scenarios from the same feature registration share one
    browser context. Each module that calls ``scenarios()`` gets a new context.

    Sets default timeout for all page actions (click, fill, wait_for, etc.) and navigation
    operations (goto, reload, etc.) to use framework's configured timeout value (from APP_TIMEOUT
    env var, default 90000ms).

    :param Page playwright_page: Raw Playwright page for this module's browser context.
    :param Config config: Config object containing application configuration
    :return: Dict[str, Any]: Dictionary containing hierarchical page containers:
        - "raw_page": The raw Page object for direct access if needed.
        - "login": LoginPage instance for login-related operations.
        - "nav": LeftNavigationBar instance for navigation operations.
        - "modal": ConfirmationModal instance for modal interactions (delete confirmations, etc.).
        - "project_selector": ProjectSelector instance for switching between projects.
        - "overview": OverViewPage instance for overview page operations.
        - "pipelines": PipelinesPages container with hierarchical structure:
            - pipelines.overview: Pipelines overview dashboard
            - pipelines.list: Pipelines list page
            - pipelines.runs: PipelineRuns list page
            - pipelines.repositories: Repositories list page
            - pipelines.builder: Pipeline builder page
            - pipelines.pipeline.details: Pipeline details page
            - pipelines.pipeline.yaml: Pipeline YAML page
            - pipelines.pipeline.parameters: Pipeline parameters page
            - pipelines.pipeline.runs_tab: Pipeline runs tab page
            - pipelines.pipelinerun.details: PipelineRun details page
            - pipelines.pipelinerun.yaml: PipelineRun YAML page
            - pipelines.pipelinerun.parameters: PipelineRun parameters page
            - pipelines.pipelinerun.logs: PipelineRun logs page
            - pipelines.pipelinerun.task_runs: PipelineRun task runs page
            - pipelines.create_run: Create PipelineRun page
        - "tasks": TasksPages container with hierarchical structure:
            - tasks.list: Tasks list page
            - tasks.runs: TaskRuns list page
            - tasks.task.details: Task details page
            - tasks.task.yaml: Task YAML page
            - tasks.taskrun.details: TaskRun details page
            - tasks.taskrun.yaml: TaskRun YAML page
            - tasks.create: Create Task page
            - tasks.create_run: Create TaskRun page
        - "triggers": TriggersPages container with hierarchical structure:
            - triggers.list: Triggers main page
            - triggers.eventlistener.details: EventListener details page
            - triggers.eventlistener.yaml: EventListener YAML page
            - triggers.triggertemplate.details: TriggerTemplate details page
            - triggers.triggertemplate.yaml: TriggerTemplate YAML page
            - triggers.triggerbinding.details: TriggerBinding details page
            - triggers.triggerbinding.yaml: TriggerBinding YAML page
            - triggers.create.eventlistener: Create EventListener page
            - triggers.create.triggertemplate: Create TriggerTemplate page
            - triggers.create.triggerbinding: Create TriggerBinding page
            - triggers.create.clustertriggerbinding: Create ClusterTriggerBinding page

    Usage examples:
        await page["pipelines"].list.click_create_button()
        await page["pipelines"].pipeline.details.verify_on_page()
        await page["tasks"].task.yaml.click_save()
        await page["triggers"].eventlistener.details.get_eventlistener_name()
    """
    overview_page_module._tour_skipped = False

    playwright_page.set_default_timeout(config.timeout_ms)
    playwright_page.context.set_default_navigation_timeout(config.timeout_ms)

    return {
        "raw_page": playwright_page,
        "login": LoginPage(playwright_page, config),
        "nav": LeftNavigationBar(playwright_page, config),
        "modal": ConfirmationModal(playwright_page, config),
        "project_selector": ProjectSelector(playwright_page, config),
        "overview": OverViewPage(playwright_page, config),
        "pipelines": PipelinesPages(playwright_page, config),
        "tasks": TasksPages(playwright_page, config),
        "triggers": TriggersPages(playwright_page, config),
    }
