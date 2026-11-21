"""
Automation framework assertions
"""

from typing import List, Union


def _print_assert_message(message: str, expected_result: str, actual_result: str) -> str:
    return f"{message}\nExpected result: {expected_result}\nActual result: {actual_result}"


# Asserts actual result is equal to expected result
def assert_equals(actual_result: List, expected_result: List, message: str = None) -> str:
    """
    Asserts that two values are equal, providing a helpful error message if not.
    Handles potential case-sensitivity issues on Windows.

    :param actual_result: The actual value obtained.
    :param expected_result: The expected value to compare against.
    :param message: (Optional) A custom error message to display on failure.
    """
    if message is None:
        message = f"'{actual_result}' is not equal to '{expected_result}'"

    else:
        assert actual_result == expected_result, _print_assert_message(
            message=message,
            expected_result=expected_result,
            actual_result=actual_result,
        )


# Asserts actual result is equal to expected result
def assert_not_equals(
    actual_result: Union[str, int, List[str]],
    expected_result: Union[str, int, List[str]],
    message: str = None,
) -> None:
    """
    Asserts that two values are NOT equal.

    :param actual_result: The actual value obtained.
    :param expected_result: The value that should not be equal to `actual_result`.
    :param message: (Optional) A custom error message to display on failure.
    """
    if message is None:
        message = f"'{actual_result}' should not be equal to '{expected_result}'"
    assert actual_result != expected_result, _print_assert_message(
        message=message, expected_result=expected_result, actual_result=actual_result
    )


# Asserts wanted text appears in actual result
def assert_contains(actual_result: str, wanted_text: str, message: str = None) -> None:
    """
    Asserts that a string (wanted_text) is a substring of another (actual_result),
    ignoring case and extra whitespace.

    :param actual_result: The string to search within.
    :param wanted_text: The string to search for.
    :param message: (Optional) A custom error message to display on failure.
    """
    normalized_actual = " ".join(str(actual_result).lower().split()).strip()
    normalized_wanted = " ".join(str(wanted_text).lower().split()).strip()

    if message is None:
        message = f"'{wanted_text}' not found in '{actual_result}'"

    assert normalized_wanted in normalized_actual, _print_assert_message(
        message=message, expected_result=wanted_text, actual_result=actual_result
    )


def assert_does_not_contain(actual_result: str, unwanted_text: str, message: str = None) -> None:
    """
    Asserts that a string (unwanted_text) is NOT a substring of another (actual_result),
    ignoring case and extra whitespace.

    :param actual_result: The string to search within.
    :param unwanted_text: The string that should not be present.
    :param message: (Optional) A custom error message to display on failure.
    """
    normalized_actual = " ".join(str(actual_result).lower().split()).strip()
    normalized_unwanted = " ".join(str(unwanted_text).lower().split()).strip()

    if message is None:
        message = f"'{unwanted_text}' should not be found in '{actual_result}'"

    assert normalized_unwanted not in normalized_actual, _print_assert_message(
        message=message,
        expected_result=f"Should not include '{unwanted_text}'",
        actual_result=actual_result,
    )


def assert_lists_equals(first_list: str, second_list: str, message: str = None) -> None:
    """
    Asserts that two lists contain the same elements, regardless of order.

    :param first_list: The first list to compare.
    :param second_list: The second list to compare.
    :param message: (Optional) A custom error message to display on failure.
    """

    first_list = list(first_list) if first_list is not None else []
    second_list = list(second_list) if second_list is not None else []
    difference = set(second_list).difference(set(first_list))
    difference_to_string = "".join(difference)
    if message is None:
        message = f"Those elements are missing: {difference_to_string}"

    assert sorted(first_list) == sorted(second_list), message


def assert_item_in_list(
    verified_item: str,
    actual_list: List,
    message: str = None,
    check_list_items: bool = False,
) -> None:
    """
    Assert that an item (or part of it) exists within a list.

    :param verified_item: The item to search for.
    :param actual_list (list): The list to search within.
    :param message (str, optional): A custom error message. Defaults to None.
    :param check_list_items (bool, optional):
        If True, checks if any item in the list is a substring of the verified_item
        (case-insensitive). If False, checks if the verified_item is a substring
        of any item in the list. Defaults to False.

    :raise AssertionError: If the verified item is not found in the list.
    """

    if not message:
        message = f"'{verified_item}' not found in list: {actual_list}'"

    found = any(
        (str(verified_item).lower().strip() in str(item).lower().strip())
        if check_list_items
        else (str(item).lower().strip() in str(verified_item).lower().strip())
        for item in actual_list
    )

    assert found, message


# Checks if substring exists in list
def assert_partial_in_list(actual_list: List, wanted_item: str, message: str = None) -> None:
    """
    Asserts that a list contains at least one item that partially matches
    the provided 'wanted_item' string.

    :param actual_list: The list of strings to search within.
    :param wanted_item: The string to search for as a partial match within list items.
    :param message: (Optional) A custom error message to display on failure.
    """

    if message is None:
        message = f"'{wanted_item}' not found partially in any item of the list: {actual_list}'"

    assert any(str(wanted_item) in str(item) for item in actual_list), _print_assert_message(
        message=message,
        expected_result=f"'{wanted_item}' partially present in at least one list item",
        actual_result=f"List: {actual_list}",
    )


def assert_list_contains_all_elements(actual_list: List, wanted_list: str, message: str = None) -> None:
    """
    Asserts that all elements from 'wanted_list' are present in 'actual_list'.

    :param actual_list: The list to check for the presence of all elements.
    :param wanted_list: The list containing all the elements that should be present.
    :param message: (Optional) A custom error message to display on failure.
    """

    difference = set(actual_list).difference(set(wanted_list))
    difference_to_string = "".join(difference)
    if message is None:
        message = f"Those elements are missing: {difference_to_string}"

    for item in wanted_list:
        assert item in actual_list, _print_assert_message(
            message=message,
            expected_result=f"List containing '{item}'",
            actual_result=f"List: {actual_list}",
        )


def assert_all_in_list(actual_list: List, wanted_item: str, message: str = None) -> None:
    """
    Asserts that the provided 'wanted_item' string is present
    (as a substring) in all items of the 'actual_list'.

    :param actual_list: The list of strings to search within.
    :param wanted_item: The string to search for in all list items.
    :param message: (Optional) A custom error message to display on failure.
    """

    if message is None:
        message = f"'{wanted_item}' not found in all items of the list: {actual_list}'"

    assert all(str(wanted_item) in str(item) for item in actual_list), _print_assert_message(
        message=message,
        expected_result=f"'{wanted_item}' present in all list items",
        actual_result=f"List: {actual_list}",
    )


def assert_not_in_list(
    actual_list: List,
    unwanted_item: str,
    message: str = None,
    check_list_items: bool = False,
) -> None:
    """
    Asserts that the 'unwanted_item' is NOT present in the 'actual_list'.
    Handles two cases based on 'check_list_items':
    - If False (default): Checks if 'unwanted_item' is a substring of any list item.
    - If True: Checks if any item in 'actual_list' is a substring of 'unwanted_item'.

    :param actual_list: The list of strings to check.
    :param unwanted_item: The string that should not be present in the list.
    :param message: (Optional) A custom error message to display on failure.
    :param check_list_items: (bool) Determines the type of check to perform
                            (see function description).
    """
    if message is None:
        message = f"'{unwanted_item}' should not be found in the list: {actual_list}'"

    if not check_list_items:
        assert not any(str(unwanted_item).lower().strip() in str(item).lower().strip() for item in actual_list), (
            _print_assert_message(
                message=message,
                expected_result=f"'{unwanted_item}' not present in the list",
                actual_result=f"List: {actual_list}",
            )
        )
    else:
        assert not any(str(item).lower().strip() in str(unwanted_item).lower().strip() for item in actual_list), (
            _print_assert_message(
                message=message,
                expected_result=f"No item from the list should be a substring of '{unwanted_item}'",
                actual_result=f"List: {actual_list}",
            )
        )


def assert_in_dict(key: str, dictionary: dict, message: str = None, actual: str = None) -> None:
    """
    Asserts that a specific key is present in the given dictionary.

    :param key: The key to search for in the dictionary.
    :param dictionary: The dictionary to check for the key.
    :param message: (Optional) A custom error message to display on failure.
    """

    if message is None:
        message = f"Key '{key}' not found in dictionary. Found keys: {list(dictionary.keys())}"

    assert key in dictionary, _print_assert_message(
        message=message,
        expected_result=f"Key '{key}' to be present",
        actual_result=f"Dictionary: {dictionary}",
    )


def assert_keys_in_dict(keys: List, dictionary: dict, message: str = None) -> None:
    """
    Asserts that all keys in the provided 'keys' iterable are present
    in the given 'dictionary'.

    :param keys: An iterable (list, tuple, etc.) of keys to check for in the dictionary.
    :param dictionary: The dictionary to check for the presence of keys.
    :param message: (Optional) A custom error message to display on failure (used
                 if any key is not found).
    """

    for key in keys:
        if key not in dictionary:  # Check for missing key early
            if message is None:
                message = (
                    f"Key '{key}' not found in dictionary.\n"
                    f"Keys provided: {list(keys)}\n"
                    f"Keys found in dictionary: {list(dictionary.keys())}"
                )
            break  # No need to check other keys if one is missing

    assert all(key in dictionary for key in keys), _print_assert_message(
        message=message,
        expected_result=f"All keys ({list(keys)}) to be present",
        actual_result=f"Dictionary: {dictionary}",
    )


def assert_not_in_dict(key: str, dictionary: dict, message: str = None) -> None:
    """
    Asserts that a specific key is NOT present in the given dictionary.

    :param key: The key that should not be in the dictionary.
    :param dictionary: The dictionary to check.
    :param message: (Optional) A custom error message to display on failure.
    """

    if message is None:
        message = f"Key '{key}' unexpectedly found in dictionary.\nDictionary keys: {list(dictionary.keys())}"

    assert key not in dictionary, _print_assert_message(
        message=message,
        expected_result=f"Key '{key}' not to be present",
        actual_result=f"Dictionary: {dictionary}",
    )


# Asserts result is None
def assert_none(actual_result: str, message: str = None) -> None:
    if message is None:
        message = "Got '{0}' (actual response), expected None".format(actual_result)
    assert actual_result is None, _print_assert_message(
        message=message, expected_result="None", actual_result=actual_result
    )


# Asserts result is not None
def assert_not_none(actual_result: str, message: str = None) -> None:
    if message is None:
        message = f"Got '{actual_result}' (actual response), expected Not None"
    assert actual_result, _print_assert_message(
        message=message, expected_result="Not None", actual_result=actual_result
    )


# Asserts that result is True
def assert_true(actual_result: str | bool, message: str = None) -> None:
    if message is None:
        message = f"Got '{actual_result}' expected True."
    assert actual_result is True, _print_assert_message(
        message=message, expected_result="True", actual_result=actual_result
    )


# Asserts that result is False
def assert_false(actual_result: str | bool, message: str = None) -> None:
    if not message:
        message = f"Got '{actual_result}' expected False."
    assert actual_result is False, _print_assert_message(
        message=message, expected_result="False", actual_result=actual_result
    )


def assert_nested_keys(data: str, *keys: str, message: str = None) -> None:
    """Asserts that a sequence of nested keys exists in a dictionary.

    :param data (dict): The dictionary to check for nested keys.
    :param *keys: Variable length argument list of keys to check in order.
    :param message (str, optional): Custom error message if assertion fails.
                                  Defaults to a descriptive message.

    :raise: AssertionError: If any key in the sequence is not found in
                         the corresponding nested dictionary.
    """

    current_level = data
    key_path = ""

    for i, key in enumerate(keys):
        key_path += f"['{key}']"
        if not isinstance(current_level, dict) or key not in current_level:
            if message is None:
                message = (
                    f"Nested key not found: {key_path}\n"
                    f"Full path: dictionary{key_path}\n"
                    f"Data at current level: {current_level}"
                )
            raise AssertionError(
                _print_assert_message(
                    message=message,
                    expected_result=f"Key '{key}' to exist at path {key_path}",
                    actual_result=f"Key missing or invalid data type encountered at {key_path}",
                )
            )
        current_level = current_level[key]


def assert_greater_than(actual_result: str, lowest_limit: str, message: str = None) -> None:
    if message is None:
        message = "Expected a higher value."
    assert actual_result > lowest_limit, _print_assert_message(
        message=message,
        expected_result=f"Value greater than {lowest_limit}",
        actual_result=actual_result,
    )


def assert_greater_equals_than(actual_result: str, lowest_limit: str, message: str = None) -> None:
    if not message:
        message = "Expected a higher or an equal value."
    assert actual_result >= lowest_limit, _print_assert_message(
        message=message,
        expected_result=f"Value greater or equal to {lowest_limit}",
        actual_result=actual_result,
    )


def assert_list_empty(actual_list: str, message: str) -> None:
    assert_equals(
        actual_result=actual_list is not None and list(actual_list),
        expected_result=[],
        message=message,
    )


def assert_list_not_empty(actual_list: List, message: str) -> None:
    assert_not_equals(
        actual_result=actual_list is not None and list(actual_list),
        expected_result=[],
        message=message,
    )


def assert_string_empty(actual_result: str, message: str = None) -> None:
    if not message:
        message = f"Got '{actual_result}' (actual response), expected ''"
    assert actual_result == "", _print_assert_message(message=message, expected_result="", actual_result=actual_result)


def assert_string_non_empty(actual_result: str, message: str = None) -> None:
    if not message:
        message = "Got empty, expected non-empty"
    assert actual_result != "", _print_assert_message(
        message=message,
        expected_result="A non-empty string",
        actual_result=actual_result,
    )


def assert_raises_with_message(action: callable, expected_exception: Exception, message: str, *args, **kwargs) -> None:
    """
    Asserts that a specific exception with a substring in its message
    is raised when calling the given action.

    :param action (callable): The function or code block to execute.
    :param expected_exception (Exception): The expected exception type.
    :param message (str): The substring expected to be in the exception message.
    :param *args: Positional arguments to pass to the action.
    :param **kwargs: Keyword arguments to pass to the action.
    """
    try:
        action(*args, **kwargs)
        raise AssertionError(f"Expected exception {expected_exception.__name__} was not raised.")
    except expected_exception as e:
        error_message = str(e)
        assert message in error_message, f"Exception message '{error_message}' does not contain '{message}'."


def assert_len_equals(actual: str, expected: str, message: str = None) -> None:
    """
    Asserts that the length of the actual value is equal to the expected length.

    :param actual: The value whose length is being checked.
    :param expected: The expected length (can be an integer or another object with a length).
    :param message (str, optional): A custom error message to display on failure.
                                   Defaults to a descriptive message.
    """

    if message is None:
        message = f"Length mismatch!\nExpected length: {expected}\nActual length:   {len(actual)}"

    try:
        assert len(actual) == len(expected), _print_assert_message(
            message=message,
            expected_result=f"Length: {len(expected)}",
            actual_result=f"Length: {len(actual)}",
        )
    except TypeError as e:
        raise TypeError(f"Failed to get the length of actual/expected:\n{e}")


def assert_strings_equal(actual: str, expected: str, message: str = "") -> None:
    """
    Asserts that two strings are exactly equal.

    Parameters:
    :param actual: (str): The actual string value.
    :param expected: (str): The expected string value.
    :param message: (str, optional): Optional custom error message to display on failure.

    Raises:
        AssertionError: If the actual and expected strings are not equal.
    """
    assert actual == expected, message or f"Expected '{expected}', but got '{actual}'"
