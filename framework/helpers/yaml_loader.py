"""YAML test data loader utility.

Provides centralized access to test data YAML files, eliminating code duplication.
Follows DRY principle - single source of truth for test data loading.
"""

from pathlib import Path
from typing import Any, Dict


class YamlLoader:
    """Centralized YAML test data loader.

    Provides class methods for loading test data from various resource directories.
    Eliminates duplicate file-reading logic across step definitions.
    """

    TEST_DATA_BASE = Path(__file__).parent.parent / "resources" / "test_data"

    @classmethod
    def load_task_yaml(cls, yaml_filename: str) -> str:
        """
        Load a task YAML file from test_data/tasks directory.

        :param str yaml_filename: Name of the YAML file (e.g., "simple_task.yaml")
        :return: str: YAML content as string
        :raises FileNotFoundError: If the YAML file does not exist
        """
        yaml_path = cls.TEST_DATA_BASE / "tasks" / yaml_filename
        if not yaml_path.exists():
            raise FileNotFoundError(f"Task YAML file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            return f.read()

    @classmethod
    def load_pipeline_yaml(cls, yaml_filename: str) -> str:
        """
        Load a pipeline YAML file from test_data/pipelines directory.

        :param str yaml_filename: Name of the YAML file (e.g., "simple_pipeline.yaml")
        :return: str: YAML content as string
        :raises FileNotFoundError: If the YAML file does not exist
        """
        yaml_path = cls.TEST_DATA_BASE / "pipelines" / yaml_filename
        if not yaml_path.exists():
            raise FileNotFoundError(f"Pipeline YAML file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            return f.read()

    @classmethod
    def load_pipelinerun_yaml(cls, yaml_filename: str) -> str:
        """
        Load a pipelinerun YAML file from test_data/pipelineruns directory.

        :param str yaml_filename: Name of the YAML file (e.g., "simple_pipelinerun.yaml")
        :return: str: YAML content as string
        :raises FileNotFoundError: If the YAML file does not exist
        """
        yaml_path = cls.TEST_DATA_BASE / "pipelineruns" / yaml_filename
        if not yaml_path.exists():
            raise FileNotFoundError(f"PipelineRun YAML file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            return f.read()

    @classmethod
    def load_taskrun_yaml(cls, yaml_filename: str) -> str:
        """
        Load a taskrun YAML file from test_data/taskruns directory.

        :param str yaml_filename: Name of the YAML file (e.g., "simple_taskrun.yaml")
        :return: str: YAML content as string
        :raises FileNotFoundError: If the YAML file does not exist
        """
        yaml_path = cls.TEST_DATA_BASE / "taskruns" / yaml_filename
        if not yaml_path.exists():
            raise FileNotFoundError(f"TaskRun YAML file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            return f.read()

    @classmethod
    def get_task_metadata(cls, yaml_content: str) -> Dict[str, str]:
        """
        Extract metadata from task YAML content.

        :param str yaml_content: YAML content string
        :return: Dict[str, str]: Metadata dictionary with 'name', 'kind', 'apiVersion'
        :raises ValueError: If YAML content is invalid or missing required fields
        """
        import yaml

        try:
            data = yaml.safe_load(yaml_content)
            return {
                "name": data.get("metadata", {}).get("name", ""),
                "kind": data.get("kind", ""),
                "apiVersion": data.get("apiVersion", ""),
            }
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content: {e}")

    @classmethod
    def get_pipeline_metadata(cls, yaml_content: str) -> Dict[str, str]:
        """
        Extract metadata from pipeline YAML content.

        :param str yaml_content: YAML content string
        :return: Dict[str, str]: Metadata dictionary with 'name', 'kind', 'apiVersion'
        :raises ValueError: If YAML content is invalid or missing required fields
        """
        import yaml

        try:
            data = yaml.safe_load(yaml_content)
            return {
                "name": data.get("metadata", {}).get("name", ""),
                "kind": data.get("kind", ""),
                "apiVersion": data.get("apiVersion", ""),
            }
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content: {e}")

    @classmethod
    def get_labels_and_annotations(cls, yaml_content: str) -> Dict[str, Any]:
        """
        Extract labels and annotations from YAML content.

        :param str yaml_content: YAML content string
        :return: Dict[str, Any]: Dictionary with 'labels' (dict) and 'annotations' (dict)
        :raises ValueError: If YAML content is invalid
        """
        import yaml

        try:
            data = yaml.safe_load(yaml_content)
            metadata = data.get("metadata", {})
            return {
                "labels": metadata.get("labels", {}),
                "annotations": metadata.get("annotations", {}),
            }
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content: {e}")
