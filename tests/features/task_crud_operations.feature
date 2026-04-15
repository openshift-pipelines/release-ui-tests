Feature: Task CRUD Operations

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar
    When the user navigates to the Tasks page
    And user switches to current project

  @smoke @sanity
  Scenario Outline: Create tasks from YAML and verify redirection to task details page
    When the user creates a task from YAML file "<yaml_file>"
    Then validate user is redirected to task details page for task "<task_name>"
    And the task details page should display the task name as "<task_name>"

    Examples:
      | yaml_file            | task_name       |
      | task_for_create.yaml | task-for-create |

  @smoke @sanity
  Scenario Outline:  Verify created task appears in list
    Then the task "<task_name>" should appear in the tasks list

    Examples:
      | task_name       |
      | task-for-create |


  @sanity
  Scenario Outline: Edit created task & validate changes in task details page
    When the user edits the task "<task_name>" with YAML file "<updated_yaml_file>"
    Then the task details page should display the task name as "<task_name>"

    Examples:
      |  task_name       | updated_yaml_file          |
      |  task-for-create | task_for_edit_updated.yaml   |

  @smoke @sanity
  Scenario Outline:  Verify edited task appears in list
    Then the task "<task_name>" should appear in the tasks list

    Examples:
      | task_name       |
      | task-for-create |

  @sanity
  Scenario Outline: Delete task and verify removal
    When the user deletes the task "<task_name>"
    Then the task "<task_name>" should not appear in the tasks list

    Examples:
      |  task_name         |
      |  task-for-create   |
