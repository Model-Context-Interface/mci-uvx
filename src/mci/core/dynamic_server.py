"""
dynamic_server.py - Dynamic MCP server creation from MCI schemas

This module provides the DynamicMCPServer class for creating and running
MCP servers that dynamically load tools from MCI schema files. The server
uses MCIClient to load tools (including toolsets and environment variables),
converts them to MCP format, and delegates execution back to MCIClient.

The server supports:
- Loading tools from JSON/YAML MCI schemas
- Tool filtering by name, tags, and toolsets
- STDIO transport for MCP protocol
- Graceful shutdown and error handling
- Environment variable templating

Note: This module accesses dynamically added attributes on MCP Server instances
(prefixed with _mci_). Type checkers will report these as unknown attributes,
which is expected.
"""
# pyright: reportAttributeAccessIssue=false

from mcp.server.lowlevel import Server

from mci.core.mci_client import MCIClientWrapper
from mci.core.mcp_server import MCPServerBuilder, ServerInstance
from mci.core.tool_manager import ToolManager


class DynamicMCPServer:
    """
    Creates and manages dynamic MCP servers from MCI schemas.

    This class provides the main interface for creating MCP servers that serve
    tools from MCI schema files. It handles loading, filtering, conversion,
    and runtime management of the server.
    """

    def __init__(
        self,
        schema_path: str,
        filter_spec: str | None = None,
        env_vars: dict[str, str] | None = None,
    ):
        """
        Initialize the dynamic server configuration.

        Args:
            schema_path: Path to the MCI schema file (.json, .yaml, or .yml)
            filter_spec: Optional filter specification (e.g., "tags:api,database")
            env_vars: Optional environment variables for template substitution
        """
        self.schema_path: str = schema_path
        self.filter_spec: str | None = filter_spec
        self.env_vars: dict[str, str] = env_vars or {}
        self.server: Server | None = None
        self.instance: ServerInstance | None = None
        self.mci_client_wrapper: MCIClientWrapper | None = None

    async def create_from_mci_schema(
        self, server_name: str = "mci-dynamic-server", server_version: str = "1.0.0"
    ) -> ServerInstance:
        """
        Create an MCP server instance from the MCI schema.

        This method:
        1. Loads tools using MCIClient (with toolsets and env var templating)
        2. Applies filters if specified
        3. Converts tools to MCP format using Stage 8 converter
        4. Registers tools with MCP server
        5. Sets up handlers for tool listing and execution
        6. Returns ServerInstance ready for STDIO transport

        Args:
            server_name: Name for the MCP server
            server_version: Version string for the server

        Returns:
            ServerInstance configured with MCI tools

        Raises:
            Exception: If schema loading, tool conversion, or server creation fails

        Example:
            >>> server = DynamicMCPServer("mci.json")
            >>> instance = await server.create_from_mci_schema()
            >>> await instance.start(stdio=True)
        """
        # Step 1: Load tools using MCIClient
        self.mci_client_wrapper = MCIClientWrapper(self.schema_path, self.env_vars)

        # Step 2: Apply filters if specified
        if self.filter_spec:
            tools = ToolManager.apply_filter_spec(self.mci_client_wrapper, self.filter_spec)
        else:
            tools = self.mci_client_wrapper.get_tools()

        # Step 3: Create MCP server using Stage 8 infrastructure
        builder = MCPServerBuilder(self.mci_client_wrapper.client)
        self.server = await builder.create_server(server_name, server_version)

        # Step 4: Register all tools (converter handles MCI to MCP conversion)
        await builder.register_all_tools(self.server, tools)

        # Step 5: Create ServerInstance (sets up handlers for listing and execution)
        self.instance = ServerInstance(self.server, self.mci_client_wrapper.client, self.env_vars)

        return self.instance

    async def start_stdio(self) -> None:
        """
        Start the MCP server on STDIO transport.

        This method starts the server and blocks until shutdown is requested.
        The server will stop when:
        - Ctrl+C (KeyboardInterrupt) is pressed
        - The client disconnects
        - An unrecoverable error occurs

        The server will:
        - Respond to MCP protocol requests for tool listing
        - Execute tools by delegating to MCIClient.execute()
        - Support structured output validation (outputSchema)
        - Handle errors gracefully

        Raises:
            RuntimeError: If server instance is not created
            Exception: If server startup or runtime fails

        Example:
            >>> server = DynamicMCPServer("mci.json")
            >>> await server.create_from_mci_schema()
            >>> await server.start_stdio()  # Blocks until Ctrl+C
        """
        if self.instance is None:
            raise RuntimeError("Server instance not created. Call create_from_mci_schema() first.")

        try:
            # Start the server on STDIO (this blocks until server stops)
            # KeyboardInterrupt will be raised automatically when Ctrl+C is pressed
            await self.instance.start(stdio=True)
        except KeyboardInterrupt:
            # Graceful shutdown on Ctrl+C
            pass
        finally:
            # Cleanup
            if self.instance:
                self.instance.stop()

    def get_tool_count(self) -> int:
        """
        Get the number of tools registered with the server.

        Returns:
            Number of registered tools, or 0 if server not created

        Example:
            >>> server = DynamicMCPServer("mci.json")
            >>> await server.create_from_mci_schema()
            >>> count = server.get_tool_count()
            >>> print(f"Server has {count} tools")
        """
        if self.server and hasattr(self.server, "_mci_tools"):
            return len(self.server._mci_tools)  # type: ignore[attr-defined]
        return 0


async def run_server(
    schema_path: str, filter_spec: str | None = None, env_vars: dict[str, str] | None = None
) -> None:
    """
    Create and run a dynamic MCP server from an MCI schema.

    This is a convenience function that creates a server, loads tools,
    and starts it on STDIO in a single call.

    Args:
        schema_path: Path to the MCI schema file
        filter_spec: Optional filter specification (e.g., "tags:api,database")
        env_vars: Optional environment variables for template substitution

    Example:
        >>> await run_server("mci.json")
        >>> await run_server("mci.json", filter_spec="tags:api")
    """
    server = DynamicMCPServer(schema_path, filter_spec, env_vars)
    await server.create_from_mci_schema()
    await server.start_stdio()
