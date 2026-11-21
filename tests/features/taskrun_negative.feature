@regression
Feature: TaskRun Negative Scenarios

  Background:
    Given the user is logged into openshift console
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Tasks page
    And user switches to current project

  Scenario Outline: Create a taskrun from invalid YAML and verify the error message
    When the user creates a task via cli from YAML file "<task_yaml_file>"
    And the user submits taskrun YAML file "<yaml_file>"
    Then a taskrun validation error alert is displayed

    Examples:
      | task_yaml_file             | yaml_file            |
      | negative_taskrun_task.yaml | invalid_taskrun.yaml |

  Scenario Outline: Edit an existing taskrun from yaml page and verify save button does not appear
    # Completed TaskRuns render the YAML tab read-only (no Save). Use a short-lived Task.
    When the user creates a task via cli from YAML file "<task_yaml_file>"
    And the user creates a valid taskrun from YAML file "<valid_yaml_file>"
    And the user navigates to TaskRuns tab
    Then the user should not find save button for taskrun "<taskrun_name>" in taskrun yaml page

    Examples:
      | task_yaml_file             | valid_yaml_file            | taskrun_name          |
      | negative_taskrun_task.yaml | negative_edit_taskrun.yaml | negative-edit-taskrun |

  Scenario Outline: Add invalid annotations to a taskrun and verify the error message
    When the user opens the Edit annotations dialog for taskrun "<taskrun_name>"
    And the user submits invalid taskrun annotation "<annotation_key>" with value "<annotation_value>"
    Then a taskrun annotations validation error alert is displayed for "<annotation_key>"
    And the user closes the taskrun edit annotations dialog

    Examples:
      | taskrun_name          | annotation_key | annotation_value |
      | negative-edit-taskrun | qeew0-         | invalid          |

  Scenario Outline: Add invalid labels to a taskrun and verify the error message
    When the user opens the Edit labels dialog for taskrun "<taskrun_name>"
    And the user submits invalid taskrun label "<label_key>" with value "<label_value>"
    Then a taskrun labels validation error alert is displayed for "<label_key>"
    And the user closes the taskrun edit labels dialog

    Examples:
      | taskrun_name          | label_key | label_value |
      | negative-edit-taskrun | wfe32435- | invalid     |

  Scenario Outline: Cancel taskrun creation and verify the taskrun is not created
    When the user creates a task via cli from YAML file "<task_yaml_file>"
    And the user enters taskrun YAML file "<yaml_file>" and cancels creation
    Then the taskrun "<taskrun_name>" should not appear in the taskruns list

    Examples:
      | task_yaml_file             | yaml_file              | taskrun_name              |
      | negative_taskrun_task.yaml | cancelled_taskrun.yaml | cancelled-create-taskrun  |

  Scenario Outline: Cancel taskrun deletion and verify the taskrun remains in the list
    When the user navigates to TaskRuns tab
    And the user starts deletion of taskrun "<taskrun_name>" and cancels it
    Then the taskrun "<taskrun_name>" should appear in the taskruns list

    Examples:
      | taskrun_name          |
      | negative-edit-taskrun |
