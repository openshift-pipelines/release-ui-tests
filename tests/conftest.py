# Import fixtures from framework
from framework.fixtures.ui_fixtures import *  # noqa: F403, F401

# Register plugins to load step definitions
pytest_plugins = [
    "tests.steps.test_common_steps",
]
