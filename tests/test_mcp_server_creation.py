"""
Feature test for MCP server creation workflow.

Tests the complete workflow of creating an MCP server from MCI tools,
including loading MCI schema, converting tools, registering them,
and setting up handlers.
"""

import json
import tempfile
from pathlib import Path

import pytest
from mcipy import MCIClient

from mci.core.mcp_server import MCPServerBuilder, ServerInstance


def create_test_schema(schema_dict: dict) -> str:
    """Helper to create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema_dict, f)
        return f.name


@pytest.mark.asyncio
async def test_full_server_creation_workflow():
    """
    Test the complete workflow of creating an MCP server from MCI schema.

    This test covers:
    1. Loading MCI schema via MCIClient
    2. Creating MCP server with MCPServerBuilder
    3. Registering all tools from MCI schema
    4. Verifying tools are converted to MCP format
    5. Creating ServerInstance for runtime management
    """
    # Step 1: Create a comprehensive MCI schema
    schema = {
        "schemaVersion": "1.0",
        "metadata": {"name": "Test Schema", "description": "Testing MCP server creation"},
        "tools": [
            {
                "name": "greet_user",
                "description": "Greets a user by name",
                "inputSchema": {
                    "type": "object",
                    "properties": {"name": {"type": "string", "description": "User's name"}},
                    "required": ["name"],
                },
                "execution": {"type": "text", "text": "Hello, {{props.name}}!"},
            },
            {
                "name": "get_weather",
                "description": "Gets weather for a city",
                "inputSchema": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
                "execution": {"type": "text", "text": "Weather in {{props.city}}"},
            },
            {
                "name": "simple_tool",
                "description": "A simple tool with no inputs",
                "execution": {"type": "text", "text": "Simple output"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        # Step 2: Load MCI schema using MCIClient
        mci_client = MCIClient(schema_file_path=schema_path)
        tools = mci_client.tools()

        assert len(tools) == 3
        assert tools[0].name == "greet_user"
        assert tools[1].name == "get_weather"
        assert tools[2].name == "simple_tool"

        # Step 3: Create MCP server
        builder = MCPServerBuilder(mci_client)
        server = await builder.create_server("test-mci-server", "1.0.0")

        assert server is not None
        assert server.name == "test-mci-server"

        # Step 4: Register all tools
        await builder.register_all_tools(server, tools)

        # Verify all tools are registered
        assert hasattr(server, "_mci_tools")
        assert len(server._mci_tools) == 3  # type: ignore

        # Step 5: Verify tools are properly converted to MCP format
        mcp_tools = server._mci_tools  # type: ignore

        # Check first tool (greet_user)
        assert mcp_tools[0].name == "greet_user"
        assert mcp_tools[0].description == "Greets a user by name"
        assert mcp_tools[0].inputSchema["type"] == "object"
        assert "name" in mcp_tools[0].inputSchema["properties"]

        # Check second tool (get_weather)
        assert mcp_tools[1].name == "get_weather"
        assert mcp_tools[1].description == "Gets weather for a city"
        assert "city" in mcp_tools[1].inputSchema["properties"]

        # Check third tool (simple_tool)
        assert mcp_tools[2].name == "simple_tool"
        assert mcp_tools[2].description == "A simple tool with no inputs"

        # Step 6: Create ServerInstance
        instance = ServerInstance(server, mci_client)

        assert instance is not None
        assert instance.mci_client is mci_client
        assert instance.server is server
        assert instance._running is False

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_with_filtered_tools():
    """
    Test creating an MCP server with filtered MCI tools.

    This tests that the server can be created with a subset of tools
    from the MCI schema, using MCIClient's filtering capabilities.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "api_read",
                "description": "Read from API",
                "tags": ["api", "read"],
                "execution": {"type": "text", "text": "Reading..."},
            },
            {
                "name": "api_write",
                "description": "Write to API",
                "tags": ["api", "write"],
                "execution": {"type": "text", "text": "Writing..."},
            },
            {
                "name": "db_query",
                "description": "Query database",
                "tags": ["database"],
                "execution": {"type": "text", "text": "Querying..."},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        # Load schema and filter for only API tools
        mci_client = MCIClient(schema_file_path=schema_path)
        api_tools = mci_client.tags(["api"])

        assert len(api_tools) == 2
        assert all("api" in tool.tags for tool in api_tools)

        # Create server with filtered tools
        builder = MCPServerBuilder(mci_client)
        server = await builder.create_server("api-server")

        await builder.register_all_tools(server, api_tools)

        # Verify only API tools are registered
        assert len(server._mci_tools) == 2  # type: ignore
        tool_names = [t.name for t in server._mci_tools]  # type: ignore
        assert "api_read" in tool_names
        assert "api_write" in tool_names
        assert "db_query" not in tool_names

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_preserves_tool_metadata():
    """
    Test that all tool metadata is preserved through the conversion process.

    Verifies that descriptions, input schemas, and other metadata from
    MCI tools are correctly preserved in the MCP server.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "complex_tool",
                "description": "A tool with complex metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "age": {"type": "number"},
                            },
                            "required": ["name"],
                        },
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["user"],
                },
                "execution": {"type": "text", "text": "Complex output"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        tools = mci_client.tools()

        builder = MCPServerBuilder(mci_client)
        server = await builder.create_server("metadata-server")

        await builder.register_all_tools(server, tools)

        mcp_tool = server._mci_tools[0]  # type: ignore

        # Verify all metadata is preserved
        assert mcp_tool.name == "complex_tool"
        assert mcp_tool.description == "A tool with complex metadata"

        # Verify complex schema structure is preserved
        assert mcp_tool.inputSchema["type"] == "object"
        assert "user" in mcp_tool.inputSchema["properties"]
        assert "options" in mcp_tool.inputSchema["properties"]

        user_schema = mcp_tool.inputSchema["properties"]["user"]
        assert user_schema["type"] == "object"
        assert "name" in user_schema["properties"]
        assert "age" in user_schema["properties"]

        assert mcp_tool.inputSchema["required"] == ["user"]

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_multiple_servers_from_same_client():
    """
    Test creating multiple MCP servers from the same MCIClient.

    Verifies that a single MCIClient can be used to create multiple
    independent server instances.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "tool1", "execution": {"type": "text", "text": "T1"}},
            {"name": "tool2", "execution": {"type": "text", "text": "T2"}},
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        # Create first server with all tools
        server1 = await builder.create_server("server1")
        all_tools = mci_client.tools()
        await builder.register_all_tools(server1, all_tools)

        # Create second server with subset of tools
        server2 = await builder.create_server("server2")
        subset_tools = mci_client.only(["tool1"])
        await builder.register_all_tools(server2, subset_tools)

        # Verify servers are independent
        assert server1.name == "server1"
        assert server2.name == "server2"
        assert len(server1._mci_tools) == 2  # type: ignore
        assert len(server2._mci_tools) == 1  # type: ignore

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_preserves_annotations():
    """
    Test that tool annotations are preserved when creating MCP server.

    Verifies that annotations from MCI tools (title, readOnlyHint, destructiveHint,
    idempotentHint, openWorldHint) are correctly transferred to MCP tools in the server.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "delete_resource",
                "description": "Delete a resource from the remote server",
                "annotations": {
                    "title": "Delete Resource",
                    "readOnlyHint": False,
                    "destructiveHint": True,
                    "idempotentHint": False,
                    "openWorldHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                    "required": ["id"],
                },
                "execution": {"type": "text", "text": "Deleted resource {{props.id}}"},
            },
            {
                "name": "read_data",
                "description": "Read data from the server",
                "annotations": {
                    "title": "Read Data",
                    "readOnlyHint": True,
                },
                "execution": {"type": "text", "text": "Reading data..."},
            },
            {
                "name": "no_annotations",
                "description": "Tool without annotations",
                "execution": {"type": "text", "text": "No annotations"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        # Load schema and create server
        mci_client = MCIClient(schema_file_path=schema_path)
        tools = mci_client.tools()

        builder = MCPServerBuilder(mci_client)
        server = await builder.create_server("annotated-server")

        await builder.register_all_tools(server, tools)

        mcp_tools = server._mci_tools  # type: ignore

        # Verify annotations for delete_resource
        delete_tool = mcp_tools[0]
        assert delete_tool.name == "delete_resource"
        assert delete_tool.annotations is not None
        assert delete_tool.annotations.title == "Delete Resource"
        assert delete_tool.annotations.readOnlyHint is False
        assert delete_tool.annotations.destructiveHint is True
        assert delete_tool.annotations.idempotentHint is False
        assert delete_tool.annotations.openWorldHint is True

        # Verify annotations for read_data
        read_tool = mcp_tools[1]
        assert read_tool.name == "read_data"
        assert read_tool.annotations is not None
        assert read_tool.annotations.title == "Read Data"
        assert read_tool.annotations.readOnlyHint is True
        # Other fields should be None (not set in MCI)
        assert read_tool.annotations.destructiveHint is None
        assert read_tool.annotations.idempotentHint is None
        assert read_tool.annotations.openWorldHint is None

        # Verify no annotations for no_annotations tool
        no_ann_tool = mcp_tools[2]
        assert no_ann_tool.name == "no_annotations"
        assert no_ann_tool.annotations is None

    finally:
        Path(schema_path).unlink()
