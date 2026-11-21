@regression
Feature: TaskRun CRUD Operations

  Background:
    Given the user is logged into openshift console
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Tasks page
    And user switches to current project

  @sanity
  Scenario Outline: Create TaskRun and verify redirect to details page
    When the user creates a task via cli from YAML file "<task_yaml_file>"
    And the user creates a taskrun from YAML file "<yaml_file>"
    Then validate user is redirected to taskrun details page for taskrun "<taskrun_name>"
    And the taskrun details page should display the taskrun name as "<taskrun_name>"

    Examples:
      | task_yaml_file   | yaml_file            | taskrun_name      |
      | simple_task.yaml | simple_taskrun.yaml  | simple-taskrun-   |

  @sanity
  Scenario Outline: Verify TaskRun appears in TaskRuns list
    When the user navigates to TaskRuns tab
    Then the taskrun "<taskrun_name>" should appear in the taskruns list

    Examples:
      | taskrun_name      |
      | simple-taskrun-   |


  @sanity
  Scenario Outline: Verify TaskRun is executed successfully
    When the user navigates to TaskRuns tab
    Then the taskrun "<taskrun_name>" is executed with status "<taskrun_status>"

    Examples:
      | taskrun_name      | taskrun_status |
      | simple-taskrun-   | succeeded      |


  @sanity
  Scenario Outline: Validate all available fields in taskrun details page
    When the user navigates to TaskRuns tab
    When the user navigates to taskrun details page for taskrun "<taskrun_name>"
    Then the taskrun details page should display the taskrun name as "<taskrun_name>"
    And the taskrun details page should display namespace
    And the taskrun details page should contain labels with value "<labels>"
    And the taskrun details page should contain appropriate count of annotations value as "<annotations_count>"

    Examples:
      | taskrun_name      | labels                                                  |   annotations_count   |
      | simple-taskrun-   | {"app.kubernetes.io/managed-by": "tekton-pipelines"}    |       5               |


  Scenario Outline: Edit above task run to update labels & validate in taskrun details page
    When the user navigates to TaskRuns tab
    When the user navigates to taskrun details page for taskrun "<taskrun_name>"
    When the user opens edits labels popup of taskrun from taskrun details page
    And the user adds labels to taskrun "<task_name>" with labels "<update_labels>"
    Then the taskrun details page should contain labels with value "<update_labels>"

    Examples:
      | taskrun_name      | update_labels          |
      | simple-taskrun-   | {"cleanup": "true"}    |


  Scenario Outline: Edit above task run to update annotations & validate in taskrun details page
    When the user navigates to TaskRuns tab
    When the user navigates to taskrun details page for taskrun "<taskrun_name>"
    When the user opens edits annotations popup of taskrun from taskrun details page
    And the user adds new annotations to taskrun "<taskrun_name>" with annotations "<update_annotations>"
    Then the taskrun details page should contain appropriate count of annotations value as "<annotations_count>"

    Examples:
      | taskrun_name      |   update_annotations         |   annotations_count    |
      | simple-taskrun-   |  {"status": "succeeded"}     |   6                    |


  @skip @known_bug
  # KNOWN BUG: TaskRun delete operation fails in OpenShift Console
  # Issue: Deleted Taskrun does not disappear from taskruns page (even after switching pages)
  # Affects: OSP 1.21.x, 1.22.x, 1.23.x
  # Root Cause: Deleted Taskrun takes higher time to disappear from taskruns list
  # Tracking: SRVKP-12032
  # Expected Fix: OSP 1.24.x
  # Last Verified: 2026-06-22
  # TODO: Re-enable this test once bug is fixed and verified
  Scenario Outline: Delete TaskRun and verify removal
    When the user navigates to TaskRuns tab
    And the user deletes the taskrun "<taskrun_name>"
    And the user navigates to the Tasks page
    And the user navigates to TaskRuns tab
    Then the taskrun "<taskrun_name>" should not appear in the taskruns list

    Examples:
      | taskrun_name      |
      | simple-taskrun-   |
