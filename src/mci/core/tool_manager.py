"""
tool_manager.py - Tool filtering and management logic

This module provides utilities for parsing filter specifications from the CLI
and applying them to tools using the MCIClient filtering methods.
"""

from mcipy.models import Tool

from mci.core.mci_client import MCIClientWrapper


class ToolManager:
    """
    Manages tool filtering based on CLI filter specifications.

    This class parses filter specifications from command-line arguments
    and applies them using MCIClient's built-in filtering methods.
    """

    @staticmethod
    def parse_filter_spec(filter_spec: str) -> tuple[str, list[str]]:
        """
        Parse a filter specification string into filter type and values.

        Filter specifications follow the format:
        - "only:tool1,tool2,tool3" - Include only specified tools
        - "except:tool1,tool2" - Exclude specified tools
        - "tags:tag1,tag2" - Include tools with any of these tags
        - "without-tags:tag1,tag2" - Exclude tools with any of these tags
        - "toolsets:toolset1,toolset2" - Include tools from specified toolsets

        Args:
            filter_spec: Filter specification string (e.g., "tags:api,database")

        Returns:
            Tuple of (filter_type, values) where:
            - filter_type is one of: "only", "except", "tags", "without-tags", "toolsets"
            - values is a list of filter values

        Raises:
            ValueError: If filter specification is invalid or malformed

        Example:
            >>> filter_type, values = ToolManager.parse_filter_spec("tags:api,database")
            >>> print(filter_type, values)
            ('tags', ['api', 'database'])
        """
        if not filter_spec or ":" not in filter_spec:
            raise ValueError(
                f"Invalid filter specification: '{filter_spec}'. "
                "Expected format: 'type:value1,value2,...' "
                "where type is one of: only, except, tags, without-tags, toolsets"
            )

        parts = filter_spec.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid filter specification: '{filter_spec}'")

        filter_type = parts[0].strip()
        values_str = parts[1].strip()

        # Validate filter type
        valid_types = ["only", "except", "tags", "without-tags", "toolsets"]
        if filter_type not in valid_types:
            raise ValueError(
                f"Invalid filter type: '{filter_type}'. Valid types are: {', '.join(valid_types)}"
            )

        # Parse comma-separated values
        if not values_str:
            raise ValueError(f"No values provided for filter type '{filter_type}'")

        values = [v.strip() for v in values_str.split(",") if v.strip()]
        if not values:
            raise ValueError(f"No valid values found in filter specification: '{filter_spec}'")

        return (filter_type, values)

    @staticmethod
    def apply_filter_spec(client: MCIClientWrapper, filter_spec: str) -> list[Tool]:
        """
        Apply a filter specification to get filtered tools.

        This method parses the filter specification and applies the appropriate
        MCIClient filtering method.

        Args:
            client: MCIClientWrapper instance to apply filters on
            filter_spec: Filter specification string (e.g., "tags:api,database")

        Returns:
            Filtered list of Tool objects

        Raises:
            ValueError: If filter specification is invalid

        Example:
            >>> wrapper = MCIClientWrapper("mci.json")
            >>> tools = ToolManager.apply_filter_spec(wrapper, "tags:api,database")
            >>> print([t.name for t in tools])
        """
        filter_type, values = ToolManager.parse_filter_spec(filter_spec)

        # Apply the appropriate filter based on type
        if filter_type == "only":
            return client.filter_only(values)
        elif filter_type == "except":
            return client.filter_except(values)
        elif filter_type == "tags":
            return client.filter_tags(values)
        elif filter_type == "without-tags":
            return client.filter_without_tags(values)
        elif filter_type == "toolsets":
            return client.filter_toolsets(values)
        else:
            # This shouldn't happen if parse_filter_spec validates correctly
            raise ValueError(f"Unsupported filter type: '{filter_type}'")
