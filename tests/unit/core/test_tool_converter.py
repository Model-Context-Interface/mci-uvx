"""
Unit tests for MCIToolConverter class.

Tests the conversion of MCI tool definitions to MCP tool format,
ensuring proper schema conversion and metadata preservation.
"""

import mcp.types as types
from mcipy.models import Annotations, Tool

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


# Annotations tests


def test_convert_tool_with_annotations():
    """Test converting a tool with annotations to MCP format."""
    mci_tool = Tool(
        name="annotated_tool",
        description="Tool with annotations",
        execution={"type": "text", "text": "Test"},
        annotations=Annotations(
            title="Annotated Tool",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    # Verify annotations are transferred
    assert mcp_tool.annotations is not None
    assert isinstance(mcp_tool.annotations, types.ToolAnnotations)
    assert mcp_tool.annotations.title == "Annotated Tool"
    assert mcp_tool.annotations.readOnlyHint is True
    assert mcp_tool.annotations.destructiveHint is False
    assert mcp_tool.annotations.idempotentHint is True
    assert mcp_tool.annotations.openWorldHint is False


def test_convert_tool_with_partial_annotations():
    """Test converting a tool with partial annotations (only some fields set)."""
    mci_tool = Tool(
        name="partial_annotated_tool",
        description="Tool with partial annotations",
        execution={"type": "text", "text": "Test"},
        annotations=Annotations(title="My Tool", destructiveHint=True),
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    # Verify annotations are transferred with None for unset fields
    assert mcp_tool.annotations is not None
    assert mcp_tool.annotations.title == "My Tool"
    assert mcp_tool.annotations.destructiveHint is True
    assert mcp_tool.annotations.readOnlyHint is None
    assert mcp_tool.annotations.idempotentHint is None
    assert mcp_tool.annotations.openWorldHint is None


def test_convert_tool_without_annotations():
    """Test converting a tool without annotations returns None for annotations field."""
    mci_tool = Tool(
        name="no_annotations_tool",
        description="Tool without annotations",
        execution={"type": "text", "text": "Test"},
        annotations=None,
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    # Should have None for annotations
    assert mcp_tool.annotations is None


def test_convert_annotations_with_title_only():
    """Test converting annotations with only title field set."""
    mci_annotations = Annotations(title="Test Title")

    mcp_annotations = MCIToolConverter.convert_annotations(mci_annotations)

    assert mcp_annotations is not None
    assert mcp_annotations.title == "Test Title"
    assert mcp_annotations.readOnlyHint is None
    assert mcp_annotations.destructiveHint is None
    assert mcp_annotations.idempotentHint is None
    assert mcp_annotations.openWorldHint is None


def test_convert_annotations_with_all_fields():
    """Test converting annotations with all fields set."""
    mci_annotations = Annotations(
        title="Complete Tool",
        readOnlyHint=False,
        destructiveHint=True,
        idempotentHint=False,
        openWorldHint=True,
    )

    mcp_annotations = MCIToolConverter.convert_annotations(mci_annotations)

    assert mcp_annotations is not None
    assert mcp_annotations.title == "Complete Tool"
    assert mcp_annotations.readOnlyHint is False
    assert mcp_annotations.destructiveHint is True
    assert mcp_annotations.idempotentHint is False
    assert mcp_annotations.openWorldHint is True


def test_convert_none_annotations():
    """Test converting None annotations returns None."""
    mcp_annotations = MCIToolConverter.convert_annotations(None)

    assert mcp_annotations is None


def test_annotations_preserved_in_mcp_tool_object():
    """Test that annotations are properly preserved in the MCP Tool object structure."""
    mci_tool = Tool(
        name="delete_resource",
        description="Delete a resource from the remote server",
        execution={"type": "text", "text": "Deleted"},
        annotations=Annotations(
            title="Delete Resource",
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        ),
    )

    converter = MCIToolConverter()
    mcp_tool = converter.convert_to_mcp_tool(mci_tool)

    # Verify all properties match the example from the issue
    assert mcp_tool.name == "delete_resource"
    assert mcp_tool.description == "Delete a resource from the remote server"
    assert mcp_tool.annotations is not None
    assert mcp_tool.annotations.title == "Delete Resource"
    assert mcp_tool.annotations.readOnlyHint is False
    assert mcp_tool.annotations.destructiveHint is True
    assert mcp_tool.annotations.idempotentHint is False
    assert mcp_tool.annotations.openWorldHint is True
