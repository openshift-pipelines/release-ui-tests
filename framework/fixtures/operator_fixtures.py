"""Session-scoped fixture to ensure OpenShift Pipelines operator is installed."""

import asyncio
import logging
import os
import time

import pytest
from playwright.async_api import Browser, Page

from framework.cli.openshift_cli import OpenShiftCLI
from framework.config.config import Config

logger = logging.getLogger(__name__)

OSP_SETUP_TIMEOUT_SECONDS = int(os.getenv("OSP_SETUP_TIMEOUT", "600"))

CATALOG_SOURCE_YAML = """\
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: {name}
  namespace: openshift-marketplace
spec:
  sourceType: grpc
  image: {index_image}
  displayName: {name}
  updateStrategy:
    registryPoll:
      interval: 30m
"""

IDMS_YAML = """\
apiVersion: config.openshift.io/v1
kind: ImageDigestMirrorSet
metadata:
  name: pipelines-mirror
spec:
  imageDigestMirrors:
  - source: registry.stage.redhat.io/openshift-pipelines
    mirrors:
    - quay.io/openshift-pipeline
  - source: registry.redhat.io/openshift-pipelines
    mirrors:
    - quay.io/openshift-pipeline
"""

SUBSCRIPTION_YAML = """\
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-pipelines-operator-rh
  namespace: openshift-operators
spec:
  channel: {channel}
  installPlanApproval: {install_plan_approval}
  name: openshift-pipelines-operator-rh
  source: {catalog_source}
  sourceNamespace: openshift-marketplace
{starting_csv_line}"""


def _remaining(deadline: float) -> float:
    return max(0, deadline - time.monotonic())


def _elapsed_str(start: float, deadline: float) -> str:
    elapsed = int(time.monotonic() - start)
    total = int(deadline - start)
    return f"{elapsed}s/{total}s"


def _is_nightly(index_image: str) -> bool:
    return index_image.endswith(":nightly")


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


async def _apply_idms(cli: OpenShiftCLI) -> bool:
    logger.info("[OSP Setup] Applying ImageDigestMirrorSet for nightly registry mirrors...")
    success = await cli.apply_yaml(IDMS_YAML)
    if success:
        exit_code, _, _ = await cli._run_command(
            ["oc", "get", "imagedigestmirrorset", "pipelines-mirror", "-o", "name"],
            check=False,
        )
        if exit_code == 0:
            logger.info("[OSP Setup] ImageDigestMirrorSet applied successfully.")
            return True
    logger.error("[OSP Setup] Failed to apply ImageDigestMirrorSet.")
    return False


async def _create_catalog_source(
    cli: OpenShiftCLI,
    catalog_source: str,
    index_image: str,
    start: float,
    deadline: float,
) -> bool:
    logger.info(
        "[OSP Setup] Creating CatalogSource '%s' from index image: %s",
        catalog_source,
        index_image,
    )
    yaml_content = CATALOG_SOURCE_YAML.format(name=catalog_source, index_image=index_image)
    success = await cli.apply_yaml(yaml_content)
    if not success:
        logger.error("[OSP Setup] Failed to apply CatalogSource YAML.")
        return False

    logger.info("[OSP Setup] Waiting for CatalogSource pod to be ready...")
    await asyncio.sleep(10)

    while _remaining(deadline) > 0:
        exit_code, stdout, _ = await cli._run_command(
            [
                "oc",
                "get",
                "catalogsource",
                catalog_source,
                "-n",
                "openshift-marketplace",
                "-o",
                "jsonpath={.status.connectionState.lastObservedState}",
            ],
            check=False,
        )
        if exit_code == 0 and stdout.strip() == "READY":
            logger.info("[OSP Setup] CatalogSource '%s' is READY.", catalog_source)
            return True
        logger.info(
            "[OSP Setup] CatalogSource '%s' state=%s, waiting... (%s)",
            catalog_source,
            stdout.strip() if stdout else "unknown",
            _elapsed_str(start, deadline),
        )
        await asyncio.sleep(min(15, _remaining(deadline)))

    logger.error("[OSP Setup] CatalogSource '%s' did not reach READY state.", catalog_source)
    return False


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


async def _approve_installplan(cli: OpenShiftCLI, start: float, deadline: float) -> bool:
    """Approve Manual InstallPlans and wait for CSV Succeeded."""
    logger.info("[OSP Setup] [2/5 Install] Waiting for InstallPlan (Manual approval)...")
    while _remaining(deadline) > 0:
        # Check if CSV is already Succeeded
        exit_code, installed_csv, _ = await cli._run_command(
            [
                "oc",
                "get",
                "subscription",
                "openshift-pipelines-operator-rh",
                "-n",
                "openshift-operators",
                "-o",
                "jsonpath={.status.installedCSV}",
            ],
            check=False,
        )
        if exit_code == 0 and installed_csv:
            phase_code, phase, _ = await cli._run_command(
                [
                    "oc",
                    "get",
                    f"csv/{installed_csv}",
                    "-n",
                    "openshift-operators",
                    "-o",
                    "jsonpath={.status.phase}",
                ],
                check=False,
            )
            if phase_code == 0 and phase == "Succeeded":
                logger.info("[OSP Setup] [2/5 Install] CSV %s reached Succeeded.", installed_csv)
                return True

        # Find and approve unapproved InstallPlans
        exit_code, ip_output, _ = await cli._run_command(
            [
                "oc",
                "get",
                "installplan",
                "-n",
                "openshift-operators",
                "-o",
                "jsonpath={range .items[*]}{.metadata.name}|{.spec.approved}|"
                '{.spec.clusterServiceVersionNames[*]}{"\\n"}{end}',
            ],
            check=False,
        )
        if exit_code == 0 and ip_output:
            for line in ip_output.strip().split("\n"):
                parts = line.split("|")
                if len(parts) >= 3:
                    ip_name, approved, csvs = parts[0], parts[1], parts[2]
                    if "openshift-pipelines-operator-rh" in csvs and approved != "true":
                        logger.info("[OSP Setup] [2/5 Install] Approving InstallPlan %s", ip_name)
                        await cli._run_command(
                            [
                                "oc",
                                "patch",
                                f"installplan/{ip_name}",
                                "-n",
                                "openshift-operators",
                                "--type",
                                "merge",
                                "-p",
                                '{"spec":{"approved":true}}',
                            ],
                            check=False,
                        )

        logger.info(
            "[OSP Setup] [2/5 Install] Waiting for operator CSV... (%s)",
            _elapsed_str(start, deadline),
        )
        await asyncio.sleep(min(10, _remaining(deadline)))
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


async def _prepare_non_prod_catalog(
    cli: OpenShiftCLI,
    env: str,
    catalog_source: str,
    index_image: str,
    nightly: bool,
    start: float,
    deadline: float,
) -> None:
    if env not in ("pre-stage", "stage"):
        return
    if not index_image:
        raise RuntimeError(
            f"KONFLUX_INDEX_IMAGE is required when OPERATOR_ENVIRONMENT={env}. Set it to the quay.io index image URL."
        )
    if nightly:
        if not await _apply_idms(cli):
            raise RuntimeError("Failed to apply ImageDigestMirrorSet for nightly builds")
        await asyncio.sleep(5)
    if not await _create_catalog_source(cli, catalog_source, index_image, start, deadline):
        raise RuntimeError(
            f"CatalogSource '{catalog_source}' did not reach READY within timeout ({_elapsed_str(start, deadline)})"
        )


async def _install_operator(
    cli: OpenShiftCLI,
    channel: str,
    catalog_source: str,
    operator_version: str,
    nightly: bool,
    start: float,
    deadline: float,
) -> None:
    starting_csv_line = ""
    install_plan_approval = "Automatic"
    if operator_version and not nightly:
        csv_name = f"openshift-pipelines-operator-rh.v{operator_version}"
        starting_csv_line = f"  startingCSV: {csv_name}"
        install_plan_approval = "Manual"
        logger.info(
            "[OSP Setup] [2/5 Install] Pinning startingCSV=%s on %s/%s",
            csv_name,
            catalog_source,
            channel,
        )
    elif nightly:
        install_plan_approval = "Manual"
        logger.info(
            "[OSP Setup] [2/5 Install] Nightly channel-head install on %s/%s (no startingCSV pin)",
            catalog_source,
            channel,
        )

    logger.info(
        "[OSP Setup] [2/5 Install] Creating Subscription (channel=%s, source=%s, approval=%s)...",
        channel,
        catalog_source,
        install_plan_approval,
    )
    yaml_content = SUBSCRIPTION_YAML.format(
        channel=channel,
        catalog_source=catalog_source,
        install_plan_approval=install_plan_approval,
        starting_csv_line=starting_csv_line,
    )
    success = await cli.apply_yaml(yaml_content)
    if not success:
        raise RuntimeError("Failed to apply OpenShift Pipelines Subscription YAML")
    logger.info("[OSP Setup] [2/5 Install] Subscription created, waiting for CSV...")

    if install_plan_approval == "Manual":
        if not await _approve_installplan(cli, start, deadline):
            raise RuntimeError(f"Operator CSV did not reach Succeeded within timeout ({_elapsed_str(start, deadline)})")
    else:
        if not await _wait_for_csv(cli, start, deadline):
            raise RuntimeError(f"Operator CSV did not reach Succeeded within timeout ({_elapsed_str(start, deadline)})")
    logger.info("[OSP Setup] [2/5 Install] CSV reached Succeeded.")


async def _validate_post_install(cli: OpenShiftCLI, start: float, deadline: float) -> None:
    logger.info("[OSP Setup] [3/5 TektonConfig] Checking TektonConfig readiness...")
    if not await _wait_for_tektonconfig(cli, start, deadline):
        raise RuntimeError(f"TektonConfig did not reach Ready state within timeout ({_elapsed_str(start, deadline)})")
    logger.info("[OSP Setup] [3/5 TektonConfig] Ready.")

    logger.info("[OSP Setup] [4/5 Console Plugin] Checking console plugin status...")
    if not await _enable_console_plugin(cli, start, deadline):
        raise RuntimeError(f"Console plugin was not enabled within timeout ({_elapsed_str(start, deadline)})")

    logger.info("[OSP Setup] [5/5 Pod Readiness] Checking console deployments...")
    logger.info("[OSP Setup] [5/5 Pod Readiness] Waiting for openshift-console/console...")
    if not await _wait_for_deployment_rollout(cli, "console", "openshift-console", start, deadline):
        raise RuntimeError(
            f"openshift-console deployment did not roll out within timeout ({_elapsed_str(start, deadline)})"
        )
    logger.info("[OSP Setup] [5/5 Pod Readiness] openshift-console/console is ready.")

    logger.info("[OSP Setup] [5/5 Pod Readiness] Waiting for openshift-pipelines/pipelines-console-plugin...")
    if not await _wait_for_deployment_rollout(cli, "pipelines-console-plugin", "openshift-pipelines", start, deadline):
        raise RuntimeError(
            f"pipelines-console-plugin deployment did not roll out within timeout ({_elapsed_str(start, deadline)})"
        )
    logger.info("[OSP Setup] [5/5 Pod Readiness] openshift-pipelines/pipelines-console-plugin is ready.")


async def _install_operator_via_ui(
    ui_page: Page,
    cli: OpenShiftCLI,
    config: Config,
    start: float,
    deadline: float,
) -> None:
    from framework.ui_components.operators.operator_install_page import OperatorInstallPage

    nightly = config.nightly
    # Nightly installs the channel head; OPERATOR_VERSION is channel-ish there ("5.0")
    # and must not be pinned.
    version = None if nightly else (config.operator_version or None)
    logger.info(
        "[OSP Setup] [2/5 Install] Installing operator via UI (nightly=%s, version=%s)...",
        nightly,
        version or "<channel head>",
    )
    install_page = OperatorInstallPage(ui_page, config)
    success = await install_page.install_operator(
        catalog_source=config.catalog_source,
        channel=config.channel,
        version=version,
        nightly=nightly,
    )
    if not success:
        raise RuntimeError("UI-based operator install failed")

    # The UI selects Automatic approval, so OLM creates the CSV without an InstallPlan
    # approval step (unlike the CLI path, which uses Manual).
    logger.info("[OSP Setup] [2/5 Install] UI install triggered, waiting for CSV via CLI...")
    if not await _wait_for_csv(cli, start, deadline):
        raise RuntimeError(f"Operator CSV did not reach Succeeded within timeout ({_elapsed_str(start, deadline)})")
    logger.info("[OSP Setup] [2/5 Install] CSV reached Succeeded.")


async def _ensure_osp(
    cli: OpenShiftCLI,
    config: Config,
    timeout_seconds: int = OSP_SETUP_TIMEOUT_SECONDS,
    ui_page: Page | None = None,
) -> None:
    start = time.monotonic()
    deadline = start + timeout_seconds

    env = config.operator_environment
    channel = config.channel
    catalog_source = config.catalog_source
    index_image = config.konflux_index_image
    operator_version = config.operator_version
    nightly = _is_nightly(index_image) if index_image else False

    logger.info("[OSP Setup] ===== Starting OpenShift Pipelines operator setup (timeout=%ds) =====", timeout_seconds)
    logger.info(
        "[OSP Setup] Config: environment=%s channel=%s catalog_source=%s version=%s index_image=%s nightly=%s",
        env,
        channel,
        catalog_source,
        operator_version,
        index_image or "<none>",
        nightly,
    )

    await _prepare_non_prod_catalog(cli, env, catalog_source, index_image, nightly, start, deadline)

    logger.info("[OSP Setup] [1/5 Check] Checking if operator is already installed...")
    if await _is_osp_installed(cli):
        logger.info("[OSP Setup] [1/5 Check] Operator already installed with CSV Succeeded.")
    elif ui_page:
        # The Software Catalog panel exposes a version selector, so pinning no longer
        # forces a fall back to the CLI path.
        await _install_operator_via_ui(ui_page, cli, config, start, deadline)
    else:
        await _install_operator(cli, channel, catalog_source, operator_version, nightly, start, deadline)

    await _validate_post_install(cli, start, deadline)

    total_elapsed = int(time.monotonic() - start)
    logger.info("[OSP Setup] ===== OpenShift Pipelines operator setup complete (%ds) =====", total_elapsed)


@pytest.fixture(scope="session")
def ensure_osp_installed(
    openshift_cli: OpenShiftCLI,
    config: Config,
    browser: Browser,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    from framework.cli.openshift_cli import derive_api_url_from_console_url
    from framework.fixtures.async_bridge import run_async

    if not config.install_pipelines_operator:
        logger.info("[OSP Setup] INSTALL_PIPELINES_OPERATOR is not true, skipping operator installation.")
        return

    async def _setup() -> None:
        logger.info("[OSP Setup] [0/5 Login] Checking CLI authentication...")

        if await openshift_cli.is_logged_in():
            logger.info("[OSP Setup] [0/5 Login] Already authenticated via existing KUBECONFIG.")
        else:
            api_url = os.getenv("API_URL")
            if api_url:
                logger.info("[OSP Setup] [0/5 Login] Using API_URL env var: %s", api_url)
            else:
                api_url = derive_api_url_from_console_url(config.base_url)
                assert api_url, f"Could not derive API URL from {config.base_url}"
                logger.info("[OSP Setup] [0/5 Login] Derived API URL: %s", api_url)

            assert await openshift_cli.login_with_credentials(
                api_url=api_url, username=config.username, password=config.password
            ), f"CLI login failed against {api_url}"
            logger.info("[OSP Setup] [0/5 Login] Logged in successfully.")

        ui_page: Page | None = None
        context = None
        if config.install_method == "ui":
            logger.info("[OSP Setup] Install method=ui, creating browser session for OperatorHub...")
            context = await browser.new_context(
                ignore_https_errors=True,
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )
            ui_page = await context.new_page()
            ui_page.set_default_timeout(config.timeout_ms)
            from framework.ui_components.commons.login_page import LoginPage

            login = LoginPage(ui_page, config)
            await login.goto()
            await login.perform_login(config.auth_type)
            await ui_page.wait_for_load_state("networkidle")
            logger.info("[OSP Setup] Browser session ready.")

        try:
            await _ensure_osp(openshift_cli, config, ui_page=ui_page)
        finally:
            if context:
                await context.close()

    run_async(playwright_event_loop, _setup())
