"""
Unit tests for MCPServerBuilder and ServerInstance classes.

Tests the creation and configuration of MCP servers, tool registration,
and basic server lifecycle management.
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
async def test_create_server():
    """Test creating an MCP server instance."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "test_tool", "execution": {"type": "text", "text": "Hello"}},
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("test-server", "1.0.0")

        assert server is not None
        assert server.name == "test-server"
        assert hasattr(server, "_mci_client")
        assert hasattr(server, "_mci_converter")
        assert hasattr(server, "_server_version")
        assert server._server_version == "1.0.0"  # type: ignore
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_create_server_with_default_version():
    """Test creating a server with default version."""
    schema = {"schemaVersion": "1.0", "tools": []}

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("my-server")

        assert server.name == "my-server"
        assert server._server_version == "1.0.0"  # type: ignore
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_register_single_tool():
    """Test registering a single tool with the server."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "single_tool",
                "description": "A single tool",
                "execution": {"type": "text", "text": "Output"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("test-server")

        # Get the tool from MCIClient
        tools = mci_client.tools()
        assert len(tools) == 1

        # Register the tool
        await builder.register_tool(server, tools[0])

        # Verify registration
        assert hasattr(server, "_mci_tools")
        assert len(server._mci_tools) == 1  # type: ignore
        assert server._mci_tools[0].name == "single_tool"  # type: ignore
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_register_multiple_tools():
    """Test registering multiple tools with the server."""
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
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("test-server")

        # Get all tools from MCIClient
        tools = mci_client.tools()
        assert len(tools) == 3

        # Register all tools
        await builder.register_all_tools(server, tools)

        # Verify all tools are registered
        assert hasattr(server, "_mci_tools")
        assert len(server._mci_tools) == 3  # type: ignore

        tool_names = [t.name for t in server._mci_tools]  # type: ignore
        assert "tool1" in tool_names
        assert "tool2" in tool_names
        assert "tool3" in tool_names
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_metadata():
    """Test that server metadata is properly set."""
    schema = {"schemaVersion": "1.0", "tools": []}

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("metadata-test", "2.5.1")

        assert server.name == "metadata-test"
        assert server._server_version == "2.5.1"  # type: ignore
        assert server._mci_client is mci_client  # type: ignore
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_instance_creation():
    """Test creating a ServerInstance."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [{"name": "test", "execution": {"type": "text", "text": "Hi"}}],
    }

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("test-server")
        tools = mci_client.tools()
        await builder.register_all_tools(server, tools)

        # Create server instance
        instance = ServerInstance(server, mci_client)

        assert instance is not None
        assert instance.server is server
        assert instance.mci_client is mci_client
        assert instance._running is False
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_server_instance_list_tools():
    """Test that ServerInstance can list tools."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "tool_a", "execution": {"type": "text", "text": "A"}},
            {"name": "tool_b", "execution": {"type": "text", "text": "B"}},
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("test-server")
        tools = mci_client.tools()
        await builder.register_all_tools(server, tools)

        instance = ServerInstance(server, mci_client)

        # The handlers are set up, verify tools can be listed
        assert hasattr(server, "_mci_tools")
        assert len(server._mci_tools) == 2  # type: ignore
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_builder_maintains_client_reference():
    """Test that the builder maintains reference to MCIClient."""
    schema = {"schemaVersion": "1.0", "tools": []}

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        assert builder.mci_client is mci_client
        assert builder.converter is not None
    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_register_tool_order_preserved():
    """Test that tools are registered in the order they're added."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "first", "execution": {"type": "text", "text": "1"}},
            {"name": "second", "execution": {"type": "text", "text": "2"}},
            {"name": "third", "execution": {"type": "text", "text": "3"}},
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        mci_client = MCIClient(schema_file_path=schema_path)
        builder = MCPServerBuilder(mci_client)

        server = await builder.create_server("test-server")
        tools = mci_client.tools()

        # Register tools one by one
        for tool in tools:
            await builder.register_tool(server, tool)

        # Verify order
        registered_names = [t.name for t in server._mci_tools]  # type: ignore
        assert registered_names == ["first", "second", "third"]
    finally:
        Path(schema_path).unlink()
