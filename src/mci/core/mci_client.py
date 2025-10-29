"""
mci_client.py - CLI wrapper around MCIClient from mci-py

This module provides a CLI-friendly wrapper around the MCIClient class from mci-py.
It delegates all schema parsing, validation, tool loading, and filtering to MCIClient,
while providing CLI-specific error handling and output formatting.
"""

from mcipy import MCIClient
from mcipy.models import Tool


class MCIClientWrapper:
    """
    CLI wrapper around MCIClient from mci-py.

    This class provides a CLI-friendly interface to MCIClient, delegating all
    tool loading, filtering, and schema operations to the upstream mci-py library.
    It focuses on error handling and formatting for CLI usability.
    """

    def __init__(self, file_path: str, env_vars: dict[str, str] | None = None):
        """
        Initialize the wrapper with an MCIClient instance.

        Args:
            file_path: Path to the MCI schema file (.json, .yaml, or .yml)
            env_vars: Optional environment variables for template substitution

        Raises:
            MCIClientError: If the schema file cannot be loaded or parsed
        """
        self._client: MCIClient = MCIClient(schema_file_path=file_path, env_vars=env_vars or {})
        self._file_path: str = file_path

    @property
    def client(self) -> MCIClient:
        """Get the underlying MCIClient instance."""
        return self._client

    def get_tools(self) -> list[Tool]:
        """
        Get all available tools from the loaded schema.

        Returns:
            List of Tool objects from the schema

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> tools = wrapper.get_tools()
            >>> print([t.name for t in tools])
        """
        return self._client.tools()

    def filter_only(self, tool_names: list[str]) -> list[Tool]:
        """
        Filter tools to include only specified tools by name.

        This method delegates to MCIClient.only() to perform filtering.

        Args:
            tool_names: List of tool names to include

        Returns:
            Filtered list of Tool objects matching the specified names

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> tools = wrapper.filter_only(["get_weather", "get_forecast"])
            >>> print([t.name for t in tools])
        """
        return self._client.only(tool_names)

    def filter_except(self, tool_names: list[str]) -> list[Tool]:
        """
        Filter tools to exclude specified tools by name.

        This method delegates to MCIClient.without() to perform filtering.

        Args:
            tool_names: List of tool names to exclude

        Returns:
            Filtered list of Tool objects excluding the specified names

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> tools = wrapper.filter_except(["delete_data", "admin_tools"])
            >>> print([t.name for t in tools])
        """
        return self._client.without(tool_names)

    def filter_tags(self, tags: list[str]) -> list[Tool]:
        """
        Filter tools to include only those with at least one matching tag.

        This method delegates to MCIClient.tags() to perform filtering.

        Args:
            tags: List of tags to filter by (OR logic - tool must have at least one matching tag)

        Returns:
            Filtered list of Tool objects that have at least one of the specified tags

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> tools = wrapper.filter_tags(["api", "database"])
            >>> print([t.name for t in tools])
        """
        return self._client.tags(tags)

    def filter_without_tags(self, tags: list[str]) -> list[Tool]:
        """
        Filter tools to exclude those with any matching tag.

        This method delegates to MCIClient.withoutTags() to perform filtering.

        Args:
            tags: List of tags to exclude (OR logic - tool is excluded if it has any matching tag)

        Returns:
            Filtered list of Tool objects that do NOT have any of the specified tags

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> tools = wrapper.filter_without_tags(["external", "deprecated"])
            >>> print([t.name for t in tools])
        """
        return self._client.withoutTags(tags)

    def filter_toolsets(self, toolset_names: list[str]) -> list[Tool]:
        """
        Filter tools to include only those from specified toolsets.

        This method delegates to MCIClient.toolsets() to perform filtering.

        Args:
            toolset_names: List of toolset names to include

        Returns:
            Filtered list of Tool objects from the specified toolsets

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> tools = wrapper.filter_toolsets(["weather", "database"])
            >>> print([t.name for t in tools])
        """
        return self._client.toolsets(toolset_names)

    def list_tool_names(self) -> list[str]:
        """
        List available tool names as strings.

        Returns:
            List of tool names (strings)

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> names = wrapper.list_tool_names()
            >>> print(names)
        """
        return self._client.list_tools()
