"""
CLI Fixtures for OpenShift Integration.

Provides pytest fixtures for OpenShift CLI operations, including:
- Isolated test project creation per feature file
- Automatic project cleanup on test completion
- CLI authentication and context management
"""

import logging
import os

import pytest

from framework.cli.openshift_cli import OpenShiftCLI

logger = logging.getLogger(__name__)


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
async def test_project(openshift_cli: OpenShiftCLI, request) -> str:
    """
    Module-scoped fixture that creates an isolated project for each feature file.

    Creates a unique project with name: release-ui-test-{5_random_chars}
    Yields the project name for use in tests.
    Automatically deletes the project after tests complete (only if all tests passed).

    :param OpenShiftCLI openshift_cli: CLI wrapper instance
    :param request: pytest request object for accessing test metadata
    :return: str: The created project name
    :raises: RuntimeError if project creation fails
    """
    # Ensure we're logged in (either via token or previous oc login)
    is_logged_in = await openshift_cli.is_logged_in()

    if not is_logged_in:
        # Try to login with token if available
        if openshift_cli.token and openshift_cli.api_url:
            login_success = await openshift_cli.login()
            if not login_success:
                raise RuntimeError(
                    "Not logged into OpenShift cluster. "
                    "Either run 'oc login' manually or set OC_TOKEN and OC_API_URL env vars"
                )
        else:
            raise RuntimeError(
                "Not logged into OpenShift cluster and no token/API URL provided. "
                "Run 'oc login' or set OC_TOKEN and OC_API_URL environment variables"
            )

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
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results for project cleanup decision.

    Attaches test result to the request node so test_project fixture
    can check if tests failed before deciding to delete the project.
    """
    outcome = yield
    rep = outcome.get_result()

    # Store result in item for later access
    setattr(item, f"rep_{rep.when}", rep)
