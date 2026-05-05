Feature: Validate User is able to navigate to Pipelines, PipelineRuns & Repositories Pages & underlying sub pages

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smoke
  Scenario: Verify successful navigation to Pipelines page and Sub Tabs
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Pipelines page
    And the user navigates to PipelineRuns tab
    And the user navigates to Repositories tab
