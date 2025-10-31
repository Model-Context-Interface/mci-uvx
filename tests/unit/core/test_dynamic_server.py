"""
Unit tests for dynamic_server.py - Dynamic MCP server creation from MCI schemas.

Tests the DynamicMCPServer class and run_server function for creating
MCP servers that dynamically load tools from MCI schema files.
"""

import json
import tempfile
from pathlib import Path

import pytest

from mci.core.dynamic_server import DynamicMCPServer


def create_test_schema(schema_dict: dict) -> str:
    """Helper to create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema_dict, f)
        return f.name


@pytest.mark.asyncio
async def test_create_server_from_schema():
    """
    Test creating an MCP server from an MCI schema file.

    Verifies that DynamicMCPServer can load a schema and create a
    properly configured ServerInstance.
    """
    schema = {
        "schemaVersion": "1.0",
        "metadata": {"name": "Test Schema"},
        "tools": [
            {
                "name": "test_tool",
                "description": "A test tool",
                "execution": {"type": "text", "text": "Test output"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        server = DynamicMCPServer(schema_path)
        instance = await server.create_from_mci_schema("test-server", "1.0.0")

        # Verify server was created
        assert instance is not None
        assert server.server is not None
        assert server.instance is not None
        assert server.mci_client_wrapper is not None

        # Verify server has correct name
        assert server.server.name == "test-server"

        # Verify tools are registered
        assert server.get_tool_count() == 1

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_load_tools_via_mciclient():
    """
    Test that tools are loaded using MCIClient.

    Verifies that the server uses MCIClient to load tools from the schema,
    ensuring all MCI features (toolsets, env vars) are supported.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "tool1", "execution": {"type": "text", "text": "T1"}},
            {"name": "tool2", "execution": {"type": "text", "text": "T2"}},
            {"name": "tool3", "execution": {"type": "text", "text": "T3"}},
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        server = DynamicMCPServer(schema_path)
        await server.create_from_mci_schema()

        # Verify MCIClient wrapper was created
        assert server.mci_client_wrapper is not None

        # Verify tools were loaded
        tools = server.mci_client_wrapper.get_tools()
        assert len(tools) == 3
        assert [t.name for t in tools] == ["tool1", "tool2", "tool3"]

        # Verify all tools are registered
        assert server.get_tool_count() == 3

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_convert_tools_to_mcp():
    """
    Test that MCI tools are converted to MCP format.

    Verifies that the server uses the Stage 8 converter to properly
    convert MCI tools to MCP Tool format.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "greet",
                "description": "Greet a user",
                "inputSchema": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
                "execution": {"type": "text", "text": "Hello, {{props.name}}!"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        server = DynamicMCPServer(schema_path)
        await server.create_from_mci_schema()

        # Get registered MCP tools
        assert server.server is not None
        mcp_tools = server.server._mci_tools  # type: ignore[attr-defined]

        # Verify tool was converted to MCP format
        assert len(mcp_tools) == 1
        mcp_tool = mcp_tools[0]

        assert mcp_tool.name == "greet"
        assert mcp_tool.description == "Greet a user"
        assert mcp_tool.inputSchema["type"] == "object"
        assert "name" in mcp_tool.inputSchema["properties"]
        assert mcp_tool.inputSchema["required"] == ["name"]

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_handle_execution_uses_mci():
    """
    Test that tool execution delegates to MCIClient.

    Verifies that the ServerInstance delegates tool execution to
    MCIClient.execute() rather than implementing its own execution logic.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "echo",
                "description": "Echo a message",
                "inputSchema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                },
                "execution": {"type": "text", "text": "Echo: {{props.message}}"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        server = DynamicMCPServer(schema_path)
        instance = await server.create_from_mci_schema()

        # Execute a tool using the instance
        result = await instance.handle_tool_call("echo", {"message": "Hello World"})

        # Verify result is returned in MCP format (list of TextContent)
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].type == "text"
        assert "Echo: Hello World" in result[0].text

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_with_filter():
    """
    Test creating a server with tool filtering.

    Verifies that the server supports filtering tools using the
    filter specification format.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "api_read",
                "tags": ["api", "read"],
                "execution": {"type": "text", "text": "Reading..."},
            },
            {
                "name": "api_write",
                "tags": ["api", "write"],
                "execution": {"type": "text", "text": "Writing..."},
            },
            {
                "name": "db_query",
                "tags": ["database"],
                "execution": {"type": "text", "text": "Querying..."},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        # Create server with filter for API tools only
        server = DynamicMCPServer(schema_path, filter_spec="tags:api")
        await server.create_from_mci_schema()

        # Verify only API tools are registered
        assert server.get_tool_count() == 2

        mcp_tools = server.server._mci_tools  # type: ignore[attr-defined]
        tool_names = [t.name for t in mcp_tools]
        assert "api_read" in tool_names
        assert "api_write" in tool_names
        assert "db_query" not in tool_names

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_with_only_filter():
    """Test server with 'only' filter type."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "tool1", "execution": {"type": "text", "text": "T1"}},
            {"name": "tool2", "execution": {"type": "text", "text": "T2"}},
            {"name": "tool3", "execution": {"type": "text", "text": "T3"}},
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        server = DynamicMCPServer(schema_path, filter_spec="only:tool1,tool3")
        await server.create_from_mci_schema()

        assert server.get_tool_count() == 2
        mcp_tools = server.server._mci_tools  # type: ignore[attr-defined]
        tool_names = [t.name for t in mcp_tools]
        assert "tool1" in tool_names
        assert "tool3" in tool_names
        assert "tool2" not in tool_names

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_with_except_filter():
    """Test server with 'except' filter type."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "tool1", "execution": {"type": "text", "text": "T1"}},
            {"name": "tool2", "execution": {"type": "text", "text": "T2"}},
            {"name": "tool3", "execution": {"type": "text", "text": "T3"}},
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        server = DynamicMCPServer(schema_path, filter_spec="except:tool2")
        await server.create_from_mci_schema()

        assert server.get_tool_count() == 2
        mcp_tools = server.server._mci_tools  # type: ignore[attr-defined]
        tool_names = [t.name for t in mcp_tools]
        assert "tool1" in tool_names
        assert "tool3" in tool_names
        assert "tool2" not in tool_names

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_preserves_metadata():
    """
    Test that server preserves all tool metadata.

    Verifies that descriptions, input schemas, and other metadata
    are correctly preserved through the conversion process.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "complex_tool",
                "description": "A complex tool",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "age": {"type": "number"},
                            },
                        }
                    },
                },
                "execution": {"type": "text", "text": "Complex output"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        server = DynamicMCPServer(schema_path)
        await server.create_from_mci_schema()

        mcp_tool = server.server._mci_tools[0]  # type: ignore[attr-defined]

        # Verify metadata is preserved
        assert mcp_tool.name == "complex_tool"
        assert mcp_tool.description == "A complex tool"
        assert "user" in mcp_tool.inputSchema["properties"]
        assert "name" in mcp_tool.inputSchema["properties"]["user"]["properties"]

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_get_tool_count_before_creation():
    """Test that get_tool_count returns 0 before server is created."""
    server = DynamicMCPServer("nonexistent.json")
    assert server.get_tool_count() == 0


@pytest.mark.asyncio
async def test_start_stdio_before_creation_raises_error():
    """Test that start_stdio raises error if server not created."""
    server = DynamicMCPServer("nonexistent.json")

    with pytest.raises(RuntimeError, match="Server instance not created"):
        await server.start_stdio()
