from typing import Any, Dict

from pytest_bdd import given, parsers, when


@given("the user is on the OpenShift login page")
def user_on_login_page(page: Dict[str, Any]) -> None:
    """
    step for navigating to and verifying the OpenShift login page.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation or verification fails.
    """
    assert page["login"].goto() and page["login"].verify_successful_navigation_to_login_page()


@when(parsers.parse("user chooses to login with {auth_type}"))
def user_to_chose_login_auth_type(page: Dict[str, Any], auth_type: str) -> None:
    """
    step for choosing the authentication type.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :param str auth_type: the type of authentication user chosen for login
    :return: None: Raises AssertionError if login verification fails, TimeoutError if operations timeout.
    """
    page["login"].choose_login_auth_type(auth_type)


@when("the user logs in with valid credentials")
def user_logs_in(page: Dict[str, Any]) -> None:
    """
    step for performing login with valid credentials.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises AssertionError if login verification fails, TimeoutError if operations timeout.
    """
    page["login"].login()
    # Verify login
    assert page["nav"].verify_successful_login(), "Login verification failed."


@when("the user navigates to the Pipelines section")
def user_navigates_to_pipelines(page: Dict[str, Any]) -> None:
    """
    step for navigating to the Pipelines section.
    :param Dict[str, Any] page: Dictionary containing Page Object instances (from page fixture).
    :return: None: Raises TimeoutError if navigation elements are not clickable within the timeout.
    """
    assert page["nav"].navigate_to_pipelines()
