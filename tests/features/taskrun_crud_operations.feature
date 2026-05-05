Feature: TaskRun CRUD Operations

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Tasks page
    And user switches to current project

  @smoke @sanity
  Scenario Outline: Create TaskRun and verify redirect to details page
    When the user creates a task via cli from YAML file "<task_yaml_file>"
    And the user creates a taskrun from YAML file "<yaml_file>"
    Then validate user is redirected to taskrun details page for taskrun "<taskrun_name>"
    And the taskrun details page should display the taskrun name as "<taskrun_name>"

    Examples:
      | task_yaml_file   | yaml_file            | taskrun_name      |
      | simple_task.yaml | simple_taskrun.yaml  | simple-taskrun-   |

  @smoke @sanity
  Scenario Outline: Verify TaskRun appears in TaskRuns list
    When the user navigates to TaskRuns tab
    Then the taskrun "<taskrun_name>" should appear in the taskruns list

    Examples:
      | taskrun_name      |
      | simple-taskrun-   |

  @smoke @sanity
  Scenario Outline: Verify TaskRun is executed successfully
    When the user navigates to TaskRuns tab
    Then the taskrun "<taskrun_name>" is executed with status "<taskrun_status>"

    Examples:
      | taskrun_name      | taskrun_status |
      | simple-taskrun-   | succeeded      |

  @smoke @sanity
  Scenario Outline: Delete TaskRun and verify removal
    When the user navigates to TaskRuns tab
    And the user deletes the taskrun "<taskrun_name>"
    And the user navigates to the Tasks page
    And the user navigates to TaskRuns tab
    Then the taskrun "<taskrun_name>" should not appear in the taskruns list

    Examples:
      | taskrun_name      |
      | simple-taskrun-   |
