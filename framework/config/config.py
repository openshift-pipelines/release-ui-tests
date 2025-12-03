import logging
import os

from framework.config.singleton import Singleton

logger = logging.getLogger(__name__)


class Config(object, metaclass=Singleton):
    """
    IMPORTANT! Please read this out before using Config object.
    Config Singleton object contains configurations for various instances required
    for tests to run.

    WARNING: Do not use Config object to set a constant value outside class
    or function definition, it could lead to misconfiguration.

    Bad:
    ```
    SOME_CONST = Config.some_value

    class SomeClass:
        def __init__(self):
            self.some_field = some_function(SOME_CONST)
    ```

    OK:
    ```
     class SomeClass:
        def __init__(self):
            self.some_field = some_function(Config.some_value)
    ```
    """

    def __init__(self) -> None:
        """
        Initializes the Config singleton instance by reading environment variables.
        Priority: 1. Environment Variable, 2. Defaults (or None)
        Reads CONSOLE_URL, CONSOLE_USERNAME, CONSOLE_PASSWORD, and APP_TIMEOUT from environment.
        Raises ValueError if any critical environment variables (CONSOLE_URL, CONSOLE_USERNAME,
        CONSOLE_PASSWORD) are missing.
        :return: None: Raises ValueError if required environment variables are missing.
        """
        # Priority: 1. Environment Variable, 2. Defaults (or None)
        self._base_url = os.getenv("CONSOLE_URL")
        self._username = os.getenv("CONSOLE_USERNAME")
        self._password = os.getenv("CONSOLE_PASSWORD")

        # Parse Timeout (Handle string to int conversion safely)
        timeout_env = os.getenv("APP_TIMEOUT", "90000")
        try:
            self._timeout_ms = int(timeout_env)
        except ValueError:
            self._timeout_ms = 90000

        # Fail fast if critical parameters are missing
        missing = []
        if not self._base_url:
            missing.append("CONSOLE_URL")
        if not self._username:
            missing.append("CONSOLE_USERNAME")
        if not self._password:
            missing.append("CONSOLE_PASSWORD")

        if missing:
            raise ValueError(f"CRITICAL: Missing required environment variables: {', '.join(missing)}")

    @property
    def base_url(self) -> str:
        """
        Gets the base URL for the application console.
        Value is read from CONSOLE_URL environment variable.
        :return: str: The base URL string for the application console.
        """
        return self._base_url

    @property
    def username(self) -> str:
        """
        Gets the username for login authentication.
        Value is read from CONSOLE_USERNAME environment variable.
        :return: str: The username string for authentication.
        """
        return self._username

    @property
    def password(self) -> str:
        """
        Gets the password for login authentication.
        Value is read from CONSOLE_PASSWORD environment variable.
        :return: str: The password string for authentication.
        """
        return self._password

    @property
    def timeout_ms(self) -> int:
        """
        Gets the timeout value in milliseconds for element waits and page operations.
        Value is read from APP_TIMEOUT environment variable, defaults to 90000 (90 seconds)
        if not set or if conversion fails.
        :return: int: The timeout value in milliseconds.
        """
        return self._timeout_ms
