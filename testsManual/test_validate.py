"""
Manual test for the validate command.

This script provides manual testing for the validate command with various scenarios.
Run this script to visually verify the output of the validate command.

Usage:
    uv run python testsManual/test_validate.py
"""

import json
import tempfile
from pathlib import Path

from rich.console import Console

from mci.cli.validate import validate
from click.testing import CliRunner


def print_section(console: Console, title: str):
    """Print a section header."""
    console.print(f"\n{'='*70}")
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"{'='*70}\n")


def test_valid_schema():
    """Test 1: Valid schema with no issues."""
    console = Console()
    print_section(console, "Test 1: Valid Schema")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "valid.mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Valid Test Schema",
                "description": "A valid schema with no issues",
            },
            "tools": [
                {
                    "name": "echo",
                    "description": "Echo a message",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "Message to echo"}
                        },
                        "required": ["message"],
                    },
                    "execution": {"type": "text", "text": "{{props.message}}"},
                }
            ],
            "toolsets": [],
            "mcp_servers": {},
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        console.print(f"[dim]Schema file: {schema_file}[/dim]")
        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])
        console.print(result.output)


def test_invalid_schema():
    """Test 2: Invalid schema (missing required fields)."""
    console = Console()
    print_section(console, "Test 2: Invalid Schema (Missing Required Fields)")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "invalid.mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            # Missing metadata - required field
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        console.print(f"[dim]Schema file: {schema_file}[/dim]")
        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])
        console.print(result.output)


def test_schema_with_missing_toolsets():
    """
    Test 3: Schema with missing toolset files.
    
    This test verifies that the validate CLI command correctly reports errors from MCIClient
    when toolset references are missing (i.e., toolset files do not exist in the mci/ directory).
    It demonstrates that validation fails and the CLI output includes appropriate error messages.
    """
    console = Console()
    print_section(console, "Test 3: Schema with Missing Toolset Files (Errors)")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci directory
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()

        schema_file = Path(tmpdir) / "with_toolsets.mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Schema with Toolsets",
                "description": "Schema that references missing toolsets",
            },
            "tools": [],
            "toolsets": ["weather", "database", "analytics"],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        console.print(f"[dim]Schema file: {schema_file}[/dim]")
        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])
        console.print(result.output)


def test_schema_with_missing_mcp_commands():
    """Test 4: Valid schema with missing MCP commands (warnings)."""
    console = Console()
    print_section(console, "Test 4: Schema with Missing MCP Commands (Warnings)")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "with_mcp.mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Schema with MCP Servers",
                "description": "Schema with MCP server references",
            },
            "tools": [],
            "mcp_servers": {
                "weather_server": {
                    "command": "nonexistent_weather_mcp",
                    "args": ["--port", "3000"],
                },
                "db_server": {
                    "command": "nonexistent_db_mcp",
                    "args": [],
                },
            },
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        console.print(f"[dim]Schema file: {schema_file}[/dim]")
        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])
        console.print(result.output)


def test_schema_with_both_warnings():
    """Test 5: Valid schema with MCP command warnings."""
    console = Console()
    print_section(console, "Test 5: Schema with MCP Command Warnings")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "with_warnings.mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Schema with Warnings",
                "description": "Schema with MCP server warnings",
            },
            "tools": [
                {
                    "name": "test_tool",
                    "description": "Test tool",
                    "execution": {"type": "text", "text": "Test"},
                }
            ],
            "toolsets": [],
            "mcp_servers": {
                "server1": {"command": "fake_cmd_1", "args": []},
                "server2": {"command": "fake_cmd_2", "args": []},
            },
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        console.print(f"[dim]Schema file: {schema_file}[/dim]")
        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])
        console.print(result.output)


def test_yaml_schema():
    """Test 6: Valid YAML schema."""
    console = Console()
    print_section(console, "Test 6: Valid YAML Schema")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "test.mci.yaml"
        schema_content = """
schemaVersion: "1.0"
metadata:
  name: "YAML Test Schema"
  description: "Testing YAML format validation"
tools:
  - name: "yaml_tool"
    description: "Tool defined in YAML"
    execution:
      type: "text"
      text: "YAML output"
toolsets: []
mcp_servers: {}
"""
        schema_file.write_text(schema_content)

        console.print(f"[dim]Schema file: {schema_file}[/dim]")
        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])
        console.print(result.output)


def test_validate_actual_mci_json():
    """Test 7: Validate the actual mci.json in the project."""
    console = Console()
    print_section(console, "Test 7: Validate Project's mci.json")

    # Try to validate the actual project mci.json
    project_mci = Path(__file__).parent.parent / "mci.json"

    if project_mci.exists():
        console.print(f"[dim]Validating: {project_mci}[/dim]")
        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(project_mci)])
        console.print(result.output)
    else:
        console.print("[yellow]Project mci.json not found, skipping this test[/yellow]")


def main():
    """Run all manual tests."""
    console = Console()
    console.print("\n[bold green]Starting Manual Validation Tests[/bold green]")
    console.print("[dim]These tests show the visual output of the validate command[/dim]")

    test_valid_schema()
    test_invalid_schema()
    test_schema_with_missing_toolsets()
    test_schema_with_missing_mcp_commands()
    test_schema_with_both_warnings()
    test_yaml_schema()
    test_validate_actual_mci_json()

    console.print("\n[bold green]✅ All Manual Tests Completed[/bold green]\n")


if __name__ == "__main__":
    main()
