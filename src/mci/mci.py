"""
mci.py - Main entry point for the MCI CLI Tool

This module provides the main CLI interface for managing MCI (Model Context Interface)
schemas and dynamically running MCP servers using defined MCI toolsets.
"""

import click


@click.group()
@click.version_option()
def main():
    """
    MCI CLI - Manage Model Context Interface schemas and run MCP servers.

    Use 'mci COMMAND --help' for more information on a specific command.
    """
    pass


if __name__ == "__main__":
    main()
