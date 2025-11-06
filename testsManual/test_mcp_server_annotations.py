#!/usr/bin/env python3
"""
Test script to verify annotations are present in MCP server responses.

This script starts an MCP server and queries it to verify that tool annotations
are correctly included in the tool list response.
"""

import asyncio
import json
import pathlib
import sys
import tempfile

from mcipy import MCIClient
from rich.console import Console
from rich.table import Table

from mci.core.mcp_server import MCPServerBuilder

console = Console()


async def test_mcp_server_annotations():
    """Test that MCP server includes annotations in tool responses."""
    console.print("\n[bold blue]Testing Annotations in MCP Server[/bold blue]\n")

    # Create a test schema with annotations
    test_schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Annotations Test",
            "description": "Testing annotation preservation in MCP server",
        },
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
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Resource ID to delete",
                        }
                    },
                    "required": ["id"],
                },
                "execution": {
                    "type": "text",
                    "text": "Deleted resource with ID: {{props.id}}",
                },
            },
            {
                "name": "read_data",
                "description": "Read data from the database",
                "annotations": {"title": "Read Data", "readOnlyHint": True},
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Query string"}
                    },
                    "required": ["query"],
                },
                "execution": {
                    "type": "text",
                    "text": "Reading data with query: {{props.query}}",
                },
            },
            {
                "name": "update_config",
                "description": "Update configuration settings",
                "annotations": {
                    "title": "Update Configuration",
                    "readOnlyHint": False,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Configuration key"},
                        "value": {"type": "string", "description": "Configuration value"},
                    },
                    "required": ["key", "value"],
                },
                "execution": {
                    "type": "text",
                    "text": "Updated config: {{props.key}} = {{props.value}}",
                },
            },
            {
                "name": "simple_tool",
                "description": "A simple tool without annotations",
                "execution": {"type": "text", "text": "Simple output without annotations"},
            },
        ],
        "toolsets": [],
        "mcp_servers": {},
    }

    # Create temporary schema file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mci.json", delete=False
    ) as f:
        json.dump(test_schema, f)
        schema_path = f.name

    try:
        console.print(f"[green]✓[/green] Created test schema at {schema_path}")

        # Load MCI schema
        mci_client = MCIClient(schema_file_path=schema_path)
        tools = mci_client.tools()
        console.print(f"[green]✓[/green] Loaded {len(tools)} tools from MCI schema\n")

        # Create MCP server
        builder = MCPServerBuilder(mci_client)
        server = await builder.create_server("annotations-test-server", "1.0.0")
        await builder.register_all_tools(server, tools)
        console.print(f"[green]✓[/green] Created MCP server: {server.name}\n")

        # Get MCP tools
        mcp_tools = server._mci_tools  # type: ignore

        # Create comparison table
        table = Table(title="MCP Server Tool Annotations", show_header=True)
        table.add_column("Tool Name", style="cyan", width=20)
        table.add_column("Title", style="yellow", width=25)
        table.add_column("ReadOnly", style="green", width=10)
        table.add_column("Destructive", style="red", width=12)
        table.add_column("Idempotent", style="blue", width=11)
        table.add_column("OpenWorld", style="magenta", width=11)

        all_passed = True

        for mcp_tool in mcp_tools:
            ann = mcp_tool.annotations
            if ann:
                table.add_row(
                    mcp_tool.name,
                    str(ann.title or "-"),
                    str(ann.readOnlyHint if ann.readOnlyHint is not None else "-"),
                    str(ann.destructiveHint if ann.destructiveHint is not None else "-"),
                    str(ann.idempotentHint if ann.idempotentHint is not None else "-"),
                    str(ann.openWorldHint if ann.openWorldHint is not None else "-"),
                )
            else:
                table.add_row(mcp_tool.name, "-", "-", "-", "-", "-")

        console.print(table)
        console.print()

        # Verify each tool
        console.print("[bold]Verification:[/bold]\n")

        # Tool 1: delete_resource
        delete_tool = mcp_tools[0]
        console.print(f"[cyan]{delete_tool.name}[/cyan]")
        if delete_tool.annotations:
            if (
                delete_tool.annotations.title == "Delete Resource"
                and delete_tool.annotations.readOnlyHint is False
                and delete_tool.annotations.destructiveHint is True
                and delete_tool.annotations.idempotentHint is False
                and delete_tool.annotations.openWorldHint is True
            ):
                console.print("  [green]✓ All annotations correct[/green]")
            else:
                console.print("  [red]✗ Annotations mismatch[/red]")
                all_passed = False
        else:
            console.print("  [red]✗ Missing annotations[/red]")
            all_passed = False

        # Tool 2: read_data
        read_tool = mcp_tools[1]
        console.print(f"[cyan]{read_tool.name}[/cyan]")
        if read_tool.annotations:
            if (
                read_tool.annotations.title == "Read Data"
                and read_tool.annotations.readOnlyHint is True
            ):
                console.print("  [green]✓ Annotations correct[/green]")
            else:
                console.print("  [red]✗ Annotations mismatch[/red]")
                all_passed = False
        else:
            console.print("  [red]✗ Missing annotations[/red]")
            all_passed = False

        # Tool 3: update_config
        update_tool = mcp_tools[2]
        console.print(f"[cyan]{update_tool.name}[/cyan]")
        if update_tool.annotations:
            if (
                update_tool.annotations.title == "Update Configuration"
                and update_tool.annotations.readOnlyHint is False
                and update_tool.annotations.destructiveHint is False
                and update_tool.annotations.idempotentHint is True
            ):
                console.print("  [green]✓ Annotations correct[/green]")
            else:
                console.print("  [red]✗ Annotations mismatch[/red]")
                all_passed = False
        else:
            console.print("  [red]✗ Missing annotations[/red]")
            all_passed = False

        # Tool 4: simple_tool
        simple_tool = mcp_tools[3]
        console.print(f"[cyan]{simple_tool.name}[/cyan]")
        if simple_tool.annotations is None:
            console.print("  [green]✓ Correctly has no annotations[/green]")
        else:
            console.print("  [red]✗ Should not have annotations[/red]")
            all_passed = False

        console.print()

        if all_passed:
            console.print("[bold green]✓ All tests passed![/bold green]")
            console.print(
                "[green]Annotations are correctly preserved in MCP server responses.[/green]\n"
            )
            return True
        else:
            console.print("[bold red]✗ Some tests failed![/bold red]")
            console.print(
                "[red]Annotations are not correctly preserved in MCP server responses.[/red]\n"
            )
            return False
    finally:
        # Clean up temporary file
        pathlib.Path(schema_path).unlink(missing_ok=True)


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server_annotations())
    sys.exit(0 if success else 1)
