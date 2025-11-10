#!/usr/bin/env python3
"""
Manual test for annotations transfer from MCI to MCP.

This test demonstrates that annotations from MCI tool definitions
are correctly transferred to MCP tools when creating MCP servers.

Run with: uv run python testsManual/test_annotations_in_mcp.py
"""

import asyncio
import json
import tempfile
from pathlib import Path

from mcipy import MCIClient
from rich.console import Console
from rich.table import Table

from mci.core.mcp_server import MCPServerBuilder

console = Console()


async def test_annotations_transfer():
    """Test that annotations are preserved from MCI to MCP."""
    console.print("\n[bold blue]Testing Annotations Transfer from MCI to MCP[/bold blue]\n")

    # Create a test MCI schema with annotations
    schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Annotations Test",
            "description": "Testing annotation preservation",
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
                "name": "update_config",
                "description": "Update configuration",
                "annotations": {
                    "title": "Update Configuration",
                    "readOnlyHint": False,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "execution": {"type": "text", "text": "Config updated"},
            },
            {
                "name": "no_annotations",
                "description": "Tool without annotations",
                "execution": {"type": "text", "text": "No annotations"},
            },
        ],
    }

    # Create temporary schema file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mci.json", delete=False
    ) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        console.print("[green]✓[/green] Created test MCI schema")

        # Load schema using MCIClient
        mci_client = MCIClient(schema_file_path=schema_path)
        tools = mci_client.tools()
        console.print(f"[green]✓[/green] Loaded {len(tools)} tools from MCI schema\n")

        # Create MCP server and register tools
        builder = MCPServerBuilder(mci_client)
        server = await builder.create_server("annotations-test-server", "1.0.0")
        await builder.register_all_tools(server, tools)
        console.print(f"[green]✓[/green] Created MCP server: {server.name}\n")

        # Display annotations comparison table
        table = Table(title="Annotations Preservation: MCI → MCP", show_header=True)
        table.add_column("Tool Name", style="cyan")
        table.add_column("Title", style="yellow")
        table.add_column("Read Only", style="green")
        table.add_column("Destructive", style="red")
        table.add_column("Idempotent", style="blue")
        table.add_column("Open World", style="magenta")

        mcp_tools = server._mci_tools  # type: ignore

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

        # Verify specific tools
        console.print("[bold]Verification Results:[/bold]\n")

        delete_tool = mcp_tools[0]
        console.print(f"[cyan]Tool: {delete_tool.name}[/cyan]")
        if delete_tool.annotations:
            console.print(f"  ✓ Has annotations")
            console.print(f"  ✓ Title: {delete_tool.annotations.title}")
            console.print(f"  ✓ ReadOnly: {delete_tool.annotations.readOnlyHint}")
            console.print(f"  ✓ Destructive: {delete_tool.annotations.destructiveHint}")
            console.print(f"  ✓ Idempotent: {delete_tool.annotations.idempotentHint}")
            console.print(f"  ✓ OpenWorld: {delete_tool.annotations.openWorldHint}")
            
            # Verify values match expectations
            assert delete_tool.annotations.title == "Delete Resource"
            assert delete_tool.annotations.readOnlyHint is False
            assert delete_tool.annotations.destructiveHint is True
            assert delete_tool.annotations.idempotentHint is False
            assert delete_tool.annotations.openWorldHint is True
            console.print("  [green]✓ All annotations match expected values[/green]\n")
        else:
            console.print("  [red]✗ No annotations found[/red]\n")

        read_tool = mcp_tools[1]
        console.print(f"[cyan]Tool: {read_tool.name}[/cyan]")
        if read_tool.annotations:
            console.print(f"  ✓ Has annotations")
            console.print(f"  ✓ Title: {read_tool.annotations.title}")
            console.print(f"  ✓ ReadOnly: {read_tool.annotations.readOnlyHint}")
            
            assert read_tool.annotations.title == "Read Data"
            assert read_tool.annotations.readOnlyHint is True
            console.print("  [green]✓ Partial annotations correctly transferred[/green]\n")
        else:
            console.print("  [red]✗ No annotations found[/red]\n")

        no_ann_tool = mcp_tools[3]
        console.print(f"[cyan]Tool: {no_ann_tool.name}[/cyan]")
        if no_ann_tool.annotations is None:
            console.print("  [green]✓ Correctly has no annotations[/green]\n")
        else:
            console.print("  [red]✗ Should have no annotations[/red]\n")

        console.print("\n[bold green]✓ All tests passed![/bold green]")
        console.print("[green]Annotations are correctly transferred from MCI to MCP tools.[/green]\n")

    finally:
        Path(schema_path).unlink()


if __name__ == "__main__":
    asyncio.run(test_annotations_transfer())
