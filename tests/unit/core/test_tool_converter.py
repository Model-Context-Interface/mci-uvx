"""
Unit tests for MCIToolConverter class.

Tests the conversion of MCI tool definitions to MCP tool format,
ensuring proper schema conversion and metadata preservation.
"""

import mcp.types as types
from mcipy.models import Tool

from mci.core.tool_converter import MCIToolConverter


def test_convert_mci_to_mcp_tool():
    """Test converting a basic MCI tool to MCP Tool format."""
    # Create a simple MCI tool
    mci_tool = Tool(
        name="test_tool",
        description="A test tool",
        execution={"type": "text", "text": "Hello World"},
        inputSchema={"type": "object", "properties": {"name": {"type": "string"}}},
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    # Verify the conversion
    assert isinstance(mcp_tool, types.Tool)
    assert mcp_tool.name == "test_tool"
    assert mcp_tool.description == "A test tool"
    assert mcp_tool.inputSchema["type"] == "object"
    assert "properties" in mcp_tool.inputSchema


def test_convert_tool_without_description():
    """Test converting a tool with no description."""
    mci_tool = Tool(
        name="no_desc_tool", execution={"type": "text", "text": "Test"}, description=None
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    assert mcp_tool.name == "no_desc_tool"
    assert mcp_tool.description == ""  # Should default to empty string


def test_convert_tool_without_input_schema():
    """Test converting a tool with no inputSchema."""
    mci_tool = Tool(
        name="no_schema_tool",
        description="Tool without schema",
        execution={"type": "text", "text": "Test"},
        inputSchema=None,
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    assert mcp_tool.name == "no_schema_tool"
    # Should have a minimal valid schema
    assert mcp_tool.inputSchema["type"] == "object"
    assert "properties" in mcp_tool.inputSchema


def test_convert_input_schema():
    """Test converting inputSchema to MCP format."""
    schema = {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
    }

    converter = MCIToolConverter()
    mcp_schema = converter.convert_input_schema(schema)

    assert mcp_schema["type"] == "object"
    assert "properties" in mcp_schema
    assert "city" in mcp_schema["properties"]
    assert mcp_schema["required"] == ["city"]


def test_convert_empty_input_schema():
    """Test converting an empty inputSchema."""
    converter = MCIToolConverter()
    mcp_schema = converter.convert_input_schema({})

    # Should provide minimal valid schema
    assert mcp_schema["type"] == "object"
    assert "properties" in mcp_schema


def test_convert_schema_without_type():
    """Test converting a schema that's missing the type field."""
    schema = {"properties": {"name": {"type": "string"}}}

    converter = MCIToolConverter()
    mcp_schema = converter.convert_input_schema(schema)

    # Should add type field
    assert mcp_schema["type"] == "object"
    assert "properties" in mcp_schema


def test_preserve_tool_description():
    """Test that tool description is preserved during conversion."""
    description = "This is a detailed description of the tool's functionality"
    mci_tool = Tool(
        name="detailed_tool",
        description=description,
        execution={"type": "text", "text": "Output"},
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    assert mcp_tool.description == description


def test_convert_complex_input_schema():
    """Test converting a complex nested inputSchema."""
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                    "active": {"type": "boolean"},
                },
                "required": ["name"],
            },
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["user"],
    }

    converter = MCIToolConverter()
    mcp_schema = converter.convert_input_schema(schema)

    assert mcp_schema["type"] == "object"
    assert "user" in mcp_schema["properties"]
    assert "tags" in mcp_schema["properties"]
    assert mcp_schema["properties"]["user"]["type"] == "object"
    assert mcp_schema["properties"]["tags"]["type"] == "array"


def test_converter_is_stateless():
    """Test that the converter can be used multiple times without state issues."""
    converter = MCIToolConverter()

    tool1 = Tool(name="tool1", execution={"type": "text", "text": "T1"})
    tool2 = Tool(name="tool2", execution={"type": "text", "text": "T2"})

    mcp_tool1 = converter.convert_to_mcp_tool(tool1)
    mcp_tool2 = converter.convert_to_mcp_tool(tool2)

    # Each conversion should be independent
    assert mcp_tool1.name == "tool1"
    assert mcp_tool2.name == "tool2"
    assert mcp_tool1.name != mcp_tool2.name


def test_static_methods_work_without_instance():
    """Test that static methods can be called without instantiating the class."""
    schema = {"type": "object", "properties": {"key": {"type": "string"}}}

    # Call static method directly on class
    mcp_schema = MCIToolConverter.convert_input_schema(schema)

    assert mcp_schema["type"] == "object"
