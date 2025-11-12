"""
envs.py - Environment variables command for displaying required env vars

This module implements the `envs` command for the MCI CLI, which scans
the MCI configuration and displays all environment variables referenced
in templates across tools, toolsets, and MCP servers.
"""

import json
from pathlib import Path

import click
import yaml
from mcipy import MCIClientError
from rich.console import Console
from rich.table import Table

from mci.cli.formatters.env_formatter import EnvFormatter
from mci.core.file_finder import MCIFileFinder
from mci.utils.env_scanner import EnvScanner
from mci.utils.error_handler import ErrorHandler


def extract_env_vars_from_schema(schema_path: str) -> dict[str, list[str]]:
    """
    Extract all environment variables from a schema file and its referenced files.

    This function loads the main schema file and scans it along with all
    referenced toolsets and MCP servers to find environment variable references.

    Args:
        schema_path: Path to the main MCI schema file

    Returns:
        Dictionary mapping variable names to list of locations where used
        (e.g., {"API_KEY": ["main", "weather-toolset"]})

    Raises:
        FileNotFoundError: If schema file or referenced files are not found
        ValueError: If schema file is invalid
    """
    env_vars: dict[str, set[str]] = {}
    schema_dir = Path(schema_path).parent.resolve()

    # Load main schema
    with open(schema_path) as f:
        if schema_path.endswith((".yaml", ".yml")):
            main_schema = yaml.safe_load(f)
        else:
            main_schema = json.load(f)

    # Scan main schema (excluding mcp_servers which we'll scan separately)
    main_schema_without_mcp = {k: v for k, v in main_schema.items() if k != "mcp_servers"}
    main_env_vars = EnvScanner.scan_dict(main_schema_without_mcp)
    for var in main_env_vars:
        if var not in env_vars:
            env_vars[var] = set()
        env_vars[var].add("main")

    # Get library directory for toolsets
    library_dir = main_schema.get("libraryDir", "mci")
    lib_path = schema_dir / library_dir

    # Scan registered toolsets
    toolsets = main_schema.get("toolsets", [])
    for toolset_ref in toolsets:
        toolset_name = toolset_ref if isinstance(toolset_ref, str) else toolset_ref.get("name")
        if not toolset_name:
            continue

        # Try to find toolset file
        toolset_file = _find_toolset_file(lib_path, toolset_name)
        if toolset_file:
            try:
                with open(toolset_file) as f:
                    if toolset_file.suffix in {".yaml", ".yml"}:
                        toolset_schema = yaml.safe_load(f)
                    else:
                        toolset_schema = json.load(f)

                # Scan toolset
                toolset_env_vars = EnvScanner.scan_dict(toolset_schema)
                for var in toolset_env_vars:
                    if var not in env_vars:
                        env_vars[var] = set()
                    env_vars[var].add(toolset_name)
            except Exception as e:
                # Warn but continue if toolset file is invalid
                console = Console()
                console.print(
                    f"[yellow]⚠[/yellow] Warning: Could not load toolset '{toolset_name}': {e}",
                    style="yellow",
                )

    # Scan MCP servers
    mcp_servers = main_schema.get("mcp_servers", {})
    if isinstance(mcp_servers, dict):
        for server_name, server_config in mcp_servers.items():
            if isinstance(server_config, dict):
                server_env_vars = EnvScanner.scan_dict(server_config)
                for var in server_env_vars:
                    if var not in env_vars:
                        env_vars[var] = set()
                    env_vars[var].add(f"mcp:{server_name}")

    # Convert sets to sorted lists
    result = {var: sorted(locations) for var, locations in env_vars.items()}
    return result


def _find_toolset_file(lib_path: Path, toolset_name: str) -> Path | None:
    """
    Find a toolset file in the library directory.

    Args:
        lib_path: Path to the library directory
        toolset_name: Name of the toolset

    Returns:
        Path to the toolset file if found, None otherwise
    """
    if not lib_path.exists():
        return None

    # Try various file patterns
    patterns = [
        f"{toolset_name}.mci.json",
        f"{toolset_name}.mci.yaml",
        f"{toolset_name}.mci.yml",
        f"{toolset_name}.json",
        f"{toolset_name}.yaml",
        f"{toolset_name}.yml",
    ]

    for pattern in patterns:
        file_path = lib_path / pattern
        if file_path.exists() and file_path.is_file():
            return file_path

    # Check if it's a directory with a schema file
    dir_path = lib_path / toolset_name
    if dir_path.exists() and dir_path.is_dir():
        for pattern in patterns:
            file_path = dir_path / pattern
            if file_path.exists() and file_path.is_file():
                return file_path

    return None


@click.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    default=None,
    help="Path to MCI schema file (defaults to mci.json or mci.yaml in current directory)",
)
@click.option(
    "--format",
    type=click.Choice(["table", "env"], case_sensitive=False),
    default="table",
    help="Output format (default: table)",
)
def envs_command(file: str | None, format: str):
    """
    List all environment variables used in the MCI configuration.

    Scans the main schema file, referenced toolsets, and MCP servers to find
    all environment variable references in templates ({{env.VARIABLE}}).

    Outputs a list of all required environment variables with their locations,
    helping you understand what credentials and configuration are needed.

    Examples:

        # Show environment variables in table format
        mci envs

        # Generate .env.example.mci file
        mci envs --format=env

        # Scan specific schema file
        mci envs --file=custom.mci.json
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

        # Extract environment variables
        try:
            env_vars = extract_env_vars_from_schema(file)
        except FileNotFoundError as e:
            console.print(f"[red]✗[/red] File not found: {e}", style="red")
            raise click.Abort() from e
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            console.print(f"[red]✗[/red] Invalid schema file: {e}", style="red")
            raise click.Abort() from e
        except Exception as e:
            console.print(ErrorHandler.format_generic_error(e))
            raise click.Abort() from e

        # Check if any variables were found
        if not env_vars:
            if format == "table":
                console.print("[yellow]ℹ[/yellow] No environment variables found in schema.")
            else:
                console.print(
                    "[yellow]ℹ[/yellow] No environment variables found. Skipping file generation."
                )
            return

        # Format and display output
        if format == "table":
            # Display table to console
            table = Table(
                title=f"🔐 Environment Variables ({len(env_vars)})",
                show_header=True,
                header_style="bold cyan",
            )

            table.add_column("Variable", style="green", no_wrap=True)
            table.add_column("Used In", style="blue")

            # Sort by variable name
            for var_name in sorted(env_vars.keys()):
                locations = env_vars[var_name]
                locations_str = ", ".join(locations)
                table.add_row(var_name, locations_str)

            console.print(table)

        elif format == "env":
            # Write to .env.example.mci file
            filename = EnvFormatter.format_to_file(env_vars)
            console.print(f"[green]✓[/green] Environment variables exported to: {filename}")
            console.print("[dim]Copy this file to .env.mci and fill in your values[/dim]")

    except click.Abort:
        raise
    except MCIClientError as e:
        console.print(ErrorHandler.format_mci_client_error(e))
        raise click.Abort() from e
    except Exception as e:
        console.print(ErrorHandler.format_generic_error(e))
        raise click.Abort() from e
