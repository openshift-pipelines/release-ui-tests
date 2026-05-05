Feature: Validate User is able to navigate to Pipelines, PipelineRuns & Repositories Pages & underlying sub pages

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smoke
  Scenario: Verify successful navigation to Overview page
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Overview page
