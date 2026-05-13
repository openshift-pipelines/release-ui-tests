Feature: New Pipelines Tasks Navigation & Visibility

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smokee @sanity
  Scenario: New Verify successful navigation to Triggers page and Sub Tabs
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Triggers page
    And the user navigates to TriggerTemplates tab
    And the user navigates to TriggerBindings tab
    And the user navigates to ClusterTriggerBindings tab
