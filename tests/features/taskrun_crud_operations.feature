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
