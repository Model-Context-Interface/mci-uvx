#!/usr/bin/env python3
"""
Manual test for tool loading with MCI-PY integration.

This script demonstrates loading MCI tools using MCIClient and applying
various filters. Run this script to manually verify the integration works
correctly with real MCI files.

Usage:
    uv run python testsManual/test_tool_loading.py
"""

import json
import sys
import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from mci.core.mci_client import MCIClientWrapper
from mci.core.tool_manager import ToolManager
from mci.utils.error_handler import ErrorHandler

console = Console()


def create_sample_schema() -> str:
    """Create a sample schema file for testing."""
    schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Sample Tool Collection",
            "description": "A sample collection of tools for testing",
            "version": "1.0.0",
        },
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather information for a location",
                "tags": ["api", "read", "weather"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name or location"},
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature units",
                        },
                    },
                    "required": ["location"],
                },
                "execution": {
                    "type": "http",
                    "method": "GET",
                    "url": "https://api.weather.example.com/current",
                    "params": {
                        "location": "{{props.location}}",
                        "units": "{{props.units}}",
                        "api_key": "{{env.WEATHER_API_KEY}}",
                    },
                },
            },
            {
                "name": "create_report",
                "description": "Create a new report",
                "tags": ["api", "write", "reports"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Report title"},
                        "content": {"type": "string", "description": "Report content"},
                    },
                    "required": ["title", "content"],
                },
                "execution": {
                    "type": "http",
                    "method": "POST",
                    "url": "https://api.example.com/reports",
                    "body": {
                        "type": "json",
                        "content": {"title": "{{props.title}}", "content": "{{props.content}}"},
                    },
                },
            },
            {
                "name": "list_directory",
                "description": "List files in a directory",
                "tags": ["cli", "filesystem", "read"],
                "inputSchema": {
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "Directory path"}},
                    "required": ["path"],
                },
                "execution": {"type": "cli", "command": "ls", "args": ["-la", "{{props.path}}"]},
            },
            {
                "name": "search_database",
                "description": "Search database for records",
                "tags": ["database", "read", "search"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"],
                },
                "execution": {"type": "text", "text": "Searching for: {{props.query}}"},
            },
            {
                "name": "echo_message",
                "description": "Simple echo tool",
                "tags": ["text", "simple"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Message to echo"}
                    },
                    "required": ["message"],
                },
                "execution": {"type": "text", "text": "Echo: {{props.message}}"},
            },
            {
                "name": "deprecated_tool",
                "description": "A deprecated tool that should not be used",
                "tags": ["deprecated", "old"],
                "execution": {"type": "text", "text": "This tool is deprecated"},
            },
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f, indent=2)
        return f.name


def display_tools_table(tools, title="Tools"):
    """Display tools in a formatted table."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Tags", style="yellow")
    table.add_column("Type", style="green")

    for tool in tools:
        tags = ", ".join(tool.tags) if tool.tags else "none"
        exec_type = tool.execution.type if hasattr(tool.execution, "type") else "unknown"
        table.add_row(tool.name, tool.description or "", tags, exec_type)

    console.print(table)
    console.print(f"\n[bold]Total tools:[/bold] {len(tools)}\n")


def test_basic_loading():
    """Test basic tool loading."""
    console.print("\n[bold blue]═══ Test 1: Basic Tool Loading ═══[/bold blue]\n")

    schema_path = create_sample_schema()
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = wrapper.get_tools()

        console.print(f"✓ Successfully loaded schema from: {schema_path}")
        console.print(f"✓ Found {len(tools)} tools\n")

        display_tools_table(tools, "All Available Tools")

        # Test list_tool_names
        tool_names = wrapper.list_tool_names()
        console.print(f"[bold]Tool names:[/bold] {', '.join(tool_names)}\n")

    finally:
        Path(schema_path).unlink()


def test_filter_only():
    """Test filtering with 'only' specification."""
    console.print("\n[bold blue]═══ Test 2: Filter Only ═══[/bold blue]\n")

    schema_path = create_sample_schema()
    try:
        wrapper = MCIClientWrapper(schema_path)

        filter_spec = "only:get_weather,create_report,echo_message"
        console.print(f"Filter specification: [yellow]{filter_spec}[/yellow]\n")

        tools = ToolManager.apply_filter_spec(wrapper, filter_spec)
        display_tools_table(tools, "Filtered Tools (only)")

    finally:
        Path(schema_path).unlink()


def test_filter_except():
    """Test filtering with 'except' specification."""
    console.print("\n[bold blue]═══ Test 3: Filter Except ═══[/bold blue]\n")

    schema_path = create_sample_schema()
    try:
        wrapper = MCIClientWrapper(schema_path)

        filter_spec = "except:deprecated_tool"
        console.print(f"Filter specification: [yellow]{filter_spec}[/yellow]\n")

        tools = ToolManager.apply_filter_spec(wrapper, filter_spec)
        display_tools_table(tools, "Filtered Tools (except)")

    finally:
        Path(schema_path).unlink()


def test_filter_tags():
    """Test filtering by tags."""
    console.print("\n[bold blue]═══ Test 4: Filter by Tags ═══[/bold blue]\n")

    schema_path = create_sample_schema()
    try:
        wrapper = MCIClientWrapper(schema_path)

        # Test single tag
        filter_spec = "tags:api"
        console.print(f"Filter specification: [yellow]{filter_spec}[/yellow]\n")
        tools = ToolManager.apply_filter_spec(wrapper, filter_spec)
        display_tools_table(tools, "API Tools")

        # Test multiple tags
        filter_spec = "tags:read,write"
        console.print(f"Filter specification: [yellow]{filter_spec}[/yellow]\n")
        tools = ToolManager.apply_filter_spec(wrapper, filter_spec)
        display_tools_table(tools, "Read/Write Tools")

    finally:
        Path(schema_path).unlink()


def test_filter_without_tags():
    """Test filtering to exclude tags."""
    console.print("\n[bold blue]═══ Test 5: Filter Without Tags ═══[/bold blue]\n")

    schema_path = create_sample_schema()
    try:
        wrapper = MCIClientWrapper(schema_path)

        filter_spec = "without-tags:deprecated,old"
        console.print(f"Filter specification: [yellow]{filter_spec}[/yellow]\n")

        tools = ToolManager.apply_filter_spec(wrapper, filter_spec)
        display_tools_table(tools, "Non-Deprecated Tools")

    finally:
        Path(schema_path).unlink()


def test_error_handling():
    """Test error handling."""
    console.print("\n[bold blue]═══ Test 6: Error Handling ═══[/bold blue]\n")

    # Test missing file
    console.print("[bold]Testing missing file error:[/bold]\n")
    try:
        MCIClientWrapper("/nonexistent/schema.mci.json")
    except Exception as e:
        formatted_error = ErrorHandler.format_mci_client_error(e)
        console.print(formatted_error)

    # Test invalid filter spec
    console.print("\n[bold]Testing invalid filter specification:[/bold]\n")
    schema_path = create_sample_schema()
    try:
        wrapper = MCIClientWrapper(schema_path)
        try:
            ToolManager.apply_filter_spec(wrapper, "invalid_spec")
        except ValueError as e:
            console.print(f"[red]✗ {e}[/red]\n")
    finally:
        Path(schema_path).unlink()


def test_with_real_mci_file():
    """Test with the example toolset from assets."""
    console.print("\n[bold blue]═══ Test 7: Real MCI File (example_toolset) ═══[/bold blue]\n")

    # Try to find the example toolset
    example_path = Path(__file__).parent.parent / "src" / "mci" / "assets" / "example_toolset.mci.json"

    if not example_path.exists():
        console.print("[yellow]⚠ Example toolset not found, skipping test[/yellow]\n")
        return

    try:
        console.print(f"Loading: [cyan]{example_path}[/cyan]\n")

        env_vars = {"PROJECT_ROOT": str(Path.home())}
        wrapper = MCIClientWrapper(str(example_path), env_vars=env_vars)
        tools = wrapper.get_tools()

        display_tools_table(tools, "Example Toolset Tools")

    except Exception as e:
        formatted_error = ErrorHandler.format_mci_client_error(e)
        console.print(formatted_error)


def main():
    """Run all manual tests."""
    console.print(
        "\n[bold green]MCI-PY Integration - Manual Tool Loading Tests[/bold green]"
    )
    console.print("[dim]Testing MCIClientWrapper and ToolManager functionality[/dim]\n")

    try:
        test_basic_loading()
        test_filter_only()
        test_filter_except()
        test_filter_tags()
        test_filter_without_tags()
        test_error_handling()
        test_with_real_mci_file()

        console.print("\n[bold green]✓ All manual tests completed successfully![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed with error:[/bold red]")
        console.print(str(e))
        console.print()
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
