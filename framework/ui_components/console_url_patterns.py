"""
Compiled regex patterns for OpenShift console URLs.

These are passed to Playwright ``Page.wait_for_url`` via ``BasePage._verify_page_regex``.
Each pattern may match as a substring of the full URL (query strings and hashes allowed).
"""

import re

PIPELINES_NS_URL = re.compile(r"pipelines/(?:all-namespaces|ns/[^/?#]+)")

PIPELINES_OVERVIEW_URL = re.compile(r"pipelines-overview/(?:all-namespaces|ns/[^/?#]+)")

PIPELINE_BUILDER_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Pipeline/(?:~new|[^/?#]+)/builder")

CREATE_PIPELINE_RUN_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~PipelineRun/~new")

PIPELINE_DETAILS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Pipeline/[^/?#]+$")

PIPELINE_YAML_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Pipeline/[^/?#]+/yaml")

PIPELINE_PARAMETERS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Pipeline/[^/?#]+/parameters")

PIPELINE_PIPELINERUNS_TAB_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Pipeline/[^/?#]+/Runs")

PIPELINERUN_DETAILS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~PipelineRun/[^/?#]+$")

PIPELINERUN_YAML_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~PipelineRun/[^/?#]+/yaml")

PIPELINERUN_PARAMETERS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~PipelineRun/[^/?#]+/parameters")

PIPELINERUN_LOGS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~PipelineRun/[^/?#]+/logs")

PIPELINERUN_TASKRUNS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~PipelineRun/[^/?#]+/task-runs")

TASKS_URL = re.compile(r"tasks/(?:all-namespaces|ns/[^/?#]+)")

TASK_DETAILS_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Task/[^/?#]+$")

TASK_YAML_URL = re.compile(r"k8s/ns/[^/?#]+/tekton\.dev~v1~Task/[^/?#]+/yaml")

TRIGGERS_URL = re.compile(r"triggers/(?:all-namespaces|ns/[^/?#]+)")

EVENTLISTENER_DETAILS_URL = re.compile(r"k8s/ns/[^/?#]+/triggers\.tekton\.dev~v1beta1~EventListener/[^/?#]+$")

EVENTLISTENER_YAML_URL = re.compile(r"k8s/ns/[^/?#]+/triggers\.tekton\.dev~v1beta1~EventListener/[^/?#]+/yaml")

TRIGGERTEMPLATE_DETAILS_URL = re.compile(r"k8s/ns/[^/?#]+/triggers\.tekton\.dev~v1beta1~TriggerTemplate/[^/?#]+$")

TRIGGERTEMPLATE_YAML_URL = re.compile(r"k8s/ns/[^/?#]+/triggers\.tekton\.dev~v1beta1~TriggerTemplate/[^/?#]+/yaml")

TRIGGERBINDING_DETAILS_URL = re.compile(r"k8s/ns/[^/?#]+/triggers\.tekton\.dev~v1beta1~TriggerBinding/[^/?#]+$")

TRIGGERBINDING_YAML_URL = re.compile(r"k8s/ns/[^/?#]+/triggers\.tekton\.dev~v1beta1~TriggerBinding/[^/?#]+/yaml")
