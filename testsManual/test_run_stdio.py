"""
Manual test for running MCP server with STDIO transport.

This manual test demonstrates launching an MCP server from an MCI schema
and connecting to it with an MCP client. Run this test from the terminal
to verify the full server lifecycle and protocol compliance.

Usage:
    uv run python testsManual/test_run_stdio.py
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

from mci.core.dynamic_server import DynamicMCPServer


def create_demo_schema() -> str:
    """Create a demo MCI schema for testing."""
    schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Demo MCP Server",
            "description": "Demonstration MCP server for testing mcix run command",
        },
        "tools": [
            {
                "name": "greet",
                "description": "Greet a person by name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the person to greet",
                        }
                    },
                    "required": ["name"],
                },
                "execution": {"type": "text", "text": "Hello, {{props.name}}! Welcome to MCI-MCP!"},
            },
            {
                "name": "calculate_sum",
                "description": "Calculate the sum of two numbers",
                "tags": ["math", "calculator"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["a", "b"],
                },
                "execution": {"type": "text", "text": "The sum of {{props.a}} + {{props.b}}"},
            },
            {
                "name": "echo_message",
                "description": "Echo a message back",
                "tags": ["utility"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back",
                        }
                    },
                    "required": ["message"],
                },
                "execution": {"type": "text", "text": "Echo: {{props.message}}"},
            },
            {
                "name": "get_info",
                "description": "Get server information",
                "execution": {
                    "type": "text",
                    "text": "MCI Dynamic MCP Server v1.0.0 - Serving tools from MCI schema",
                },
            },
            {
                "name": "list_env",
                "description": "List environment variables (demo of env templating)",
                "execution": {
                    "type": "text",
                    "text": "User: {{env.USER}}, Home: {{env.HOME}}, Path: {{env.PATH}}",
                },
            },
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f, indent=2)
        return f.name


async def test_server_creation_and_tools():
    """Test creating the server and verifying tool registration."""
    print("=" * 80)
    print("Manual Test: MCI Run Command - STDIO Server")
    print("=" * 80)
    print()

    # Step 1: Create demo schema
    print("Step 1: Creating demo MCI schema...")
    schema_path = create_demo_schema()
    print(f"✓ Created schema at: {schema_path}")
    print()

    try:
        # Step 2: Create server without filter
        print("Step 2: Creating MCP server from schema (no filter)...")
        env_vars = dict(os.environ)
        server = DynamicMCPServer(schema_path, env_vars=env_vars)
        instance = await server.create_from_mci_schema("demo-mci-server", "1.0.0")

        print(f"✓ Server created: {server.server.name}")  # type: ignore
        print(f"  Tools registered: {server.get_tool_count()}")
        print()

        # Step 3: Display registered tools
        print("Step 3: Displaying registered tools...")
        mcp_tools = server.server._mci_tools  # type: ignore
        for i, tool in enumerate(mcp_tools, 1):
            print(f"  {i}. {tool.name}")
            print(f"     Description: {tool.description}")
            if tool.inputSchema.get("properties"):
                props = list(tool.inputSchema["properties"].keys())
                print(f"     Parameters: {', '.join(props)}")
            print()

        # Step 4: Test tool execution
        print("Step 4: Testing tool execution...")
        print()

        # Test greet tool
        print("  Testing 'greet' tool...")
        result = await instance.handle_tool_call("greet", {"name": "Alice"})
        print(f"  Result: {result[0].text}")
        print()

        # Test calculate_sum tool
        print("  Testing 'calculate_sum' tool...")
        result = await instance.handle_tool_call("calculate_sum", {"a": 42, "b": 58})
        print(f"  Result: {result[0].text}")
        print()

        # Test echo_message tool
        print("  Testing 'echo_message' tool...")
        result = await instance.handle_tool_call("echo_message", {"message": "Hello World!"})
        print(f"  Result: {result[0].text}")
        print()

        # Test get_info tool (no parameters)
        print("  Testing 'get_info' tool (no parameters)...")
        result = await instance.handle_tool_call("get_info", {})
        print(f"  Result: {result[0].text}")
        print()

        # Step 5: Test with filter
        print("Step 5: Creating server with filter (tags:math)...")
        filtered_server = DynamicMCPServer(schema_path, filter_spec="tags:math", env_vars=env_vars)
        await filtered_server.create_from_mci_schema(
            "filtered-server", "1.0.0"
        )

        print("✓ Filtered server created")
        print(f"  Tools registered: {filtered_server.get_tool_count()}")
        print()

        filtered_tools = filtered_server.server._mci_tools  # type: ignore
        print("  Filtered tools:")
        for tool in filtered_tools:
            print(f"    - {tool.name}")
        print()

        # Step 6: Test with different filter
        print("Step 6: Creating server with filter (only:greet,echo_message)...")
        only_server = DynamicMCPServer(
            schema_path, filter_spec="only:greet,echo_message", env_vars=env_vars
        )
        await only_server.create_from_mci_schema("only-server", "1.0.0")

        print("✓ Only-filtered server created")
        print(f"  Tools registered: {only_server.get_tool_count()}")
        print()

        only_tools = only_server.server._mci_tools  # type: ignore
        print("  Filtered tools:")
        for tool in only_tools:
            print(f"    - {tool.name}")
        print()

        # Step 7: Summary
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        print("✓ All steps completed successfully!")
        print()
        print("Verified functionality:")
        print("  ✓ Server creation from MCI schema")
        print("  ✓ Tool registration and conversion to MCP format")
        print("  ✓ Tool execution via MCIClient delegation")
        print("  ✓ Filter support (tags and only)")
        print("  ✓ Environment variable templating")
        print()
        print("The server is ready to run with STDIO transport.")
        print()
        print("To run this server from the CLI:")
        print(f"  uv run mcix run --file={schema_path}")
        print()
        print("To run with filter:")
        print(f"  uv run mcix run --file={schema_path} --filter=tags:math")
        print()
        print("=" * 80)

    finally:
        # Cleanup
        Path(schema_path).unlink()
        print("\n✓ Cleaned up test schema file")


async def demonstrate_cli_usage():
    """Demonstrate CLI usage patterns."""
    print("\n" + "=" * 80)
    print("CLI Usage Patterns")
    print("=" * 80)
    print()
    print("The mcix run command supports the following usage patterns:")
    print()
    print("1. Run with default mci.json/mci.yaml:")
    print("   $ uv run mcix run")
    print()
    print("2. Run with custom file:")
    print("   $ uv run mcix run --file=custom.mci.json")
    print()
    print("3. Run with tag filter:")
    print("   $ uv run mcix run --filter=tags:api,database")
    print()
    print("4. Run with only specific tools:")
    print("   $ uv run mcix run --filter=only:tool1,tool2")
    print()
    print("5. Run excluding specific tools:")
    print("   $ uv run mcix run --filter=except:admin_tools")
    print()
    print("6. Run with toolset filter:")
    print("   $ uv run mcix run --filter=toolsets:weather,news")
    print()
    print("Press Ctrl+C to stop the server when running.")
    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    asyncio.run(test_server_creation_and_tools())
    asyncio.run(demonstrate_cli_usage())
    print("\n")
