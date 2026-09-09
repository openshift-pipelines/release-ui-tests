"""Session-scoped fixture to ensure OpenShift Pipelines operator is installed via CLI."""

import asyncio
import logging
import os
import time

import pytest

from framework.cli.openshift_cli import OpenShiftCLI
from framework.config.config import Config

logger = logging.getLogger(__name__)

SUBSCRIPTION_YAML = """\
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-pipelines-operator
  namespace: openshift-operators
spec:
  channel: {channel}
  name: openshift-pipelines-operator-rh
  source: redhat-operators
  sourceNamespace: openshift-marketplace
"""

OSP_SETUP_TIMEOUT_SECONDS = int(os.getenv("OSP_SETUP_TIMEOUT", "600"))


def _remaining(deadline: float) -> float:
    return max(0, deadline - time.monotonic())


def _elapsed_str(start: float, deadline: float) -> str:
    elapsed = int(time.monotonic() - start)
    total = int(deadline - start)
    return f"{elapsed}s/{total}s"


async def _is_osp_installed(cli: OpenShiftCLI) -> bool:
    exit_code, stdout, _ = await cli._run_command(
        [
            "oc",
            "get",
            "csv",
            "-n",
            "openshift-operators",
            "-o",
            "jsonpath={.items[?(@.spec.displayName=='Red Hat OpenShift Pipelines')].status.phase}",
        ],
        check=False,
    )
    return exit_code == 0 and "Succeeded" in stdout


async def _wait_for_csv(cli: OpenShiftCLI, start: float, deadline: float, poll_interval: int = 15) -> bool:
    while _remaining(deadline) > 0:
        if await _is_osp_installed(cli):
            return True
        logger.info(
            "[OSP Setup] [2/5 Install] Waiting for CSV to reach Succeeded... (%s)",
            _elapsed_str(start, deadline),
        )
        await asyncio.sleep(min(poll_interval, _remaining(deadline)))
    return False


async def _wait_for_tektonconfig(cli: OpenShiftCLI, start: float, deadline: float, poll_interval: int = 15) -> bool:
    while _remaining(deadline) > 0:
        exit_code, stdout, _ = await cli._run_command(
            ["oc", "get", "tektonconfig", "config", "-o", 'jsonpath={.status.conditions[?(@.type=="Ready")].status}'],
            check=False,
        )
        if exit_code == 0 and "True" in stdout:
            return True
        logger.info(
            "[OSP Setup] [3/5 TektonConfig] Waiting for Ready=True... (%s)",
            _elapsed_str(start, deadline),
        )
        await asyncio.sleep(min(poll_interval, _remaining(deadline)))
    return False


async def _is_console_plugin_enabled(cli: OpenShiftCLI) -> bool:
    exit_code, stdout, _ = await cli._run_command(
        ["oc", "get", "console.operator.openshift.io", "cluster", "-o", "jsonpath={.spec.plugins}"],
        check=False,
    )
    return exit_code == 0 and "pipelines-console-plugin" in stdout


async def _enable_console_plugin(cli: OpenShiftCLI, start: float, deadline: float, poll_interval: int = 5) -> bool:
    if await _is_console_plugin_enabled(cli):
        logger.info("[OSP Setup] [4/5 Console Plugin] Already enabled, skipping.")
        return True

    while _remaining(deadline) > 0:
        exit_code, _, _ = await cli._run_command(
            ["oc", "get", "consoleplugin", "pipelines-console-plugin"],
            check=False,
        )
        if exit_code == 0:
            break
        logger.info(
            "[OSP Setup] [4/5 Console Plugin] Waiting for consoleplugin resource to be created... (%s)",
            _elapsed_str(start, deadline),
        )
        await asyncio.sleep(min(poll_interval, _remaining(deadline)))
    else:
        return False

    logger.info("[OSP Setup] [4/5 Console Plugin] Enabling pipelines-console-plugin...")
    exit_code, _, _ = await cli._run_command(
        [
            "oc",
            "patch",
            "console.operator.openshift.io",
            "cluster",
            "--type",
            "json",
            "-p",
            '[{"op":"add","path":"/spec/plugins/-","value":"pipelines-console-plugin"}]',
        ],
        check=False,
    )
    if exit_code != 0:
        await cli._run_command(
            [
                "oc",
                "patch",
                "console.operator.openshift.io",
                "cluster",
                "--type",
                "merge",
                "-p",
                '{"spec":{"plugins":["pipelines-console-plugin"]}}',
            ],
            check=True,
        )
    logger.info("[OSP Setup] [4/5 Console Plugin] Enabled successfully.")
    return True


async def _wait_for_deployment_rollout(
    cli: OpenShiftCLI,
    deployment: str,
    namespace: str,
    start: float,
    deadline: float,
    poll_interval: int = 10,
) -> bool:
    while _remaining(deadline) > 0:
        exit_code, _, _ = await cli._run_command(
            ["oc", "rollout", "status", f"deployment/{deployment}", "-n", namespace, f"--timeout={poll_interval}s"],
            check=False,
        )
        if exit_code == 0:
            return True
        logger.info(
            "[OSP Setup] [5/5 Pod Readiness] Waiting for %s/%s rollout... (%s)",
            namespace,
            deployment,
            _elapsed_str(start, deadline),
        )
    return False


async def _ensure_osp(cli: OpenShiftCLI, channel: str, timeout_seconds: int = OSP_SETUP_TIMEOUT_SECONDS) -> None:
    start = time.monotonic()
    deadline = start + timeout_seconds
    logger.info(
        "[OSP Setup] ===== Starting OpenShift Pipelines operator setup (timeout=%ds) =====",
        timeout_seconds,
    )

    # Step 1: Check if operator is already installed
    logger.info("[OSP Setup] [1/5 Check] Checking if operator is already installed...")
    if await _is_osp_installed(cli):
        logger.info("[OSP Setup] [1/5 Check] Operator already installed with CSV Succeeded.")
    else:
        # Step 2: Install operator
        logger.info("[OSP Setup] [2/5 Install] Operator not found, creating Subscription (channel=%s)...", channel)
        yaml_content = SUBSCRIPTION_YAML.format(channel=channel)
        success = await cli.apply_yaml(yaml_content)
        if not success:
            raise RuntimeError("Failed to apply OpenShift Pipelines Subscription YAML")
        logger.info("[OSP Setup] [2/5 Install] Subscription created, waiting for CSV...")
        if not await _wait_for_csv(cli, start, deadline):
            raise RuntimeError(
                f"OpenShift Pipelines CSV did not reach 'Succeeded' within global "
                f"timeout ({_elapsed_str(start, deadline)})"
            )
        logger.info("[OSP Setup] [2/5 Install] CSV reached Succeeded.")

    # Step 3: Wait for TektonConfig
    logger.info("[OSP Setup] [3/5 TektonConfig] Checking TektonConfig readiness...")
    if not await _wait_for_tektonconfig(cli, start, deadline):
        raise RuntimeError(
            f"TektonConfig did not reach Ready state within global timeout ({_elapsed_str(start, deadline)})"
        )
    logger.info("[OSP Setup] [3/5 TektonConfig] Ready.")

    # Step 4: Enable console plugin
    logger.info("[OSP Setup] [4/5 Console Plugin] Checking console plugin status...")
    if not await _enable_console_plugin(cli, start, deadline):
        raise RuntimeError(f"Console plugin was not enabled within global timeout ({_elapsed_str(start, deadline)})")

    # Step 5: Wait for console pods
    logger.info("[OSP Setup] [5/5 Pod Readiness] Checking console deployments...")

    logger.info("[OSP Setup] [5/5 Pod Readiness] Waiting for openshift-console/console...")
    if not await _wait_for_deployment_rollout(cli, "console", "openshift-console", start, deadline):
        raise RuntimeError(
            f"openshift-console deployment did not roll out within global timeout ({_elapsed_str(start, deadline)})"
        )
    logger.info("[OSP Setup] [5/5 Pod Readiness] openshift-console/console is ready.")

    logger.info("[OSP Setup] [5/5 Pod Readiness] Waiting for openshift-pipelines/pipelines-console-plugin...")
    if not await _wait_for_deployment_rollout(cli, "pipelines-console-plugin", "openshift-pipelines", start, deadline):
        raise RuntimeError(
            f"pipelines-console-plugin deployment did not roll out within global timeout"
            f" ({_elapsed_str(start, deadline)})"
        )
    logger.info("[OSP Setup] [5/5 Pod Readiness] openshift-pipelines/pipelines-console-plugin is ready.")

    total_elapsed = int(time.monotonic() - start)
    logger.info("[OSP Setup] ===== OpenShift Pipelines operator setup complete (%ds) =====", total_elapsed)


@pytest.fixture(scope="session")
def ensure_osp_installed(
    openshift_cli: OpenShiftCLI,
    config: Config,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    from framework.cli.openshift_cli import derive_api_url_from_console_url
    from framework.fixtures.async_bridge import run_async

    async def _setup() -> None:
        logger.info("[OSP Setup] [0/5 Login] Checking CLI authentication...")

        # 1. Check if already logged in via existing KUBECONFIG (CI/Prow)
        if await openshift_cli.is_logged_in():
            logger.info("[OSP Setup] [0/5 Login] Already authenticated via existing KUBECONFIG.")
        else:
            # 2. Try API_URL env var if set (explicit override)
            api_url = os.getenv("API_URL")
            if api_url:
                logger.info("[OSP Setup] [0/5 Login] Using API_URL env var: %s", api_url)
            else:
                # 3. Derive from CONSOLE_URL
                api_url = derive_api_url_from_console_url(config.base_url)
                assert api_url, f"Could not derive API URL from {config.base_url}"
                logger.info("[OSP Setup] [0/5 Login] Derived API URL: %s", api_url)

            assert await openshift_cli.login_with_credentials(
                api_url=api_url, username=config.username, password=config.password
            ), f"CLI login failed against {api_url}"
            logger.info("[OSP Setup] [0/5 Login] Logged in successfully.")

        await _ensure_osp(openshift_cli, config.osp_channel)

    run_async(playwright_event_loop, _setup())
