"""
Manual test for the add command.

Run this script to manually test adding toolsets to real MCI files
and verify the changes are correct.

Usage:
    uv run python testsManual/test_add.py
"""

import json
import tempfile
from pathlib import Path

import yaml
from rich.console import Console

from mci.core.schema_editor import SchemaEditor

console = Console()


def test_add_to_json():
    """Test adding toolsets to a JSON file."""
    console.print("\n[bold blue]Testing JSON file modification[/bold blue]\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "test.mci.json"

        # Create initial schema
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test Project", "description": "Testing add command"},
            "tools": [
                {
                    "name": "echo_tool",
                    "description": "Echo tool",
                    "inputSchema": {"type": "object", "properties": {}},
                    "execution": {"type": "text", "text": "Echo"},
                }
            ],
            "toolsets": [],
        }

        schema_file.write_text(json.dumps(schema_content, indent=2))
        console.print(f"[green]✓[/green] Created test file: {schema_file}")

        # Display initial content
        console.print("\n[yellow]Initial content:[/yellow]")
        console.print(schema_file.read_text())

        # Add simple toolset
        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools")
        editor.save_schema()
        console.print("\n[green]✓[/green] Added 'weather-tools' toolset")

        # Add toolset with filter
        editor.load_schema(str(schema_file))
        editor.add_toolset("analytics", "only", "SummarizeData,AnalyzeSentiment")
        editor.save_schema()
        console.print("[green]✓[/green] Added 'analytics' toolset with filter")

        # Display final content
        console.print("\n[yellow]Final content:[/yellow]")
        final_content = schema_file.read_text()
        console.print(final_content)

        # Verify changes
        with open(schema_file) as f:
            data = json.load(f)

        console.print("\n[bold]Verification:[/bold]")
        console.print(f"  Toolsets count: {len(data['toolsets'])}")
        console.print(f"  Toolsets: {data['toolsets']}")

        assert len(data["toolsets"]) == 2
        assert "weather-tools" in data["toolsets"]
        assert data["toolsets"][1]["name"] == "analytics"
        assert data["toolsets"][1]["filter"] == "only"

        console.print("\n[bold green]✅ JSON test passed![/bold green]\n")


def test_add_to_yaml():
    """Test adding toolsets to a YAML file."""
    console.print("\n[bold blue]Testing YAML file modification[/bold blue]\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "test.mci.yaml"

        # Create initial schema
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test Project", "description": "Testing add command"},
            "tools": [],
            "toolsets": [],
        }

        with open(schema_file, "w") as f:
            yaml.safe_dump(schema_content, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]✓[/green] Created test file: {schema_file}")

        # Display initial content
        console.print("\n[yellow]Initial content:[/yellow]")
        console.print(schema_file.read_text())

        # Add simple toolset
        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools")
        editor.save_schema()
        console.print("\n[green]✓[/green] Added 'weather-tools' toolset")

        # Add toolset with tags filter
        editor.load_schema(str(schema_file))
        editor.add_toolset("api-tools", "tags", "api,database")
        editor.save_schema()
        console.print("[green]✓[/green] Added 'api-tools' toolset with tags filter")

        # Display final content
        console.print("\n[yellow]Final content:[/yellow]")
        final_content = schema_file.read_text()
        console.print(final_content)

        # Verify changes
        with open(schema_file) as f:
            data = yaml.safe_load(f)

        console.print("\n[bold]Verification:[/bold]")
        console.print(f"  Toolsets count: {len(data['toolsets'])}")
        console.print(f"  Toolsets: {data['toolsets']}")

        # Verify YAML format preserved (no JSON curly braces)
        assert "{" not in final_content
        assert "schemaVersion:" in final_content

        assert len(data["toolsets"]) == 2
        assert "weather-tools" in data["toolsets"]
        assert data["toolsets"][1]["name"] == "api-tools"
        assert data["toolsets"][1]["filter"] == "tags"

        console.print("\n[bold green]✅ YAML test passed![/bold green]\n")


def test_update_existing_toolset():
    """Test updating an existing toolset."""
    console.print("\n[bold blue]Testing toolset update[/bold blue]\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "test.mci.json"

        # Create schema with existing toolsets
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": ["weather-tools", "analytics"],
        }

        schema_file.write_text(json.dumps(schema_content, indent=2))
        console.print(f"[green]✓[/green] Created test file with existing toolsets")

        # Display initial content
        console.print("\n[yellow]Initial content:[/yellow]")
        console.print(schema_file.read_text())

        # Update weather-tools with filter
        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools", "tags", "weather,forecast")
        editor.save_schema()
        console.print("\n[green]✓[/green] Updated 'weather-tools' with filter")

        # Display final content
        console.print("\n[yellow]Final content:[/yellow]")
        console.print(schema_file.read_text())

        # Verify changes
        with open(schema_file) as f:
            data = json.load(f)

        console.print("\n[bold]Verification:[/bold]")
        console.print(f"  Toolsets count: {len(data['toolsets'])}")
        console.print(f"  Toolsets: {data['toolsets']}")

        # Verify no duplication
        assert len(data["toolsets"]) == 2
        assert data["toolsets"][0]["name"] == "weather-tools"
        assert data["toolsets"][0]["filter"] == "tags"
        assert "analytics" in data["toolsets"]

        console.print("\n[bold green]✅ Update test passed![/bold green]\n")


def test_all_filter_types():
    """Test all supported filter types."""
    console.print("\n[bold blue]Testing all filter types[/bold blue]\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "test.mci.json"

        # Create initial schema
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }

        schema_file.write_text(json.dumps(schema_content, indent=2))

        editor = SchemaEditor()

        # Test 'only' filter
        editor.load_schema(str(schema_file))
        editor.add_toolset("toolset1", "only", "Tool1,Tool2")
        editor.save_schema()
        console.print("[green]✓[/green] Added toolset with 'only' filter")

        # Test 'except' filter
        editor.load_schema(str(schema_file))
        editor.add_toolset("toolset2", "except", "BadTool")
        editor.save_schema()
        console.print("[green]✓[/green] Added toolset with 'except' filter")

        # Test 'tags' filter
        editor.load_schema(str(schema_file))
        editor.add_toolset("toolset3", "tags", "api,database")
        editor.save_schema()
        console.print("[green]✓[/green] Added toolset with 'tags' filter")

        # Test 'withoutTags' filter
        editor.load_schema(str(schema_file))
        editor.add_toolset("toolset4", "withoutTags", "deprecated")
        editor.save_schema()
        console.print("[green]✓[/green] Added toolset with 'withoutTags' filter")

        # Display final content
        console.print("\n[yellow]Final content:[/yellow]")
        console.print(schema_file.read_text())

        # Verify all filters
        with open(schema_file) as f:
            data = json.load(f)

        console.print("\n[bold]Verification:[/bold]")
        for i, toolset in enumerate(data["toolsets"], 1):
            console.print(f"  Toolset {i}: {toolset}")

        assert len(data["toolsets"]) == 4
        assert data["toolsets"][0]["filter"] == "only"
        assert data["toolsets"][1]["filter"] == "except"
        assert data["toolsets"][2]["filter"] == "tags"
        assert data["toolsets"][3]["filter"] == "withoutTags"

        console.print("\n[bold green]✅ All filter types test passed![/bold green]\n")


if __name__ == "__main__":
    console.print("\n[bold cyan]========================================[/bold cyan]")
    console.print("[bold cyan]  MCI Add Command - Manual Tests[/bold cyan]")
    console.print("[bold cyan]========================================[/bold cyan]")

    try:
        test_add_to_json()
        test_add_to_yaml()
        test_update_existing_toolset()
        test_all_filter_types()

        console.print("\n[bold green]✅ All manual tests passed successfully![/bold green]\n")
    except AssertionError as e:
        console.print(f"\n[bold red]❌ Test failed: {e}[/bold red]\n")
        raise
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]\n")
        raise
