Feature: Pipelines UI Navigation & Visibility

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smokee @sanity
  Scenario: Verify Pipelines button is visible in left navigation bar
    Then Validate Pipelines button is visible in the left navigation bar


  @smokee @sanity
  Scenario Outline: Verify appropriate links are available under pipelines button
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then Verify the following <links> are available under Pipelines button
    Examples:
    | links     |
    | Overview  |
#    | Pipelines |
#    | Tasks     |
#    | Triggers  |


  @smoke @sanity
  Scenario: Verify successful navigation to Overview page
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Overview page


  @smoke @sanity
  Scenario: Verify successful navigation to Pipelines page and Sub Tabs
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Pipelines page
    And the user navigates to PipelineRuns tab
    And the user navigates to Repositories tab


  @smoke @sanity
  Scenario: Verify successful navigation to Tasks page and Sub Tabs
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Tasks page
    And the user navigates to TaskRuns tab


  @smoke @sanity
  Scenario: Verify successful navigation to Triggers page and Sub Tabs
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then the user navigates to the Triggers page
    And the user navigates to TriggerTemplates tab
    And the user navigates to TriggerBindings tab
    And the user navigates to ClusterTriggerBindings tab
