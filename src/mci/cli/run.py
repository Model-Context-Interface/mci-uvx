"""
run.py - Run command for starting MCP servers from MCI schemas

This module implements the `mcix run` command, which launches an MCP server
over STDIO that dynamically serves tools from an MCI schema file. The server
loads tools using MCIClient, converts them to MCP format, and delegates
execution back to MCIClient.
"""

import asyncio
import os

import click
from mcipy import MCIClientError
from rich.console import Console

from mci.core.dynamic_server import run_server
from mci.core.file_finder import MCIFileFinder
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
def run(file: str | None, filter: str | None):
    """
    Run an MCP server that serves tools from an MCI schema.

    Launches an MCP server over STDIO that dynamically loads and serves tools
    from the specified MCI schema file. The server uses MCIClient to load tools
    (including toolsets and environment variable templating), converts them to
    MCP format, and delegates execution back to MCIClient.

    The server supports:
    - Loading tools from JSON/YAML MCI schemas
    - Tool filtering by name, tags, and toolsets
    - Environment variable templating
    - Graceful shutdown on Ctrl+C

    Examples:

        # Run server with default mci.json or mci.yaml
        mcix run

        # Run server with specific file
        mcix run --file=./custom.mci.json

        # Run server with filtered tools
        mcix run --filter=tags:api,database

        # Run server with only specific tools
        mcix run --filter=only:tool1,tool2

        # Run server excluding specific tools
        mcix run --filter=except:tool3,tool4

        # Run server with tools from specific toolsets
        mcix run --filter=toolsets:weather,database
    """
    console = Console()

    try:
        # Step 1: Find MCI file
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

        # Step 2: Validate filter spec if provided
        if filter:
            # Validate filter format early to provide better error messages
            from mci.core.tool_manager import ToolManager

            try:
                ToolManager.parse_filter_spec(filter)
            except ValueError as e:
                console.print(f"[red]✗[/red] Invalid filter: {e}", style="red")
                raise click.Abort() from e

        # Step 3: Gather environment variables for templating
        env_vars = dict(os.environ)

        # Step 4: Display startup message
        console.print("[green]⚡[/green] Starting MCP server...", style="bold green")
        console.print(f"[cyan]📄 Schema:[/cyan] {file}")
        if filter:
            console.print(f"[cyan]🔍 Filter:[/cyan] {filter}")
        console.print()
        console.print("[dim]Press Ctrl+C to stop the server[/dim]")
        console.print()

        # Step 5: Run the server (this blocks until Ctrl+C)
        asyncio.run(run_server(file, filter, env_vars))

    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        console.print()
        console.print("[yellow]⏹[/yellow] Server stopped by user", style="yellow")
    except click.Abort:
        raise
    except MCIClientError as e:
        console.print()
        console.print(ErrorHandler.format_mci_client_error(e))
        raise click.Abort() from e
    except Exception as e:
        console.print()
        console.print(ErrorHandler.format_generic_error(e))
        raise click.Abort() from e
