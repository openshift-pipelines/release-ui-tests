"""
Pipelines Operator Navigation scenarios.

Registers the consolidated left-nav smoke feature. Step implementations live in
shared modules loaded via pytest_plugins (test_navigation_steps, test_auth_steps).
"""

from pathlib import Path

from pytest_bdd import scenarios

FEATURE_FILE = Path(__file__).parent.parent / "features" / "pipelines_operator_navigation.feature"
scenarios(FEATURE_FILE)
