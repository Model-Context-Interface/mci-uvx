"""
tool_converter.py - Convert MCI tools to MCP tool format

This module provides functionality to convert MCI tool definitions (from mci-py)
to MCP tool format compatible with the MCP protocol. It handles schema conversion,
metadata preservation, and ensures proper formatting for MCP servers.
"""

from typing import Any

import mcp.types as types
from mcipy.models import Tool


class MCIToolConverter:
    """
    Converter for translating MCI tool definitions to MCP tool format.

    This class handles the conversion of tool metadata, descriptions, and JSON schemas
    from the MCI format (used by mci-py) to the MCP format required by MCP servers.
    """

    @staticmethod
    def convert_to_mcp_tool(mci_tool: Tool) -> types.Tool:
        """
        Convert an MCI Tool to MCP Tool format.

        Takes a Tool object from mci-py and converts it to the types.Tool format
        expected by the MCP protocol. This includes converting the input schema,
        preserving all metadata, and transferring annotations.

        Args:
            mci_tool: Tool object from mci-py (Pydantic model)

        Returns:
            types.Tool object compatible with MCP protocol

        Example:
            >>> converter = MCIToolConverter()
            >>> mcp_tool = converter.convert_to_mcp_tool(mci_tool)
            >>> print(mcp_tool.name, mcp_tool.description)
        """
        # Convert inputSchema to MCP format (JSON Schema)
        input_schema = MCIToolConverter.convert_input_schema(mci_tool.inputSchema or {})

        # Convert annotations to MCP format
        annotations = MCIToolConverter.convert_annotations(mci_tool.annotations)

        # Create MCP Tool with converted schema and annotations
        return types.Tool(
            name=mci_tool.name,
            description=mci_tool.description or "",
            inputSchema=input_schema,
            annotations=annotations,
        )

    @staticmethod
    def convert_input_schema(mci_schema: dict[str, Any]) -> dict[str, Any]:
        """
        Convert MCI inputSchema to MCP-compatible JSON Schema format.

        MCI and MCP both use JSON Schema for input validation, but this method
        ensures the schema is in the exact format expected by MCP servers.
        Currently, both formats are compatible, so this is mostly a pass-through
        with validation.

        Args:
            mci_schema: Input schema dictionary from MCI tool definition

        Returns:
            JSON Schema dictionary compatible with MCP protocol

        Example:
            >>> schema = {"type": "object", "properties": {"name": {"type": "string"}}}
            >>> mcp_schema = MCIToolConverter.convert_input_schema(schema)
        """
        # Both MCI and MCP use JSON Schema, so we can pass through
        # If the schema is empty, provide a minimal valid schema
        if not mci_schema:
            return {"type": "object", "properties": {}}

        # Ensure the schema has at minimum a type field
        if "type" not in mci_schema:
            return {"type": "object", "properties": mci_schema}

        return mci_schema

    @staticmethod
    def convert_annotations(mci_annotations: Any) -> types.ToolAnnotations | None:
        """
        Convert MCI Annotations to MCP ToolAnnotations format.

        Transfers annotation fields from MCI tool annotations to the MCP format,
        including title, readOnlyHint, destructiveHint, idempotentHint, and openWorldHint.

        Args:
            mci_annotations: Annotations object from MCI tool definition (or None)

        Returns:
            ToolAnnotations object compatible with MCP protocol, or None if no annotations

        Example:
            >>> from mcipy.models import Annotations
            >>> mci_ann = Annotations(title="My Tool", readOnlyHint=True)
            >>> mcp_ann = MCIToolConverter.convert_annotations(mci_ann)
            >>> print(mcp_ann.title, mcp_ann.readOnlyHint)
        """
        if mci_annotations is None:
            return None

        # Convert MCI Annotations to MCP ToolAnnotations
        # Both models have the same field structure, so we can extract and transfer
        return types.ToolAnnotations(
            title=mci_annotations.title,
            readOnlyHint=mci_annotations.readOnlyHint,
            destructiveHint=mci_annotations.destructiveHint,
            idempotentHint=mci_annotations.idempotentHint,
            openWorldHint=mci_annotations.openWorldHint,
        )
