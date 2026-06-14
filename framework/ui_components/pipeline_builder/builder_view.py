from typing import Dict

from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import BuilderViewLocators
from framework.ui_components.base_page import BasePage


class BuilderView(BasePage):
    """
    View object for Pipeline Builder's visual form interface.
    Handles builder-specific UI elements and interactions for creating pipelines
    using the visual builder view.
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = BuilderViewLocators()

    # ==================== Pipeline Name Methods ====================

    async def fill_pipeline_name(self, name: str) -> bool:
        """
        Fills the pipeline name input field.
        :param str name: The name for the pipeline.
        :return: bool: True if fill succeeds.
        """
        return await self.fill_input(self.locators.PIPELINE_NAME_INPUT, name)

    # ==================== Task Management Methods ====================

    async def click_add_task(self) -> bool:
        """
        Clicks the 'Add task' button to open the quick search dialog for adding tasks.
        Note: The "Add task" element is an SVG in the pipeline builder canvas.
        :return: bool: True if click succeeds.
        """
        # The Add task element is an SVG with data-test="task-list"
        return await self.click_element(self.locators.ADD_TASK_BUTTON)

    async def search_task(self, search_text: str) -> bool:
        """
        Types text into the quick search bar to search for tasks.
        :param str search_text: The text to search for.
        :return: bool: True if fill succeeds.
        """
        # Wait for quick search input to be visible
        await self.page.wait_for_selector(self.locators.QUICK_SEARCH_INPUT, state="visible", timeout=10000)
        return await self.fill_input(self.locators.QUICK_SEARCH_INPUT, search_text)

    async def click_add_task_from_search(self) -> bool:
        """
        Clicks the 'Add' button in the task search results to add the selected task.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.ADD_TASK_FROM_SEARCH_BUTTON)

    async def add_task_by_name(self, task_name: str) -> bool:
        """
        High-level helper to add a task by name using the quick search.
        :param str task_name: Name of the task to add (e.g., "git-clone", "git-cli").
        :return: bool: True if task was added successfully.
        """
        await self.click_add_task()
        # Wait for quick search dialog to be visible
        await self.page.wait_for_selector(self.locators.QUICK_SEARCH_INPUT, state="visible", timeout=10000)
        await self.search_task(task_name)
        # Wait for search results to populate
        await self.page.wait_for_selector(self.locators.ADD_TASK_FROM_SEARCH_BUTTON, state="visible", timeout=10000)
        await self.click_add_task_from_search()
        # Wait for task node to appear in canvas
        task_node_locator = self.locators.TASK_NODE_TEMPLATE.format(task_name=task_name)
        await self.page.wait_for_selector(task_node_locator, state="visible", timeout=15000)
        return True

    async def click_task_node(self, task_name: str) -> bool:
        """
        Clicks on a task node in the pipeline canvas to open its configuration panel.
        :param str task_name: Name of the task to click.
        :return: bool: True if click succeeds.
        """
        task_node_locator = self.locators.TASK_NODE_TEMPLATE.format(task_name=task_name)
        success = await self.click_element(task_node_locator)
        if success:
            # Wait for task configuration sidebar to be visible
            await self.page.wait_for_selector(self.locators.TASK_NAME_INPUT, state="visible", timeout=10000)
        return success

    async def fill_task_name(self, task_name: str) -> bool:
        """
        Fills the task name field in the task configuration panel.
        :param str task_name: Name for the task instance.
        :return: bool: True if fill succeeds.
        """
        return await self.fill_input(self.locators.TASK_NAME_INPUT, task_name)

    # ==================== Task Parameter Configuration Methods ====================

    async def configure_task_param(self, task_index: int, param_index: int, value: str) -> bool:
        """
        Configures a specific parameter for a task using dynamic locator pattern.
        :param int task_index: Zero-based index of the task (0 for first task, 1 for second, etc.).
        :param int param_index: Zero-based index of the parameter within the task.
        :param str value: Value to set for the parameter.
        :return: bool: True if parameter was configured successfully.
        """
        param_locator = self.locators.TASK_PARAM_TEMPLATE.format(task_index=task_index, param_index=param_index)
        return await self.fill_input(param_locator, value)

    async def configure_multiple_task_params(self, task_index: int, params: Dict[int, str]) -> bool:
        """
        Configures multiple parameters for a task in a single call.
        Useful for sparse parameter configuration (e.g., only params 0, 1, and 11).
        :param int task_index: Zero-based index of the task.
        :param Dict[int, str] params: Dictionary mapping param_index to value.
        :return: bool: True if all parameters were configured successfully.
        Example:
            params = {0: "user@example.com", 1: "username", 11: "git clone script"}
            await configure_multiple_task_params(0, params)
        """
        for param_index, value in params.items():
            success = await self.configure_task_param(task_index, param_index, value)
            if not success:
                return False
        return True

    # ==================== Task Workspace Methods ====================

    async def select_task_workspace(
        self, task_index: int, workspace_index: int, workspace_name: str, workspace_type: str = "output"
    ) -> bool:
        """
        Selects a workspace for a task from the workspace dropdown.
        :param int task_index: Zero-based index of the task.
        :param int workspace_index: Zero-based index of the workspace dropdown.
        :param str workspace_name: Name of the workspace to select.
        :param str workspace_type: Type of workspace (output, ssh-directory, basic-auth, ssl-ca-directory).
        :return: bool: True if workspace was selected successfully.
        """
        workspace_locator = self.locators.TASK_WORKSPACE_TEMPLATE.format(workspace_type=workspace_type)

        # Wait for the workspace dropdown to be visible
        await self.page.wait_for_selector(workspace_locator, state="visible", timeout=10000)

        loc = self.page.locator(workspace_locator)
        await loc.select_option(label=workspace_name)
        return True

    # ==================== Pipeline Configuration Methods ====================

    async def click_add_parameter(self) -> bool:
        """
        Clicks the 'Add parameter' button to add a new parameter to the pipeline.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.ADD_PARAMETER_BUTTON)

    async def click_add_workspace(self) -> bool:
        """
        Clicks the 'Add workspace' button to add a new workspace to the pipeline.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.ADD_WORKSPACE_BUTTON)

    async def configure_pipeline_parameter(
        self, param_index: int, name: str, description: str = "", default_value: str = ""
    ) -> bool:
        """
        Configures a pipeline parameter by filling its name, description, and default value.
        :param int param_index: Zero-based index of the parameter.
        :param str name: Parameter name.
        :param str description: Parameter description (optional).
        :param str default_value: Parameter default value (optional).
        :return: bool: True if parameter was configured successfully.
        """
        # Wait for parameter input field to be visible, then fill parameter name
        name_locator = self.locators.PIPELINE_PARAM_NAME_TEMPLATE.format(param_index=param_index)
        await self.page.wait_for_selector(name_locator, state="visible", timeout=10000)
        await self.fill_input(name_locator, name)

        # Fill parameter description if provided
        if description:
            desc_locator = self.locators.PIPELINE_PARAM_DESC_TEMPLATE.format(param_index=param_index)
            await self.fill_input(desc_locator, description)

        # Fill default value if provided
        if default_value:
            default_locator = self.locators.PIPELINE_PARAM_DEFAULT_TEMPLATE.format(param_index=param_index)
            await self.fill_input(default_locator, default_value)

        return True

    async def configure_pipeline_workspace(self, workspace_index: int, name: str) -> bool:
        """
        Configures a pipeline workspace by filling its name.
        :param int workspace_index: Zero-based index of the workspace.
        :param str name: Workspace name.
        :return: bool: True if workspace was configured successfully.
        """
        workspace_locator = self.locators.PIPELINE_WORKSPACE_NAME_TEMPLATE.format(workspace_index=workspace_index)
        # Wait for workspace input field to be visible
        await self.page.wait_for_selector(workspace_locator, state="visible", timeout=10000)
        return await self.fill_input(workspace_locator, name)

    # ==================== Helper/Workflow Methods ====================
