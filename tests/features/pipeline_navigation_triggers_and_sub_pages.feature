Feature: Validate User is able to navigate to Triggers, EventListeners & TriggerTemplates, TriggerBindings,
  ClusterTriggerBindings Pages & underlying sub pages

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smoke
  Scenario: Verify successful navigation to Triggers page and Sub Tabs
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Triggers page
    And the user navigates to TriggerTemplates tab
    And the user navigates to TriggerBindings tab
    And the user navigates to ClusterTriggerBindings tab
