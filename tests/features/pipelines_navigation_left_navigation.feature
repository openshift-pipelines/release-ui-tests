Feature: Validate Appropriate Pipeline links are available under left navigation bar

  Background:
    Given the user is logged into openshift console with auth kube:admin

  @smoke
  Scenario: Verify Pipelines button is visible in left navigation bar
    Then Validate Pipelines button is visible in the left navigation bar


  @smoke
  Scenario Outline: Verify appropriate links are available under pipelines button
    Given Validate Pipelines button is visible in the left navigation bar
    And the user clicks on Pipelines button
    Then Verify the following <links> are available under Pipelines button
    Examples:
    | links     |
    | Overview  |
    | Pipelines |
    | Tasks     |
    | Triggers  |
