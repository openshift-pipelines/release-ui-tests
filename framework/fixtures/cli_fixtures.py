"""
CLI Fixtures for OpenShift Integration.

Provides pytest fixtures for OpenShift CLI operations, including:
- Isolated test project creation per feature file
- Automatic project cleanup on test completion
- CLI authentication and context management

Configuration Loading:
- Environment variables are loaded from .env file at module import time
- Priority: 1. Environment Variable (CI), 2. .env file (local dev), 3. Defaults
- This ensures consistent behavior between local development and CI environments
"""

import logging
import os
from pathlib import Path
from typing import Generator

import pytest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from dotenv import load_dotenv

from framework.cli.openshift_cli import OpenShiftCLI, derive_api_url_from_console_url
from framework.config.config import Config

logger = logging.getLogger(__name__)

# Load .env file at module level to ensure configuration is available before fixtures run
# This happens once when the module is first imported
# Note: override=False means environment variables take precedence over .env file
project_root = Path(__file__).parent.parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path=dotenv_path, override=False)

# Flag to track if CLI login has been performed in this test session
# Avoids redundant login checks across multiple test modules
_cli_logged_in = False


async def _perform_cli_login(openshift_cli: OpenShiftCLI) -> None:
    """
    Perform CLI login using available credentials.

    Tries token-based login first, then falls back to username/password.

    :param OpenShiftCLI openshift_cli: CLI wrapper instance
    :raises RuntimeError: If login fails
    """
    logger.info("Not currently logged in to OpenShift cluster - attempting login")

    # Try method 1: Login with token (if OC_TOKEN and OC_API_URL are set)
    if openshift_cli.token and openshift_cli.api_url:
        logger.info("Attempting login with OC_TOKEN")
        login_success = await openshift_cli.login()
        if login_success:
            logger.info("Successfully logged in with token")
        else:
            raise RuntimeError("Login with token failed. Check OC_TOKEN and OC_API_URL values")
        return

    # Try method 2: Login with username/password (from Config/env vars)
    logger.info("OC_TOKEN not set - attempting login with username/password from Config")
    try:
        config = Config()

        # Derive API URL from console URL
        api_url = derive_api_url_from_console_url(config.base_url)

        if not api_url:
            raise RuntimeError(
                f"Could not derive API URL from console URL: {config.base_url}. "
                "Set OC_API_URL environment variable explicitly."
            )

        logger.info(f"Using API URL: {api_url}")
        login_success = await openshift_cli.login_with_credentials(
            api_url=api_url, username=config.username, password=config.password
        )

        if login_success:
            logger.info(f"Successfully logged in as {config.username}")
        else:
            raise RuntimeError("Login with username/password failed. Check CONSOLE_USERNAME and CONSOLE_PASSWORD")

    except ValueError as e:
        raise RuntimeError(
            f"Cannot login to OpenShift cluster. Missing configuration: {e}. "
            "Set OC_TOKEN + OC_API_URL OR CONSOLE_USERNAME + CONSOLE_PASSWORD + CONSOLE_URL"
        ) from e


@pytest.fixture(scope="session")
def openshift_cli() -> OpenShiftCLI:
    """
    Session-scoped OpenShift CLI instance.

    Reads OC_TOKEN and API URL from environment if available.
    Returns an OpenShiftCLI instance that can be used for cluster operations.

    :return: OpenShiftCLI: CLI wrapper instance
    """
    # Get token from environment (optional - may already be logged in via oc login)
    token = os.getenv("OC_TOKEN")
    api_url = os.getenv("OC_API_URL")  # e.g., https://api.cluster.example.com:6443

    cli = OpenShiftCLI(api_url=api_url, token=token)
    logger.info("OpenShift CLI instance created")
    return cli


@pytest.fixture(scope="module")
async def test_project(openshift_cli: OpenShiftCLI, request: pytest.FixtureRequest) -> str:
    """
    Module-scoped fixture that creates an isolated project for each feature file.

    Creates a unique project with name: release-ui-test-{5_random_chars}
    Yields the project name for use in tests.
    Automatically deletes the project after tests complete (only if all tests passed).

    Uses a session-level flag to ensure login only happens once across all test modules,
    avoiding redundant login checks and improving test execution speed.

    :param OpenShiftCLI openshift_cli: CLI wrapper instance
    :param pytest.FixtureRequest request: pytest request object for accessing test metadata
    :return: str: The created project name
    :raises: RuntimeError if project creation fails
    """
    global _cli_logged_in

    # Check session-level login flag first to avoid redundant login checks
    if not _cli_logged_in:
        logger.info("First test module - checking CLI login status")
        await _perform_cli_login(openshift_cli)
    else:
        logger.info("Already logged in to OpenShift cluster")

    # Mark login as complete for this session
    _cli_logged_in = True
    logger.info("CLI login status confirmed - subsequent modules will skip login check")

    # Generate unique project name
    project_name = openshift_cli.generate_random_project_name()

    # Get feature file name for display name
    feature_file = getattr(request.module, "__file__", "unknown")
    display_name = f"UI Test: {os.path.basename(feature_file)}"

    logger.info(f"Creating test project: {project_name}")
    success = await openshift_cli.create_project(project_name, display_name=display_name)

    if not success:
        raise RuntimeError(f"Failed to create test project: {project_name}")

    # Switch to the new project
    await openshift_cli.switch_project(project_name)

    # Store original project to restore later (if needed)
    original_project = await openshift_cli.get_current_project()

    yield project_name

    # Teardown - Check if any tests failed
    # request.session.testsfailed gives total failures in session
    # We want module-level failure check, so we check request.node
    has_failures = False
    if hasattr(request.node, "rep_call"):
        has_failures = request.node.rep_call.failed

    # Alternative: check via session (less granular but more reliable)
    try:
        session_failed = request.session.testsfailed > 0
    except AttributeError:
        session_failed = False

    if not has_failures and not session_failed:
        logger.info(f"All tests passed - deleting test project: {project_name}")
        await openshift_cli.delete_project(project_name, wait=False)
    else:
        logger.warning(
            f"Tests failed - keeping project {project_name} for debugging. "
            f"Delete manually with: oc delete project {project_name}"
        )

    # Restore original project context (optional)
    if original_project and original_project != project_name:
        await openshift_cli.switch_project(original_project)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo[None]) -> Generator[None, None, None]:
    """
    Hook to capture test results for project cleanup decision.

    Attaches test result to the request node so test_project fixture
    can check if tests failed before deciding to delete the project.

    :param Item item: The test item being executed
    :param CallInfo call: Information about the call phase
    :return: Generator for hook wrapper
    """
    outcome = yield
    rep = outcome.get_result()

    # Store result in item for later access
    setattr(item, f"rep_{rep.when}", rep)
