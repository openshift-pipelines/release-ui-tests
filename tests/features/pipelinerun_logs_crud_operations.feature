Feature: PipelineRun Logs CRUD Operations

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Pipelines page
    And user switches to current project

  @smoke
  Scenario: Create PipelineRun and verify logs display expected content
    When the user creates a pipelinerun from YAML file "simple_pipelinerun_inline.yaml"
    And the user navigates to Logs tab
    And the user waits for logs to fully load
    Then the logs for task "greet" should contain "Hello from pipeline!"


  Scenario: Update PipelineRun and verify log output changes
    Given the user creates a pipelinerun from YAML file "simple_pipelinerun_inline.yaml"
    When the user navigates to Logs tab
    And the user waits for logs to fully load
    Then the logs for task "greet" should contain "Hello from pipeline!"
    When the user navigates to the Pipelines page
    And the user creates a pipeline via cli from YAML file "simple_pipeline_updated.yaml"
    And the user creates a pipelinerun from YAML file "simple_pipelinerun.yaml"
    And the user navigates to Logs tab
    And the user waits for logs to fully load
    Then the logs for task "greet" should contain "Hello from pipeline!"
    And the logs for task "farewell" should contain "Goodbye from pipeline!"
