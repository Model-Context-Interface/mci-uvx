"""
list.py - List command for displaying available tools

This module implements the `list` command for the MCI CLI, which displays
all available tools in the current MCI configuration with support for
filtering, multiple output formats, and verbose mode.
"""

import click
from mcipy import MCIClientError
from rich.console import Console

from mci.cli.formatters import JSONFormatter, TableFormatter, YAMLFormatter
from mci.core.file_finder import MCIFileFinder
from mci.core.mci_client import MCIClientWrapper
from mci.core.tool_manager import ToolManager
from mci.utils.error_handler import ErrorHandler


@click.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    default=None,
    help="Path to MCI schema file (defaults to mci.json or mci.yaml in current directory)",
)
@click.option(
    "--filter",
    type=str,
    default=None,
    help="Filter tools (format: type:value1,value2 - e.g., tags:api,database)",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed tool information including tags, parameters, etc.",
)
def list_command(file: str | None, filter: str | None, format: str, verbose: bool):
    """
    List available tools from the MCI configuration.

    Displays all tools defined in the MCI schema file, with support for
    filtering, multiple output formats (table, JSON, YAML), and verbose mode.

    The list command uses the same tool loading and filtering logic as the
    run command, ensuring consistency between what is listed and what will
    actually be available when running the MCP server.

    Examples:

        # List all tools in table format
        mcix list

        # List tools from specific file
        mcix list --file=./custom.mci.json

        # List tools with filter
        mcix list --filter=tags:api,database

        # List tools with verbose output
        mcix list --verbose

        # Export tools to JSON file
        mcix list --format=json

        # Export tools to YAML file with verbose info
        mcix list --format=yaml --verbose
    """
    console = Console()

    try:
        # Find MCI file
        if file is None:
            finder = MCIFileFinder()
            file = finder.find_mci_file()
            if file is None:
                console.print(
                    "[red]✗[/red] No MCI schema file found. "
                    "Run 'mcix install' to create one or specify --file.",
                    style="red",
                )
                raise click.Abort()

        # Load schema using MCIClientWrapper
        try:
            client = MCIClientWrapper(file)
        except MCIClientError as e:
            console.print(ErrorHandler.format_mci_client_error(e))
            raise click.Abort() from e
        except Exception as e:
            console.print(ErrorHandler.format_generic_error(e))
            raise click.Abort() from e

        # Get tools (with or without filter)
        if filter:
            try:
                tools = ToolManager.apply_filter_spec(client, filter)
            except ValueError as e:
                console.print(f"[red]✗[/red] Invalid filter: {e}", style="red")
                raise click.Abort() from e
        else:
            tools = client.get_tools()

        # Format and display output
        if format == "table":
            # Display table to console
            output = TableFormatter.format(tools, verbose=verbose)
            if isinstance(output, list):
                # Verbose mode returns list of Rich markup strings
                for line in output:
                    console.print(line)
            else:
                # Basic mode returns a Table object
                console.print(output)

        elif format == "json":
            # Write to JSON file
            filters_applied = [filter] if filter else []
            filename = JSONFormatter.format_to_file(
                tools=tools,
                mci_file=file,
                filters_applied=filters_applied,
                verbose=verbose,
            )
            console.print(f"[green]✓[/green] Tools exported to: {filename}")

        elif format == "yaml":
            # Write to YAML file
            filters_applied = [filter] if filter else []
            filename = YAMLFormatter.format_to_file(
                tools=tools,
                mci_file=file,
                filters_applied=filters_applied,
                verbose=verbose,
            )
            console.print(f"[green]✓[/green] Tools exported to: {filename}")

    except click.Abort:
        raise
    except MCIClientError as e:
        console.print(ErrorHandler.format_mci_client_error(e))
        raise click.Abort() from e
    except Exception as e:
        console.print(ErrorHandler.format_generic_error(e))
        raise click.Abort() from e
