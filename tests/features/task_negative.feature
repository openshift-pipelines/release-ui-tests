@regression
Feature: Task Negative Scenarios

  Background:
    Given the user is logged into openshift console
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Tasks page
    And user switches to current project

  Scenario Outline: Create a task from invalid YAML and verify the error message
    When the user submits task YAML file "<yaml_file>"
    Then a task validation error alert is displayed

    Examples:
      | yaml_file         |
      | invalid_task.yaml |

  Scenario Outline: Edit a valid task with invalid YAML and verify the error message
    When the user creates a valid task from YAML file "<valid_yaml_file>"
    And the user navigates to the Tasks page
    And the user edits task "<task_name>" with invalid YAML file "<invalid_yaml_file>"
    Then a task validation error alert is displayed

    Examples:
      | valid_yaml_file         | task_name          | invalid_yaml_file      |
      | negative_edit_task.yaml | negative-edit-task | invalid_task_edit.yaml |

  Scenario Outline: Add invalid annotations to a task and verify the error message
    When the user opens the Edit annotations dialog for task "<task_name>"
    And the user submits invalid annotation "<annotation_key>" with value "<annotation_value>"
    Then an annotations validation error alert is displayed for "<annotation_key>"
    And the user closes the edit annotations dialog

    Examples:
      | task_name          | annotation_key | annotation_value |
      | negative-edit-task | qeew0-         | invalid          |

  Scenario Outline: Add invalid labels to a task and verify the error message
    When the user opens the Edit labels dialog for task "<task_name>"
    And the user submits invalid label "<label_key>" with value "<label_value>"
    Then a labels validation error alert is displayed for "<label_key>"
    And the user closes the edit labels dialog

    Examples:
      | task_name          | label_key | label_value |
      | negative-edit-task | wfe32435- | invalid     |

  Scenario Outline: Cancel task creation and verify the task is not created
    When the user enters task YAML file "<yaml_file>" and cancels creation
    Then the task "<task_name>" should not appear in the tasks list

    Examples:
      | yaml_file           | task_name             |
      | cancelled_task.yaml | cancelled-create-task |

  Scenario Outline: Cancel task deletion and verify the task remains in the list
    When the user starts deletion of task "<task_name>" and cancels it
    Then the task "<task_name>" should appear in the tasks list

    Examples:
      | task_name          |
      | negative-edit-task |
