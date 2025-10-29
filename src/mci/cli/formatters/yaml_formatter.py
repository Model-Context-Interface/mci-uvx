"""
yaml_formatter.py - YAML formatter for file output

This module provides formatting for outputting tools to YAML files
with metadata including timestamp, source file, filters, and tool count.
"""

from pathlib import Path

import yaml

from mcipy.models import Tool

from mci.utils.timestamp import generate_timestamp_filename, get_iso_timestamp


class YAMLFormatter:
    """
    Formats tool information as YAML files with metadata.

    This class provides methods to format tool lists into YAML files
    with timestamp, source file, filters applied, and total count.
    """

    @staticmethod
    def format_to_file(
        tools: list[Tool],
        mci_file: str,
        filters_applied: list[str] | None = None,
        verbose: bool = False,
    ) -> str:
        """
        Format tools to a YAML file and return the filename.

        Creates a timestamped YAML file with tool data and metadata.
        Filename format: tools_YYYYMMDD_HHMMSS.yaml

        Args:
            tools: List of Tool objects to format
            mci_file: Path to the source MCI file
            filters_applied: Optional list of filter specifications that were applied
            verbose: Whether to include verbose tool metadata

        Returns:
            The filename of the created YAML file

        Example:
            >>> formatter = YAMLFormatter()
            >>> filename = formatter.format_to_file(tools, "mci.json", ["tags:api"])
            >>> print(filename)
            tools_20241029_143022.yaml
        """
        # Generate timestamped filename
        filename = generate_timestamp_filename("yaml")

        # Build output data structure
        output_data = {
            "timestamp": get_iso_timestamp(),
            "mci_file": mci_file,
            "filters_applied": filters_applied or [],
            "total": len(tools),
            "tools": [],
        }

        # Format each tool
        for tool in tools:
            tool_data = {
                "name": tool.name,
                "source": tool.toolset_source or "main",
                "description": tool.description or "",
            }

            # Add verbose fields if requested
            if verbose:
                tool_data["tags"] = tool.tags
                tool_data["execution_type"] = (
                    tool.execution.type.value
                    if hasattr(tool.execution.type, "value")
                    else str(tool.execution.type)
                )

                if tool.inputSchema:
                    tool_data["inputSchema"] = tool.inputSchema

                if tool.disabled:
                    tool_data["disabled"] = tool.disabled

            output_data["tools"].append(tool_data)

        # Write to file
        with open(filename, "w") as f:
            yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)

        return filename
