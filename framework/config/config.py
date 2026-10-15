import logging
import os
from pathlib import Path

from dotenv import load_dotenv

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
        Priority: 1. Environment Variable, 2. .env file, 3. Defaults (or None)
        Loads .env file from project root if it exists, then reads CONSOLE_URL, CONSOLE_USERNAME,
        CONSOLE_PASSWORD, and APP_TIMEOUT from environment.
        Raises ValueError if any critical environment variables (CONSOLE_URL, CONSOLE_USERNAME,
        CONSOLE_PASSWORD) are missing.
        :return: None: Raises ValueError if required environment variables are missing.
        """
        # Load environment variables from .env file (if exists)
        # Find project root (where .env should be located)
        project_root = Path(__file__).parent.parent.parent
        dotenv_path = project_root / ".env"
        load_dotenv(dotenv_path=dotenv_path, override=False)  # Don't override existing env vars

        # Priority: 1. Environment Variable, 2. .env file, 3. Defaults (or None)
        self._base_url = os.getenv("CONSOLE_URL")
        self._username = os.getenv("CONSOLE_USERNAME")
        self._password = os.getenv("CONSOLE_PASSWORD")

        # Parse Timeout (Handle string to int conversion safely)
        timeout_env = os.getenv("APP_TIMEOUT", "90000")
        try:
            self._timeout_ms = int(timeout_env)
        except ValueError:
            self._timeout_ms = 90000

        # Authentication type: kube:admin, htpasswd, or direct
        self._auth_type = os.getenv("AUTH_TYPE", "kube:admin").lower()

        # OpenShift Pipelines operator configuration
        self._install_pipelines_operator = os.getenv("INSTALL_PIPELINES_OPERATOR", "true").lower() in (
            "true",
            "yes",
            "1",
            "on",
        )
        self._operator_environment = os.getenv("OPERATOR_ENVIRONMENT", "prod").lower()
        self._operator_version = os.getenv("OPERATOR_VERSION", "")
        self._channel = os.getenv("CHANNEL", "latest")
        self._konflux_index_image = os.getenv("KONFLUX_INDEX_IMAGE", "")
        self._nightly_override = os.getenv("NIGHTLY", "").strip().lower()

        if self._operator_environment in ("pre-stage", "stage"):
            self._catalog_source = os.getenv("CATALOG_SOURCE", "custom-operators")
        else:
            self._catalog_source = os.getenv("CATALOG_SOURCE", "redhat-operators")

        self._install_method = os.getenv("OSP_INSTALL_METHOD", "cli").lower()

        # Artifact capture settings
        self._capture_screenshots = os.getenv("CAPTURE_SCREENSHOTS", "false").lower() == "true"
        self._capture_recordings = os.getenv("CAPTURE_RECORDINGS", "false").lower() == "true"
        self._artifacts_dir = os.getenv("ARTIFACTS_DIR", "/tmp/test-artifacts")

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

    @property
    def capture_screenshots(self) -> bool:
        """
        Whether to capture screenshots on test failure.
        Value is read from CAPTURE_SCREENSHOTS environment variable, defaults to False.
        :return: bool: True if screenshot capture is enabled.
        """
        return self._capture_screenshots

    @property
    def capture_recordings(self) -> bool:
        """
        Whether to record video of browser sessions.
        Value is read from CAPTURE_RECORDINGS environment variable, defaults to False.
        :return: bool: True if video recording is enabled.
        """
        return self._capture_recordings

    @property
    def artifacts_dir(self) -> str:
        """
        Directory path where test artifacts (screenshots, recordings) are saved.
        Value is read from ARTIFACTS_DIR environment variable, defaults to /tmp/test-artifacts.
        :return: str: The artifacts directory path.
        """
        return self._artifacts_dir

    @property
    def install_pipelines_operator(self) -> bool:
        return self._install_pipelines_operator

    @property
    def operator_environment(self) -> str:
        return self._operator_environment

    @property
    def operator_version(self) -> str:
        return self._operator_version

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def catalog_source(self) -> str:
        return self._catalog_source

    @property
    def konflux_index_image(self) -> str:
        return self._konflux_index_image

    @property
    def nightly(self) -> bool:
        """Is this a nightly Konflux build?

        Nightly indexes carry the `:nightly` tag, and NIGHTLY=true forces it for an
        index that does not. Nightly installs take the channel head: OPERATOR_VERSION
        is a channel-ish value such as "5.0" there, so it must never be pinned.
        """
        if self._nightly_override in ("true", "yes", "1", "on"):
            return True
        return self._konflux_index_image.endswith(":nightly")

    @property
    def install_method(self) -> str:
        return self._install_method

    @property
    def osp_channel(self) -> str:
        return self._channel

    @property
    def auth_type(self) -> str:
        """
        Gets the authentication type used for OpenShift console login.
        Value is read from AUTH_TYPE environment variable, defaults to "kube:admin".
        Supported values are "kube:admin", "htpasswd", and "direct".
        :return: str: The authentication type string (lowercase).
        """
        return self._auth_type
