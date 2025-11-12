"""
validate.py - CLI command to validate MCI schemas

This module provides the `mcix validate` command which checks MCI schema
correctness using mci-py's built-in validation and provides user-friendly
error and warning messages.
"""

import os
import sys

import click

from mci.core.file_finder import MCIFileFinder
from mci.core.validator import MCIValidator
from mci.utils.error_formatter import ErrorFormatter


@click.command()
@click.option(
    "--file",
    "-f",
    default=None,
    help="Path to MCI schema file (default: auto-discover mci.json/mci.yaml)",
)
@click.option(
    "--env",
    "-e",
    multiple=True,
    help="Environment variables in KEY=VALUE format (can be specified multiple times)",
)
def validate(file: str | None, env: tuple[str, ...]) -> None:
    """
    Validate MCI schema file for correctness.

    This command validates an MCI schema file using mci-py's built-in validation
    engine. It checks for:
    - Schema structure and syntax
    - Required fields and data types
    - Valid references and tool definitions

    Additionally, it provides warnings for:
    - Missing toolset files
    - MCP commands not in PATH

    Examples:
        mcix validate                        # Validate default mci.json/mci.yaml
        mcix validate --file custom.mci.json # Validate specific file
        mcix validate -e API_KEY=123         # Provide environment variables
    """
    formatter = ErrorFormatter()

    # Parse environment variables
    env_vars = {}
    for env_pair in env:
        if "=" in env_pair:
            key, value = env_pair.split("=", 1)
            env_vars[key] = value
        else:
            formatter.console.print(
                f"[yellow]Warning: Invalid environment variable format: {env_pair}. "
                "Expected KEY=VALUE.[/yellow]"
            )

    # Merge environment variables: user-provided env vars override system environment variables
    merged_env = {**os.environ, **env_vars}

    # Find the schema file
    if file is None:
        file_finder = MCIFileFinder()
        file = file_finder.find_mci_file()
        if file is None:
            formatter.console.print("[red]❌ No MCI schema file found in current directory[/red]\n")
            formatter.console.print(
                "[yellow]💡 Run 'mcix install' to create a default mci.json file[/yellow]"
            )
            sys.exit(1)

    # Validate the schema
    validator = MCIValidator(file_path=file, env_vars=merged_env)

    try:
        result = validator.validate_schema()

        # Display errors
        if result.errors:
            formatter.format_validation_errors(result.errors)
            formatter.console.print(
                "\n[yellow]💡 Fix the errors above and run 'mcix validate' again[/yellow]\n"
            )
            sys.exit(1)

        # Display warnings (if any)
        if result.warnings:
            formatter.format_validation_warnings(result.warnings)

        # Display success message
        formatter.format_validation_success(file)

        # Exit with appropriate code
        sys.exit(0)

    except FileNotFoundError as e:
        formatter.format_mci_error(f"File not found: {str(e)}")
        sys.exit(1)
    except Exception as e:
        formatter.format_mci_error(f"Unexpected error: {str(e)}")
        sys.exit(1)


# Allow running as script
if __name__ == "__main__":
    validate()
