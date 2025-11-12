"""
add.py - CLI command to add toolset references to MCI schemas

This module provides the `mcix add` command which adds toolset references
to MCI schema files with optional filtering, while preserving the original
file format (JSON or YAML).
"""

import sys

import click
from rich.console import Console

from mci.core.file_finder import MCIFileFinder
from mci.core.schema_editor import SchemaEditor, parse_add_filter


@click.command()
@click.argument("toolset_name", type=str)
@click.option(
    "--filter",
    "-f",
    default=None,
    help='Filter specification (e.g., "only:Tool1,Tool2" or "tags:api,database")',
)
@click.option(
    "--path",
    "-p",
    default=None,
    help="Path to MCI schema file (default: auto-discover mci.json/mci.yaml)",
)
def add(toolset_name: str, filter: str | None, path: str | None) -> None:
    """
    Add a toolset reference to an MCI schema file.

    This command adds a toolset to the schema's toolsets array. If the toolset
    already exists, it will be updated with the new filter (if provided).
    The original file format (JSON or YAML) is preserved.

    TOOLSET_NAME is the name of the toolset to add.

    Examples:

        \b
        # Add a toolset without filter
        mcix add weather-tools

        \b
        # Add a toolset with "only" filter
        mcix add analytics --filter=only:Tool1,Tool2

        \b
        # Add a toolset with "tags" filter
        mcix add api-tools --filter=tags:api,database

        \b
        # Add to a custom file
        mcix add weather-tools --path=custom.mci.json
    """
    console = Console()

    # Find the schema file
    if path is None:
        file_finder = MCIFileFinder()
        schema_file = file_finder.find_mci_file()
        if schema_file is None:
            console.print("[red]❌ No MCI schema file found in current directory[/red]\n")
            console.print("[yellow]💡 Run 'mcix install' to create a default mci.json file[/yellow]")
            sys.exit(1)
    else:
        schema_file = path

    # Parse filter specification if provided
    filter_type = None
    filter_value = None
    if filter:
        try:
            filter_type, filter_value = parse_add_filter(filter)
        except ValueError as e:
            console.print(f"[red]❌ Invalid filter specification: {e}[/red]\n")
            sys.exit(1)

    # Load, modify, and save the schema
    editor = SchemaEditor()
    try:
        editor.load_schema(schema_file)
        editor.add_toolset(toolset_name, filter_type, filter_value)
        editor.save_schema()

        # Display success message
        console.print(f"[green]✅ Added toolset '{toolset_name}' to {schema_file}[/green]")
        if filter_type and filter_value:
            console.print(f"[dim]   Filter: {filter_type}:{filter_value}[/dim]")

    except FileNotFoundError as e:
        console.print(f"[red]❌ File not found: {e}[/red]\n")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[red]❌ Error: {e}[/red]\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]\n")
        sys.exit(1)


# Allow running as script
if __name__ == "__main__":
    add()
