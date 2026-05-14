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
  Scenario Outline: Verify TaskRun appears in TaskRuns list & is executed successfully
    When the user navigates to TaskRuns tab
    Then the taskrun "<taskrun_name>" should appear in the taskruns list
    And the taskrun "<taskrun_name>" is executed with status "<taskrun_status>"

    Examples:
      | taskrun_name      | taskrun_status |
      | simple-taskrun-   | succeeded      |


  @smoke @sanity
  Scenario Outline: Validate TaskRun details page displays all information
    When the taskrun details page should display the taskrun name as "<taskrun_name>"
    Then the taskrun details page should display namespace
    And the taskrun details page should display status
    And the taskrun details page should display labels
    And the taskrun details page should display annotations count

    Examples:
      | taskrun_name      |
      | simple-taskrun-   |


  @smoke @sanity
  Scenario Outline: Validate TaskRun YAML page displays YAML editor
    When the user navigates to taskrun YAML tab for taskrun "<taskrun_name>"
    Then the taskrun YAML editor should be visible

    Examples:
      | taskrun_name      |
      | simple-taskrun-   |


  @smoke @sanity
  Scenario Outline: Validate TaskRun logs page displays logs
    When the user navigates to taskrun logs tab for taskrun "<taskrun_name>"
    Then the taskrun logs container should be visible
    And the taskrun step navigation should be visible
    And the taskrun should have at least 1 step available
    And the taskrun logs content should not be empty

    Examples:
      | taskrun_name      |
      | simple-taskrun-   |


#  @smoke @sanity
#  Scenario Outline: Delete TaskRun and verify removal
#    When the user navigates to TaskRuns tab
#    And the user deletes the taskrun "<taskrun_name>"
#    And the user navigates to the Tasks page
#    And the user navigates to TaskRuns tab
#    Then the taskrun "<taskrun_name>" should not appear in the taskruns list
#
#    Examples:
#      | taskrun_name      |
#      | simple-taskrun-   |
