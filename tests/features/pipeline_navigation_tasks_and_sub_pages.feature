Feature: Validate User is able to navigate to Tasks, TaskRuns Pages & underlying sub pages

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smoke
  Scenario: Verify successful navigation to Tasks page and Sub Tabs
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Tasks page
    And the user navigates to TaskRuns tab
