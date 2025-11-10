"""
mcp_server.py - MCP server creation and management

This module provides infrastructure for creating MCP servers that serve MCI tools.
The servers keep MCIClient and tool definitions in memory, register tools as
MCP-compatible tools, and delegate execution back to MCIClient.

Note: This module dynamically adds attributes to MCP Server instances for storing
MCI-specific data. These attributes are prefixed with _mci_ to avoid conflicts.
Type checkers will report these as unknown attributes, which is expected.
"""
# pyright: reportAttributeAccessIssue=false

import asyncio
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcipy import MCIClient
from mcipy.models import Tool
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from mci.core.tool_converter import MCIToolConverter


class MCPServerBuilder:
    """
    Builder for creating and configuring MCP servers with MCI tools.

    This class provides methods to create MCP server instances and register
    MCI tools as MCP-compatible tools. It maintains the MCIClient instance
    in memory and delegates all tool execution to MCIClient.
    """

    def __init__(self, mci_client: MCIClient):
        """
        Initialize the server builder with an MCIClient instance.

        Args:
            mci_client: Initialized MCIClient instance with loaded tools
        """
        self.mci_client: MCIClient = mci_client
        self.converter: MCIToolConverter = MCIToolConverter()

    async def create_server(self, name: str, version: str = "1.0.0") -> Server:
        """
        Create an MCP server instance configured to serve MCI tools.

        Creates a low-level MCP server that will expose MCI tools via the
        MCP protocol. The server maintains the MCIClient instance in memory
        and delegates tool execution to it.

        Args:
            name: Server name for MCP protocol
            version: Server version string

        Returns:
            Configured MCP Server instance

        Example:
            >>> builder = MCPServerBuilder(mci_client)
            >>> server = await builder.create_server("my-mci-server", "1.0.0")
        """
        server = Server(name)

        # Store reference to MCIClient for tool execution
        server._mci_client = self.mci_client  # type: ignore[attr-defined]
        server._mci_converter = self.converter  # type: ignore[attr-defined]
        server._server_version = version  # type: ignore[attr-defined]

        return server

    async def register_tool(self, server: Server, mci_tool: Tool) -> None:
        """
        Register a single MCI tool with the MCP server.

        Converts the MCI tool to MCP format and adds it to the server's
        tool registry. This does not define the handler yet - the handler
        is defined separately when setting up the server.

        Args:
            server: MCP Server instance
            mci_tool: MCI Tool object to register
        """
        # Convert MCI tool to MCP format
        mcp_tool = self.converter.convert_to_mcp_tool(mci_tool)

        # Store the tool in the server's internal registry
        if not hasattr(server, "_mci_tools"):
            server._mci_tools = []  # type: ignore[attr-defined]

        server._mci_tools.append(mcp_tool)  # type: ignore[attr-defined]

    async def register_all_tools(self, server: Server, tools: list[Tool]) -> None:
        """
        Register multiple MCI tools with the MCP server.

        Batch registration of tools. Each tool is converted to MCP format
        and added to the server's tool registry.

        Args:
            server: MCP Server instance
            tools: List of MCI Tool objects to register

        Example:
            >>> tools = mci_client.tools()
            >>> await builder.register_all_tools(server, tools)
        """
        for tool in tools:
            await self.register_tool(server, tool)


class ServerInstance:
    """
    Runtime instance of an MCP server serving MCI tools.

    This class manages the lifecycle of an MCP server, including startup,
    shutdown, and tool execution handling. It delegates all tool execution
    to the MCIClient instance.
    """

    def __init__(
        self, server: Server, mci_client: MCIClient, env_vars: dict[str, str] | None = None
    ):
        """
        Initialize the server instance.

        Args:
            server: Configured MCP Server
            mci_client: MCIClient instance for tool execution
            env_vars: Optional environment variables for template substitution during execution
        """
        self.server: Server = server
        self.mci_client: MCIClient = mci_client
        self.env_vars: dict[str, str] = env_vars or {}
        self.converter: MCIToolConverter = MCIToolConverter()
        self._running: bool = False

        # Set up handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers for tool listing and execution."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:  # pyright: ignore[reportUnusedFunction]
            """List all available MCI tools in MCP format."""
            if hasattr(self.server, "_mci_tools"):
                return self.server._mci_tools  # type: ignore[attr-defined]
            return []

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:  # pyright: ignore[reportUnusedFunction]
            """
            Handle tool execution by delegating to MCIClient.

            Args:
                name: Tool name
                arguments: Tool input arguments

            Returns:
                List of TextContent with execution results
            """
            return await self.handle_tool_call(name, arguments)

    async def handle_tool_call(
        self, name: str, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """
        Execute a tool using MCIClient and return MCP-formatted results.

        This method delegates execution to MCIClient.execute() and converts
        the result to MCP TextContent format.

        Args:
            name: Name of the tool to execute
            arguments: Input arguments for the tool

        Returns:
            List of TextContent blocks with execution results

        Raises:
            ValueError: If tool is not found or execution fails
        """
        try:
            # Execute the tool using MCIClient
            result = await asyncio.to_thread(
                self.mci_client.execute, tool_name=name, properties=arguments
            )

            # Convert result to MCP TextContent format
            # MCIClient.execute returns a dict with the execution result
            result_text = str(result)

            return [types.TextContent(type="text", text=result_text)]

        except Exception as e:
            # Return error as TextContent
            error_msg = f"Tool execution failed: {str(e)}"
            return [types.TextContent(type="text", text=error_msg)]

    async def start(self, stdio: bool = True) -> None:
        """
        Start the MCP server.

        Args:
            stdio: Whether to use STDIO transport (default: True)

        Raises:
            RuntimeError: If server is already running
        """
        if self._running:
            raise RuntimeError("Server is already running")

        self._running = True

        if stdio:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.server.name,
                        server_version=getattr(self.server, "_server_version", "1.0.0"),
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )

    def stop(self) -> None:
        """
        Stop the MCP server.

        Marks the server as not running. The actual shutdown is handled
        by the asyncio context manager in start().
        """
        self._running = False
