"""
YAML Field Extractor and Placeholder Replacer.

Utility for extracting field values from Kubernetes YAML and replacing placeholders.
Used when editing existing resources that require preserving Kubernetes-generated fields.

Follows SOLID Principles:
- Single Responsibility: Handles only YAML field extraction and substitution
- Open/Closed: Extensible for different field path notations
- Dependency Inversion: Works with any YAML string, not tied to specific resources
"""

import logging
from typing import Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class YamlFieldExtractor:
    """
    Extracts field values from YAML content using dot-notation paths.

    Examples:
        extractor = YamlFieldExtractor()
        yaml_content = '''
        apiVersion: tekton.dev/v1
        kind: Task
        metadata:
          name: my-task
          resourceVersion: "12345"
        '''

        # Extract single field
        version = extractor.get_field_value(yaml_content, "metadata.resourceVersion")
        # Returns: "12345"

        # Extract multiple fields
        fields = extractor.get_multiple_fields(
            yaml_content,
            ["metadata.resourceVersion", "metadata.uid"]
        )
        # Returns: {"metadata.resourceVersion": "12345", "metadata.uid": "..."}
    """

    @staticmethod
    def get_field_value(yaml_content: str, field_path: str) -> Optional[str]:
        """
        Extract a single field value from YAML content using dot-notation path.

        :param str yaml_content: YAML content as string
        :param str field_path: Dot-notation path (e.g., "metadata.resourceVersion")
        :return: Optional[str]: Field value as string, or None if not found

        Examples:
            get_field_value(yaml_str, "metadata.resourceVersion")
            get_field_value(yaml_str, "metadata.labels.app")
            get_field_value(yaml_str, "spec.params[0].name")
        """
        try:
            # Parse YAML to dict
            data = yaml.safe_load(yaml_content)

            # Navigate through path
            keys = field_path.split(".")
            current = data

            for key in keys:
                # Handle array indices like "params[0]"
                if "[" in key and "]" in key:
                    # Extract key and index: "params[0]" -> "params", 0
                    field_name = key.split("[")[0]
                    index = int(key.split("[")[1].rstrip("]"))
                    current = current.get(field_name, [])[index]
                else:
                    current = current.get(key)

                if current is None:
                    logger.warning(f"Field path '{field_path}' not found in YAML")
                    return None

            # Convert to string
            return str(current)

        except Exception as e:
            logger.error(f"Failed to extract field '{field_path}': {e}")
            return None

    @staticmethod
    def get_multiple_fields(yaml_content: str, field_paths: list[str]) -> Dict[str, str]:
        """
        Extract multiple field values from YAML content.

        :param str yaml_content: YAML content as string
        :param list[str] field_paths: List of dot-notation paths
        :return: Dict[str, str]: Dictionary mapping field path to value

        Example:
            fields = get_multiple_fields(
                yaml_str,
                ["metadata.resourceVersion", "metadata.uid", "metadata.creationTimestamp"]
            )
            # Returns: {
            #     "metadata.resourceVersion": "12345",
            #     "metadata.uid": "abc-def",
            #     "metadata.creationTimestamp": "2024-01-01T00:00:00Z"
            # }
        """
        result = {}
        for path in field_paths:
            value = YamlFieldExtractor.get_field_value(yaml_content, path)
            if value is not None:
                result[path] = value
        return result

    @staticmethod
    def replace_placeholders(yaml_template: str, replacements: Dict[str, str]) -> str:
        """
        Replace placeholders in YAML template with actual values.

        Supports multiple placeholder formats:
        - {{field_path}} - Standard format
        - ${field_path} - Shell-style format
        - <field_path> - Angle bracket format

        :param str yaml_template: YAML content with placeholders
        :param Dict[str, str] replacements: Map of placeholder to value
        :return: str: YAML with placeholders replaced

        Example:
            template = '''
            apiVersion: tekton.dev/v1
            kind: Task
            metadata:
              name: my-task
              resourceVersion: "{{metadata.resourceVersion}}"
              uid: "{{metadata.uid}}"
            '''

            replacements = {
                "metadata.resourceVersion": "12345",
                "metadata.uid": "abc-def-ghi"
            }

            result = replace_placeholders(template, replacements)
            # Result has actual values instead of placeholders
        """
        result = yaml_template

        for field_path, value in replacements.items():
            # Support multiple placeholder formats
            placeholders = [
                f"{{{{{field_path}}}}}",  # {{field_path}}
                f"${{{field_path}}}",  # ${field_path}
                f"<{field_path}>",  # <field_path>
            ]

            for placeholder in placeholders:
                if placeholder in result:
                    result = result.replace(placeholder, value)
                    logger.debug(f"Replaced placeholder '{placeholder}' with '{value}'")

        return result

    @staticmethod
    def extract_and_replace(existing_yaml: str, new_yaml_template: str, field_paths: list[str]) -> str:
        """
        Extract fields from existing YAML and replace placeholders in new YAML.

        This is the main workflow method that combines extraction and replacement.

        :param str existing_yaml: Current YAML content from resource
        :param str new_yaml_template: New YAML template with placeholders
        :param list[str] field_paths: Fields to extract and replace
        :return: str: New YAML with placeholders replaced

        Example:
            # Existing task YAML (from editor)
            existing = '''
            apiVersion: tekton.dev/v1
            kind: Task
            metadata:
              name: my-task
              resourceVersion: "12345"
              uid: "abc-def"
            spec:
              steps: [...]
            '''

            # New YAML template (from file)
            new_template = '''
            apiVersion: tekton.dev/v1
            kind: Task
            metadata:
              name: my-task
              resourceVersion: "{{metadata.resourceVersion}}"
              uid: "{{metadata.uid}}"
            spec:
              steps: [...]  # Updated steps
            '''

            # Extract and replace
            result = extract_and_replace(
                existing,
                new_template,
                ["metadata.resourceVersion", "metadata.uid"]
            )
            # Returns new YAML with actual resourceVersion and uid
        """
        # Extract field values from existing YAML
        extracted_values = YamlFieldExtractor.get_multiple_fields(existing_yaml, field_paths)

        if not extracted_values:
            logger.warning("No fields were extracted from existing YAML")
            return new_yaml_template

        # Replace placeholders in new YAML
        result = YamlFieldExtractor.replace_placeholders(new_yaml_template, extracted_values)

        logger.info(f"Extracted and replaced {len(extracted_values)} fields")
        return result
