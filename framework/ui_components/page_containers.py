"""
Page container classes that organize pages hierarchically to match UI navigation structure.

These containers follow the Composite Pattern, grouping related pages together based on
the actual navigation hierarchy in the OpenShift Console.

Usage:
    pages = setup_pages(playwright_page, config)

    # Navigate through hierarchy
    await pages.pipelines.list.click_create_button()
    await pages.pipelines.pipeline.details.verify_on_page()
    await pages.tasks.task.yaml.click_save()
"""

from playwright.async_api import Page

from framework.config.config import Config
from framework.ui_components.pipelineruns.create_pipeline_run_page import CreatePipelineRunPage
from framework.ui_components.pipelineruns.pipeline_runs_page import PipelineRunsPage
from framework.ui_components.pipelineruns.pipelinerun_details_page import PipelineRunDetailsPage
from framework.ui_components.pipelineruns.pipelinerun_logs_page import PipelineRunLogsPage
from framework.ui_components.pipelineruns.pipelinerun_parameters_page import PipelineRunParametersPage
from framework.ui_components.pipelineruns.pipelinerun_taskruns_page import PipelineRunTaskRunsPage
from framework.ui_components.pipelineruns.pipelinerun_yaml_page import PipelineRunYamlPage
from framework.ui_components.pipelines.pipeline_builder_page import PipelineBuilderPage
from framework.ui_components.pipelines.pipeline_details_page import PipelineDetailsPage
from framework.ui_components.pipelines.pipeline_parameters_page import PipelineParametersPage
from framework.ui_components.pipelines.pipeline_pipelineruns_tab_page import PipelinePipelineRunsTabPage
from framework.ui_components.pipelines.pipeline_yaml_page import PipelineYamlPage
from framework.ui_components.pipelines.pipelines_overview_page import PipelinesOverViewPage
from framework.ui_components.pipelines.pipelines_page import PipelinesPage
from framework.ui_components.repositories_page import RepositoriesPage
from framework.ui_components.taskruns.create_taskrun_page import CreateTaskRunPage
from framework.ui_components.taskruns.task_runs_page import TaskRunsPage
from framework.ui_components.taskruns.taskrun_details_page import TaskRunDetailsPage
from framework.ui_components.taskruns.taskrun_events_page import TaskRunEventsPage
from framework.ui_components.taskruns.taskrun_logs_page import TaskRunLogsPage
from framework.ui_components.taskruns.taskrun_yaml_page import TaskRunYamlPage
from framework.ui_components.tasks.create_task_page import CreateTaskPage
from framework.ui_components.tasks.task_details_page import TaskDetailsPage
from framework.ui_components.tasks.task_yaml_page import TaskYamlPage
from framework.ui_components.tasks.tasks_page import TasksPage
from framework.ui_components.triggers.create_clustertriggerbinding_page import CreateClusterTriggerBindingPage
from framework.ui_components.triggers.create_eventlistener_page import CreateEventListenerPage
from framework.ui_components.triggers.create_triggerbinding_page import CreateTriggerBindingPage
from framework.ui_components.triggers.create_triggertemplate_page import CreateTriggerTemplatePage
from framework.ui_components.triggers.eventlistener_details_page import EventListenerDetailsPage
from framework.ui_components.triggers.eventlistener_yaml_page import EventListenerYamlPage
from framework.ui_components.triggers.triggerbinding_details_page import TriggerBindingDetailsPage
from framework.ui_components.triggers.triggerbinding_yaml_page import TriggerBindingYamlPage
from framework.ui_components.triggers.triggers_page import TriggersPage
from framework.ui_components.triggers.triggertemplate_details_page import TriggerTemplateDetailsPage
from framework.ui_components.triggers.triggertemplate_yaml_page import TriggerTemplateYamlPage


class PipelinePages:
    """
    Container for Pipeline detail pages (specific pipeline resource).

    Navigation: Pipelines → Click pipeline name → Details/YAML/Parameters/PipelineRuns tabs
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.details = PipelineDetailsPage(page, config)
        self.yaml = PipelineYamlPage(page, config)
        self.parameters = PipelineParametersPage(page, config)
        self.runs_tab = PipelinePipelineRunsTabPage(page, config)


class PipelineRunPages:
    """
    Container for PipelineRun detail pages (specific pipelinerun resource).

    Navigation: Pipelines → PipelineRuns tab → Click run name → Details/YAML/Parameters/Logs/TaskRuns tabs
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.details = PipelineRunDetailsPage(page, config)
        self.yaml = PipelineRunYamlPage(page, config)
        self.parameters = PipelineRunParametersPage(page, config)
        self.logs = PipelineRunLogsPage(page, config)
        self.task_runs = PipelineRunTaskRunsPage(page, config)


class PipelinesPages:
    """
    Container for all pipeline-related pages.

    Hierarchy:
    - overview: Pipelines overview dashboard
    - list: Pipelines list (Pipelines tab)
    - runs: PipelineRuns list (PipelineRuns tab)
    - repositories: Repositories list
    - builder: Pipeline builder/editor
    - pipeline: Container for pipeline detail pages
    - pipelinerun: Container for pipelinerun detail pages
    - create_run: Create new PipelineRun page
    """

    def __init__(self, page: Page, config: Config) -> None:
        # List/Overview pages
        self.overview = PipelinesOverViewPage(page, config)
        self.list = PipelinesPage(page, config)
        self.runs = PipelineRunsPage(page, config)
        self.repositories = RepositoriesPage(page, config)

        # Pipeline builder
        self.builder = PipelineBuilderPage(page, config)

        # Detail page containers
        self.pipeline = PipelinePages(page, config)
        self.pipelinerun = PipelineRunPages(page, config)

        # Create pages
        self.create_run = CreatePipelineRunPage(page, config)


class TaskPages:
    """
    Container for Task detail pages (specific task resource).

    Navigation: Tasks → Click task name → Details/YAML tabs
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.details = TaskDetailsPage(page, config)
        self.yaml = TaskYamlPage(page, config)


class TaskRunPages:
    """
    Container for TaskRun detail pages (specific taskrun resource).

    Navigation: Tasks → TaskRuns tab → Click taskrun name → Details/YAML/Logs/Events tabs
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.details = TaskRunDetailsPage(page, config)
        self.yaml = TaskRunYamlPage(page, config)
        self.logs = TaskRunLogsPage(page, config)
        self.events = TaskRunEventsPage(page, config)


class TasksPages:
    """
    Container for all task-related pages.

    Hierarchy:
    - list: Tasks list (Tasks tab)
    - runs: TaskRuns list (TaskRuns tab)
    - task: Container for task detail pages
    - taskrun: Container for taskrun detail pages
    - create: Create new Task page
    - create_run: Create new TaskRun page
    """

    def __init__(self, page: Page, config: Config) -> None:
        # List pages
        self.list = TasksPage(page, config)
        self.runs = TaskRunsPage(page, config)

        # Detail page containers
        self.task = TaskPages(page, config)
        self.taskrun = TaskRunPages(page, config)

        # Create pages
        self.create = CreateTaskPage(page, config)
        self.create_run = CreateTaskRunPage(page, config)


class EventListenerPages:
    """
    Container for EventListener detail pages.

    Navigation: Triggers → EventListeners tab → Click name → Details/YAML tabs
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.details = EventListenerDetailsPage(page, config)
        self.yaml = EventListenerYamlPage(page, config)


class TriggerTemplatePages:
    """
    Container for TriggerTemplate detail pages.

    Navigation: Triggers → TriggerTemplates tab → Click name → Details/YAML tabs
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.details = TriggerTemplateDetailsPage(page, config)
        self.yaml = TriggerTemplateYamlPage(page, config)


class TriggerBindingPages:
    """
    Container for TriggerBinding detail pages.

    Navigation: Triggers → TriggerBindings tab → Click name → Details/YAML tabs
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.details = TriggerBindingDetailsPage(page, config)
        self.yaml = TriggerBindingYamlPage(page, config)


class TriggerCreatePages:
    """
    Container for Trigger resource creation pages.

    Navigation: Triggers → Create button → Select resource type
    """

    def __init__(self, page: Page, config: Config) -> None:
        self.eventlistener = CreateEventListenerPage(page, config)
        self.triggertemplate = CreateTriggerTemplatePage(page, config)
        self.triggerbinding = CreateTriggerBindingPage(page, config)
        self.clustertriggerbinding = CreateClusterTriggerBindingPage(page, config)


class TriggersPages:
    """
    Container for all trigger-related pages.

    Hierarchy:
    - list: Main Triggers page with tabs
    - eventlistener: Container for EventListener detail pages
    - triggertemplate: Container for TriggerTemplate detail pages
    - triggerbinding: Container for TriggerBinding detail pages
    - create: Container for all trigger creation pages
    """

    def __init__(self, page: Page, config: Config) -> None:
        # List page (with tabs for different trigger resources)
        self.list = TriggersPage(page, config)

        # Detail page containers
        self.eventlistener = EventListenerPages(page, config)
        self.triggertemplate = TriggerTemplatePages(page, config)
        self.triggerbinding = TriggerBindingPages(page, config)

        # Create pages container
        self.create = TriggerCreatePages(page, config)
