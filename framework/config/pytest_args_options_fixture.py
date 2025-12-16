import logging

import pytest
from pytest import Parser, Session

from framework.config.config import Config

logger = logging.getLogger(__name__)


def pytest_addoption(parser: Parser) -> None:
    """
    registers the --ignore-ssl-errors option with Pytest for controlling SSL certificate validation
    :param Parser parser: Pytest argument parser object
    :return: None
    """
    parser.addoption(
        "--ignore-ssl-errors",
        action="store",
        type=lambda x: x.lower() in ("true", "1", "yes", "on"),
        default=True,
        help="Ignore SSL certificate errors (default: True). Set to false to disable.",
    )


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session: Session) -> None:
    """
    Initializes the Config singleton instance, which reads environment variables and validates
    :param Session session: Pytest session object
    :return: None: Raises ValueError if required environment variables are missing.
    """
    Config()
