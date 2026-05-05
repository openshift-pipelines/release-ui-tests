"""
Task Navigation Test Steps.

This module contains BDD step definitions for task-specific navigation,
including tab navigation (Tasks, TaskRuns) and page verifications.
Follows Single Responsibility Principle - handles only task domain navigation.
"""

from pytest_bdd import scenarios

# Register scenarios from tasks_test.feature
scenarios("../features/pipeline_navigation_tasks_and_sub_pages.feature")
