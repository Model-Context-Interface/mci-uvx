"""
install.py - CLI command for initializing MCI project structure

This module provides the 'install' command which creates a new MCI project
by copying template files and setting up the directory structure.
"""

from importlib.resources import files
from pathlib import Path

import click


def copy_asset(resource_name: str, dest_path: Path, overwrite: bool = False) -> bool:
    """
    Copy an asset file from the package to a destination path.

    Args:
        resource_name: Name of the asset file in src/mci/assets/
        dest_path: Destination path to copy the file to
        overwrite: Whether to overwrite existing files (default: False)

    Returns:
        True if file was copied, False if it already existed and overwrite=False
    """
    if dest_path.exists() and not overwrite:
        return False

    # Get the asset file content using importlib.resources
    asset_files = files("mci.assets")
    asset_file = asset_files.joinpath(resource_name)

    # Read the asset content and write to destination
    content = asset_file.read_text()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content)

    return True


def create_mci_file(format: str = "json") -> None:
    """
    Create the main MCI configuration file (mci.json or mci.yaml).

    Args:
        format: File format, either "json" or "yaml"
    """
    if format == "yaml":
        filename = "mci.yaml"
        asset_name = "mci.yaml"
    else:
        filename = "mci.json"
        asset_name = "mci.json"

    dest_path = Path.cwd() / filename

    if copy_asset(asset_name, dest_path):
        click.echo(f"✓ Created {filename}")
    else:
        click.echo(f"⚠ {filename} already exists, skipping")


def create_mci_directory() -> None:
    """
    Create the ./mci/ directory and update .gitignore.
    """
    mci_dir = Path.cwd() / "mci"
    mci_dir.mkdir(exist_ok=True)
    click.echo("✓ Created ./mci/ directory")

    # Create or update .gitignore
    gitignore_path = mci_dir / ".gitignore"

    if gitignore_path.exists():
        # Check if 'mcp/' already exists in .gitignore
        content = gitignore_path.read_text()
        if "mcp/" not in content:
            # Append mcp/ entry
            with gitignore_path.open("a") as f:
                if not content.endswith("\n"):
                    f.write("\n")
                f.write("mcp/\n")
            click.echo("✓ Updated ./mci/.gitignore with mcp/ entry")
        else:
            click.echo("⚠ ./mci/.gitignore already contains mcp/ entry, skipping")
    else:
        # Create new .gitignore from template
        copy_asset("gitignore", gitignore_path, overwrite=True)
        click.echo("✓ Created ./mci/.gitignore")


def create_example_toolset(format: str = "json") -> None:
    """
    Create the example toolset file in ./mci/ directory.

    Args:
        format: File format, either "json" or "yaml"
    """
    if format == "yaml":
        filename = "example_toolset.mci.yaml"
        asset_name = "example_toolset.mci.yaml"
    else:
        filename = "example_toolset.mci.json"
        asset_name = "example_toolset.mci.json"

    dest_path = Path.cwd() / "mci" / filename

    if copy_asset(asset_name, dest_path):
        click.echo(f"✓ Created ./mci/{filename}")
    else:
        click.echo(f"⚠ ./mci/{filename} already exists, skipping")


@click.command()
@click.option(
    "--yaml",
    is_flag=True,
    help="Create YAML configuration file instead of JSON",
)
def install(yaml: bool):
    """
    Initialize an MCI project structure.

    Creates mci.json (or mci.yaml with --yaml flag), ./mci/ directory,
    example toolset file, and .gitignore configuration.
    """
    click.echo("Initializing MCI project...")
    click.echo()

    format = "yaml" if yaml else "json"

    # Create main configuration file
    create_mci_file(format=format)

    # Create ./mci directory and .gitignore
    create_mci_directory()

    # Create example toolset
    create_example_toolset(format=format)

    click.echo()
    click.echo("✓ MCI project initialized successfully!")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Review the generated configuration files")
    click.echo("  2. Run 'mcix list' to see available tools")
    click.echo("  3. Run 'mcix validate' to check your configuration")
