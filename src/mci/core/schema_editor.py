"""
schema_editor.py - Schema file editing logic

This module provides functionality to programmatically edit MCI schema files,
including adding toolset references with optional filters while preserving
the original file format (JSON or YAML).
"""

import json
from pathlib import Path
from typing import Any

import yaml

from mci.core.file_finder import MCIFileFinder


class SchemaEditor:
    """
    Edits MCI schema files while preserving format and structure.

    This class provides methods to load, modify, and save MCI schema files,
    ensuring that the original file format (JSON or YAML) is preserved.
    It supports adding toolset references with optional filters.
    """

    def __init__(self):
        """Initialize the SchemaEditor with empty state."""
        # Stores the loaded schema dictionary
        self.schema_data: dict[str, Any] | None = None
        # Stores the detected file format ('json' or 'yaml')
        self.file_format: str | None = None
        # Stores the path of the loaded schema file
        self.file_path: str | None = None

    def load_schema(self, file_path: str) -> dict[str, Any]:
        """
        Load an MCI schema file into memory.

        Args:
            file_path: Path to the MCI schema file (.json, .yaml, or .yml)

        Returns:
            The loaded schema data as a dictionary

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is unsupported
            Exception: If the file cannot be parsed

        Example:
            >>> editor = SchemaEditor()
            >>> schema = editor.load_schema("mci.json")
            >>> print(schema.get("schemaVersion"))
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {file_path}")

        # Detect file format
        file_finder = MCIFileFinder()
        self.file_format = file_finder.get_file_format(str(path))

        if self.file_format is None:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Load the file
        with open(path) as f:
            if self.file_format == "json":
                self.schema_data = json.load(f)
            elif self.file_format == "yaml":
                loaded_data = yaml.safe_load(f)
                if loaded_data is None:
                    raise ValueError(f"YAML file is empty or invalid: {file_path}")
                self.schema_data = loaded_data
            else:
                raise ValueError(f"Unsupported file format: {self.file_format}")

        self.file_path = str(path)

        # Type narrowing: at this point schema_data is guaranteed to be a dict
        assert self.schema_data is not None
        return self.schema_data

    def add_toolset(
        self, toolset_name: str, filter_type: str | None = None, filter_value: str | None = None
    ) -> None:
        """
        Add a toolset reference to the schema.

        This method adds a toolset to the schema's toolsets array. If the toolset
        already exists, it will be updated with the new filter (if provided).

        Args:
            toolset_name: Name of the toolset to add
            filter_type: Optional filter type (only, except, tags, withoutTags)
            filter_value: Optional comma-separated filter values

        Raises:
            ValueError: If schema hasn't been loaded yet
            ValueError: If filter_type is provided without filter_value or vice versa

        Example:
            >>> editor = SchemaEditor()
            >>> editor.load_schema("mci.json")
            >>> editor.add_toolset("weather-tools")
            >>> editor.add_toolset("analytics", "only", "Tool1,Tool2")
            >>> editor.save_schema("mci.json")
        """
        if self.schema_data is None:
            raise ValueError("No schema loaded. Call load_schema() first.")

        # Validate filter arguments
        if (filter_type is None) != (filter_value is None):
            raise ValueError("filter_type and filter_value must both be provided or both be None")

        # Ensure toolsets array exists
        if "toolsets" not in self.schema_data:
            self.schema_data["toolsets"] = []

        toolsets = self.schema_data["toolsets"]

        # Check if toolset already exists
        existing_index = None
        for i, toolset in enumerate(toolsets):
            # Toolsets can be strings or objects
            if isinstance(toolset, str) and toolset == toolset_name:
                existing_index = i
                break
            elif isinstance(toolset, dict) and toolset.get("name") == toolset_name:
                existing_index = i
                break

        # Prepare the toolset entry
        if filter_type and filter_value:
            toolset_entry = {
                "name": toolset_name,
                "filter": filter_type,
                "filterValue": filter_value,
            }
        else:
            toolset_entry = toolset_name

        # Add or update the toolset
        if existing_index is not None:
            toolsets[existing_index] = toolset_entry
        else:
            toolsets.append(toolset_entry)

    def save_schema(self, file_path: str | None = None) -> None:
        """
        Save the schema back to a file, preserving the original format.

        Args:
            file_path: Optional path to save to. If None, uses the path from load_schema()

        Raises:
            ValueError: If no schema is loaded
            ValueError: If file_path is None and no file was previously loaded
            ValueError: If file format cannot be determined

        Example:
            >>> editor = SchemaEditor()
            >>> editor.load_schema("mci.json")
            >>> editor.add_toolset("weather-tools")
            >>> editor.save_schema()  # Saves to mci.json
        """
        if self.schema_data is None:
            raise ValueError("No schema loaded. Call load_schema() first.")

        # Determine the save path
        save_path = file_path if file_path is not None else self.file_path

        if save_path is None:
            raise ValueError("No file path specified and no file was previously loaded")

        # Determine format if saving to a new path
        if file_path is not None:
            file_finder = MCIFileFinder()
            save_format = file_finder.get_file_format(file_path)
            if save_format is None:
                raise ValueError(f"Cannot determine format for file: {file_path}")
        else:
            save_format = self.file_format

        if save_format is None:
            raise ValueError("Cannot determine file format for saving")

        # Write the file
        path = Path(save_path)
        with open(path, "w") as f:
            if save_format == "json":
                json.dump(self.schema_data, f, indent=2)
                # Add newline at end of file for consistency
                f.write("\n")
            elif save_format == "yaml":
                yaml.safe_dump(
                    self.schema_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            else:
                raise ValueError(f"Unsupported save format: {save_format}")

    def preserve_format(self) -> str:
        """
        Get the format of the loaded schema file.

        Returns:
            The file format ("json" or "yaml")

        Raises:
            ValueError: If no schema has been loaded

        Example:
            >>> editor = SchemaEditor()
            >>> editor.load_schema("mci.json")
            >>> print(editor.preserve_format())  # Output: "json"
        """
        if self.file_format is None:
            raise ValueError("No schema loaded. Call load_schema() first.")
        return self.file_format


def parse_add_filter(filter_spec: str) -> tuple[str, str]:
    """
    Parse a filter specification string for the add command.

    Filter specifications follow the format:
    - "only:tool1,tool2,tool3" - Include only specified tools
    - "except:tool1,tool2" - Exclude specified tools
    - "tags:tag1,tag2" - Include tools with any of these tags
    - "withoutTags:tag1,tag2" - Exclude tools with any of these tags

    Args:
        filter_spec: Filter specification string (e.g., "tags:api,database")

    Returns:
        Tuple of (filter_type, filter_value) where:
        - filter_type is one of: "only", "except", "tags", "withoutTags"
        - filter_value is the comma-separated list of values

    Raises:
        ValueError: If filter specification is invalid or malformed

    Example:
        >>> filter_type, filter_value = parse_add_filter("tags:api,database")
        >>> print(filter_type, filter_value)
        ('tags', 'api,database')
    """
    if not filter_spec or ":" not in filter_spec:
        raise ValueError(
            f"Invalid filter specification: '{filter_spec}'. "
            "Expected format: 'type:value1,value2,...' "
            "where type is one of: only, except, tags, withoutTags"
        )

    parts = filter_spec.split(":", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid filter specification: '{filter_spec}'")

    filter_type = parts[0].strip()
    filter_value = parts[1].strip()

    # Validate filter type
    valid_types = ["only", "except", "tags", "withoutTags"]
    if filter_type not in valid_types:
        raise ValueError(
            f"Invalid filter type: '{filter_type}'. Valid types are: {', '.join(valid_types)}"
        )

    # Validate that we have values
    if not filter_value:
        raise ValueError(f"No values provided for filter type '{filter_type}'")

    # Validate that values are not empty after splitting
    values = [v.strip() for v in filter_value.split(",") if v.strip()]
    if not values:
        raise ValueError(f"No valid values found in filter specification: '{filter_spec}'")

    return (filter_type, filter_value)
