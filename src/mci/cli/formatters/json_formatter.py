"""
json_formatter.py - JSON formatter for file output

This module provides formatting for outputting tools to JSON files
with metadata including timestamp, source file, filters, and tool count.
"""

import json
from typing import Any

from mcipy.models import Tool

from mci.utils.timestamp import generate_timestamp_filename, get_iso_timestamp


class JSONFormatter:
    """
    Formats tool information as JSON files with metadata.

    This class provides methods to format tool lists into JSON files
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
        Format tools to a JSON file and return the filename.

        Creates a timestamped JSON file with tool data and metadata.
        Filename format: tools_YYYYMMDD_HHMMSS.json

        Args:
            tools: List of Tool objects to format
            mci_file: Path to the source MCI file
            filters_applied: Optional list of filter specifications that were applied
            verbose: Whether to include verbose tool metadata

        Returns:
            The filename of the created JSON file

        Example:
            >>> formatter = JSONFormatter()
            >>> filename = formatter.format_to_file(tools, "mci.json", ["tags:api"])
            >>> print(filename)
            tools_20241029_143022.json
        """
        # Generate timestamped filename
        filename = generate_timestamp_filename("json")

        # Build output data structure
        output_data: dict[str, Any] = {
            "timestamp": get_iso_timestamp(),
            "mci_file": mci_file,
            "filters_applied": filters_applied or [],
            "total": len(tools),
            "tools": [],
        }

        # Format each tool
        for tool in tools:
            tool_data: dict[str, str | list[str] | dict[str, Any] | bool] = {
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
            json.dump(output_data, f, indent=2)

        return filename
