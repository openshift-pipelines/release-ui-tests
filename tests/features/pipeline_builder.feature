Feature: Pipeline Builder Sanity Tests

  Background:
    Given the user is logged into openshift console with auth kube:admin
    When the user expands Pipelines in left navigation bar
    And the user navigates to the Pipelines page
    And user switches to current project

  @smoke @sanity
  Scenario: Create pipeline using Pipeline Builder
    When the user clicks Create button on Pipelines page
    And the user clicks Pipeline menu item
    Then the user should be on Pipeline Builder page
    When the user fills pipeline name "builder-test-pipeline" in builder view
    And the user adds pipeline workspace with name "source"
    And the user adds task "git-cli" in builder view
    And the user clicks on task "git-cli" to configure
    And the user configures git-cli task:
      | field        | value       |
      | displayName  | git-command |
      | source       | source      |
    And the user clicks Create button on Pipeline Builder page
    Then the user should be on pipeline details page
    And the pipeline details page should display the pipeline name as "builder-test-pipeline"
