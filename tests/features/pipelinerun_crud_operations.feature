Feature: PipelineRun CRUD Operations

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Pipelines page
    And user switches to current project

  @smoke @sanity
  Scenario Outline: Create PipelineRun and verify redirect to details page
    When the user creates a pipeline via cli from YAML file "<pipeline_yaml_file>"
    And the user creates a pipelinerun from YAML file "<yaml_file>"
    Then validate user is redirected to pipelinerun details page for pipelinerun "<pipelinerun_name>"
    And the pipelinerun details page should display the pipelinerun name as "<pipelinerun_name>"

    Examples:
      | pipeline_yaml_file   | yaml_file                   | pipelinerun_name      |
      | simple_pipeline.yaml | simple_pipelinerun.yaml     | simple-pipelinerun-   |

  @smoke @sanity
  Scenario Outline: Verify PipelineRun appears in PipelineRuns list
    When the user navigates to PipelineRuns tab
    Then the pipelinerun "<pipelinerun_name>" should appear in the pipelineruns list

    Examples:
      | pipelinerun_name      |
      | simple-pipelinerun-   |

  @smoke @sanity
  Scenario Outline: Verify PipelineRun is executed successfully
    When the user navigates to PipelineRuns tab
    Then the pipelinerun "<pipelinerun_name>" is executed with status "<pipelinerun_status>"

    Examples:
      | pipelinerun_name      | pipelinerun_status |
      | simple-pipelinerun-   | succeeded          |

  @smoke @sanity
  Scenario Outline: Delete PipelineRun and verify removal
    When the user navigates to PipelineRuns tab
    And the user deletes the pipelinerun "<pipelinerun_name>"
    And the user navigates to the Pipelines page
    And the user navigates to PipelineRuns tab
    Then the pipelinerun "<pipelinerun_name>" should not appear in the pipelineruns list

    Examples:
      | pipelinerun_name      |
      | simple-pipelinerun-   |
