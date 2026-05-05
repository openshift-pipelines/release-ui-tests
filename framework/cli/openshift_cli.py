"""
OpenShift CLI Wrapper.

Provides async wrapper methods for oc CLI commands used in test automation.
Handles project creation, deletion, and management for test isolation.
"""

import asyncio
import logging
import random
import re
import string
from typing import Optional

logger = logging.getLogger(__name__)


def derive_api_url_from_console_url(console_url: str) -> Optional[str]:
    """
    Derive OpenShift API URL from Console URL.

    Console URL format: https://console-openshift-console.apps.<cluster-domain>
    API URL format: https://api.<cluster-domain>:6443

    :param str console_url: Console URL (e.g., https://console-openshift-console.apps.example.com)
    :return: Optional[str]: Derived API URL or None if pattern doesn't match
    """
    # Extract cluster domain from console URL
    # Pattern: https://console-openshift-console.apps.<cluster-domain>
    match = re.search(r"https?://console-openshift-console\.apps\.(.+)", console_url)

    if match:
        cluster_domain = match.group(1)
        api_url = f"https://api.{cluster_domain}:6443"
        logger.info(f"Derived API URL from console URL: {api_url}")
        return api_url
    else:
        logger.warning(f"Could not derive API URL from console URL: {console_url}")
        return None


class OpenShiftCLI:
    """Wrapper for OpenShift CLI (oc) commands."""

    def __init__(self, api_url: Optional[str] = None, token: Optional[str] = None) -> None:
        """
        Initialize OpenShift CLI wrapper.

        :param Optional[str] api_url: OpenShift API URL (e.g., https://api.cluster.example.com:6443)
        :param Optional[str] token: OpenShift authentication token
        """
        self.api_url = api_url
        self.token = token
        self._logged_in = False

    async def _run_command(self, command: list[str], check: bool = True) -> tuple[int, str, str]:
        """
        Run oc command asynchronously.

        :param list[str] command: Command to run (e.g., ["oc", "whoami"])
        :param bool check: If True, raise exception on non-zero exit code
        :return: tuple[int, str, str]: (exit_code, stdout, stderr)
        :raises: RuntimeError if check=True and command fails
        """
        logger.debug(f"Running command: {' '.join(command)}")

        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        stdout_str = stdout.decode().strip()
        stderr_str = stderr.decode().strip()
        exit_code = process.returncode

        if exit_code != 0:
            logger.warning(f"Command failed with exit code {exit_code}: {' '.join(command)}")
            logger.warning(f"STDOUT: {stdout_str}")
            logger.warning(f"STDERR: {stderr_str}")

            if check:
                raise RuntimeError(f"Command failed: {' '.join(command)}\nSTDERR: {stderr_str}")

        return exit_code, stdout_str, stderr_str

    async def login(self, api_url: Optional[str] = None, token: Optional[str] = None) -> bool:
        """
        Login to OpenShift cluster using token.

        :param Optional[str] api_url: OpenShift API URL (overrides instance value)
        :param Optional[str] token: Authentication token (overrides instance value)
        :return: bool: True if login successful, False otherwise
        """
        url = api_url or self.api_url
        tkn = token or self.token

        if not url or not tkn:
            logger.error("API URL and token are required for login")
            return False

        try:
            command = ["oc", "login", url, "--token", tkn, "--insecure-skip-tls-verify=true"]
            exit_code, stdout, stderr = await self._run_command(command, check=True)
            self._logged_in = True
            logger.info(f"Successfully logged in to {url}")
            return True
        except RuntimeError as e:
            logger.error(f"Login failed: {e}")
            return False

    async def login_with_credentials(self, api_url: str, username: str, password: str) -> bool:
        """
        Login to OpenShift cluster using username and password.

        :param str api_url: OpenShift API URL (e.g., https://api.cluster.example.com:6443)
        :param str username: Username for authentication
        :param str password: Password for authentication
        :return: bool: True if login successful, False otherwise
        """
        if not api_url or not username or not password:
            logger.error("API URL, username, and password are required for login")
            return False

        try:
            command = [
                "oc",
                "login",
                api_url,
                "--username",
                username,
                "--password",
                password,
                "--insecure-skip-tls-verify=true",
            ]
            exit_code, stdout, stderr = await self._run_command(command, check=True)
            self._logged_in = True
            logger.info(f"Successfully logged in to {api_url} as {username}")
            return True
        except RuntimeError as e:
            logger.error(f"Login with credentials failed: {e}")
            return False

    async def is_logged_in(self) -> bool:
        """
        Check if currently logged into a cluster.

        :return: bool: True if logged in, False otherwise
        """
        try:
            exit_code, stdout, stderr = await self._run_command(["oc", "whoami"], check=False)
            return exit_code == 0
        except Exception as e:
            logger.error(f"Failed to check login status: {e}")
            return False

    async def create_project(self, name: str, display_name: Optional[str] = None) -> bool:
        """
        Create a new OpenShift project.

        :param str name: Project name (must be DNS-compatible)
        :param Optional[str] display_name: Human-readable display name
        :return: bool: True if project created successfully, False otherwise
        """
        try:
            command = ["oc", "new-project", name]
            if display_name:
                command.extend(["--display-name", display_name])

            exit_code, stdout, stderr = await self._run_command(command, check=True)
            logger.info(f"Created project: {name}")
            return True
        except RuntimeError as e:
            logger.error(f"Failed to create project {name}: {e}")
            return False

    async def delete_project(self, name: str, wait: bool = False) -> bool:
        """
        Delete an OpenShift project.

        :param str name: Project name to delete
        :param bool wait: If True, wait for project to be fully deleted
        :return: bool: True if deletion initiated successfully, False otherwise
        """
        try:
            command = ["oc", "delete", "project", name]
            if wait:
                command.append("--wait")

            exit_code, stdout, stderr = await self._run_command(command, check=True)
            logger.info(f"Deleted project: {name}")
            return True
        except RuntimeError as e:
            logger.error(f"Failed to delete project {name}: {e}")
            return False

    async def project_exists(self, name: str) -> bool:
        """
        Check if a project exists.

        :param str name: Project name to check
        :return: bool: True if project exists, False otherwise
        """
        try:
            command = ["oc", "get", "project", name, "--ignore-not-found"]
            exit_code, stdout, stderr = await self._run_command(command, check=False)

            # If stdout contains the project name, it exists
            return name in stdout
        except Exception as e:
            logger.error(f"Failed to check project existence {name}: {e}")
            return False

    async def switch_project(self, name: str) -> bool:
        """
        Switch to a different project context.

        :param str name: Project name to switch to
        :return: bool: True if switch successful, False otherwise
        """
        try:
            command = ["oc", "project", name]
            exit_code, stdout, stderr = await self._run_command(command, check=True)
            logger.info(f"Switched to project: {name}")
            return True
        except RuntimeError as e:
            logger.error(f"Failed to switch to project {name}: {e}")
            return False

    async def get_current_project(self) -> Optional[str]:
        """
        Get the current project name.

        :return: Optional[str]: Current project name or None if not in a project
        """
        try:
            command = ["oc", "project", "-q"]
            exit_code, stdout, stderr = await self._run_command(command, check=False)
            return stdout if exit_code == 0 else None
        except Exception as e:
            logger.error(f"Failed to get current project: {e}")
            return None

    def generate_random_project_name(self, prefix: str = "release-ui-test") -> str:
        """
        Generate a random project name for test isolation.

        :param str prefix: Prefix for the project name
        :return: str: Generated project name (e.g., "release-ui-test-a7k2m")
        """
        # Generate 5 random lowercase alphanumeric characters
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        return f"{prefix}-{suffix}"

    async def apply_yaml(self, yaml_content: str, namespace: Optional[str] = None) -> bool:
        """
        Apply YAML content to the cluster using oc apply.

        :param str yaml_content: YAML content to apply
        :param Optional[str] namespace: Namespace to apply the resource to (uses current if not specified)
        :return: bool: True if apply successful, False otherwise
        """
        import os
        import tempfile

        try:
            # Create a temporary file to hold the YAML content
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp_file:
                tmp_file.write(yaml_content)
                tmp_file_path = tmp_file.name

            # Build the oc apply command
            command = ["oc", "apply", "-f", tmp_file_path]
            if namespace:
                command.extend(["-n", namespace])

            # Execute the command
            exit_code, stdout, stderr = await self._run_command(command, check=True)
            logger.info("Successfully applied YAML content")
            logger.debug(f"STDOUT: {stdout}")

            return True
        except RuntimeError as e:
            logger.error(f"Failed to apply YAML: {e}")
            return False
        finally:
            # Clean up the temporary file
            if "tmp_file_path" in locals() and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
                logger.debug(f"Removed temporary file: {tmp_file_path}")
