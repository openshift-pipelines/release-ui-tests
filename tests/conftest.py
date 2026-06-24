"""
Test configuration and fixtures.

This module configures pytest for BDD test execution, registers step definition plugins,
and implements custom collection hooks for test skipping.
"""

import pytest

# Import fixtures from framework
from framework.fixtures.ui_fixtures import *  # noqa: F403, F401

# Register step definition plugins
# test_shared_steps contains steps used across multiple feature files
pytest_plugins = [
    "tests.steps.test_auth_steps",
    "tests.steps.test_navigation_steps",
    "tests.steps.test_shared_steps",
]


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """
    Automatically skip test scenarios tagged with @skip or @known_bug in feature files.

    This hook runs after test collection and adds pytest.mark.skip to any scenario
    that has the @skip or @known_bug tag in the feature file. The skip reason is
    configured to point users to the feature file for bug details.

    :param config: pytest config object
    :param items: List of collected test items
    """
    for item in items:
        # Check if scenario has @skip tag
        if "skip" in item.keywords:
            item.add_marker(
                pytest.mark.skip(reason="Scenario skipped - see feature file comments for known bug details")
            )
        # Also handle @known_bug as alias for @skip
        elif "known_bug" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="Known bug - see feature file comments for tracking information"))
