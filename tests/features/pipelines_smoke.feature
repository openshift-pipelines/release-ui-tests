Feature: Pipeline Management

  @smoke @sanity
  Scenario: Verify access to the Pipelines page after successful login
    Given the user is on the OpenShift login page
    When user chooses to login with kube:admin
    And the user logs in with valid credentials
    And the user navigates to the Pipelines section
    Then the Pipelines page should be visible
