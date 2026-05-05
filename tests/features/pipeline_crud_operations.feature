Feature: Pipeline CRUD Operations

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Pipelines page
    And user switches to current project

  @smoke @sanity
  Scenario Outline: Create pipeline and verify redirection to pipeline details page
    When the user creates a pipeline from YAML file "<yaml_file>"
    Then validate user is redirected to pipeline details page for pipeline "<pipeline_name>"
    And the pipeline details page should display the pipeline name as "<pipeline_name>"

    Examples:
      | yaml_file               | pipeline_name   |
      | simple_pipeline.yaml    | simple-pipeline |

  @smoke @sanity
  Scenario Outline: Verify pipeline exists in pipeline list page
    When the user navigates to the Pipelines page
    Then the pipeline "<pipeline_name>" should appear in the pipelines list

    Examples:
      | pipeline_name   |
      | simple-pipeline |

  @smoke @sanity
  Scenario Outline: Edit Pipeline YAML & Verify
    When the user navigates to the Pipelines page
    And the user edits the pipeline "<pipeline_name>" with YAML file "<updated_yaml_file>"
    Then validate user is redirected to pipeline details page for pipeline "<pipeline_name>"
    And the pipeline details page should display the pipeline name as "<pipeline_name>"

    Examples:
      | pipeline_name   | updated_yaml_file               |
      | simple-pipeline | simple_pipeline_updated.yaml    |

  @smoke @sanity
  Scenario Outline: Verify edited pipeline appears in pipelines list page
    When the user navigates to the Pipelines page
    Then the pipeline "<pipeline_name>" should appear in the pipelines list

    Examples:
      | pipeline_name   |
      | simple-pipeline |

  @smoke @sanity
  Scenario Outline: Delete pipeline and verify it does not appear in pipelines list page
    When the user deletes the pipeline "<pipeline_name>"
    Then the pipeline "<pipeline_name>" should not appear in the pipelines list

    Examples:
      | pipeline_name   |
      | simple-pipeline |
