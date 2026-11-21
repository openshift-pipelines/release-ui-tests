@regression
Feature: Task CRUD Operations

  Background:
    Given the user is logged into openshift console
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Tasks page
    And user switches to current project

  @sanity
  Scenario Outline: Create tasks from YAML and verify redirection to task details page
    When the user creates a task from YAML file "<yaml_file>"
    Then validate user is redirected to task details page for task "<task_name>"
    And the task details page should display heading with task name as "<task_name>"

    Examples:
      | yaml_file        | task_name   |
      | simple_task.yaml | simple-task |

  @sanity
  Scenario Outline:  Verify created task appears in list
    Then the task "<task_name>" should appear in the tasks list

    Examples:
      | task_name    |
      | simple-task  |

  @sanity
  Scenario Outline: Validate all available fields in task details page
    When the user navigates to task details page for task "<task_name>"
    Then the task details page should display the task name as "<task_name>"
    And the task details page should display namespace
    And the task details page should contain labels with value "<labels>"
    And the task details page should contain appropriate count of annotations value with "<annotations>"

    Examples:
      | task_name   | labels                                    | annotations                                                            |
      | simple-task | {"version": "v1", "app": "tekton-test" }  | { "description": "A simple task for testing", "owner": "test-user"}    |

  @sanity
  Scenario Outline: Validate annotations fields in annotations dialog of task details page
    When the user navigates to task details page for task "<task_name>"
    When the user navigates to edit annotations dialog from task details page
    Then the annotations dialog of task details page should contain annotations with value "<annotations>"
    Then the user closes the edit annotations dialog

    Examples:
      | task_name       |   annotations                                                      |
      | simple-task     |{ "description": "A simple task for testing", "owner": "test-user"} |


  @sanity
  Scenario Outline: Edit task via task yaml page & validate changes in task details page
    When the user edits the task "<task_name>" with YAML file "<updated_yaml_file>"
    Then the user navigates to task details tab
    And the task details page should display heading with task name as "<task_name>"

    Examples:
      |  task_name   | updated_yaml_file          |
      |  simple-task | simple_task_updated.yaml   |

  @sanity
  Scenario Outline:  Verify edited task appears in list
    Then the task "<task_name>" should appear in the tasks list

    Examples:
      | task_name    |
      | simple-task  |

  @sanity
  Scenario Outline: Validate updated labels and annotation count in task details page
    When the user navigates to task details page for task "<task_name>"
    Then the task details page should contain labels with value "<labels>"
    And the task details page should contain appropriate count of annotations value with "<annotations>"

    Examples:
      | task_name   | labels                                            | annotations                                                                         |
      | simple-task | {"version": "v2", "app": "tekton-test-updated"}   | {"description": "An updated simple task for testing", "owner": "updated-test-user"} |

  @sanity
  Scenario Outline: Validate updated annotations in task details edit annotations dialog
    When the user navigates to task details page for task "<task_name>"
    And the user navigates to edit annotations dialog from task details page
    Then the annotations dialog of task details page should contain annotations with value "<annotations>"
    And the user closes the edit annotations dialog

    Examples:
      | task_name   | annotations                                                                         |
      | simple-task | {"description": "An updated simple task for testing", "owner": "updated-test-user"} |

  @sanity
  Scenario Outline: Edit task labels via edit labels dialog & validate changes in task details page
    When the user opens Edit labels dialog using Edit task option for task "<task_name>"
    And the user adds labels to task "<task_name>" with labels "<labels>"
    And the user navigates to task details page for task "<task_name>"
    Then the task details page should contain labels with value "<labels>"

    Examples:
      |  task_name   | labels                |
      |  simple-task | {"automation": "ui"}  |

  @sanity
  Scenario Outline: Edit task annotations via edit annotations dialog & validate changes in task details page
    When the user opens Edit annotations dialog using Edit annotations option for task "<task_name>"
    And the user adds new annotations to task "<task_name>" with annotations "<update_annotations>"
    And the user navigates to task details page for task "<task_name>"
    Then the task details page should contain appropriate count of annotations value with "<annotations>"

    Examples:
      |  task_name   | update_annotations      | annotations                                                                                               |
      |  simple-task | {"task": "automation"}  | {"description": "An updated simple task for testing", "owner": "updated-test-user", "task": "automation"} |

  @sanity
  Scenario Outline: Delete task and verify removal
    When the user deletes the task "<task_name>"
    Then the task "<task_name>" should not appear in the tasks list

    Examples:
      |  task_name     |
      |  simple-task   |
