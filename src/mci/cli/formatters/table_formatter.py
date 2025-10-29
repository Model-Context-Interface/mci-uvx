"""
table_formatter.py - Rich table formatter for CLI output

This module provides formatting for displaying tools in Rich terminal tables
with support for both basic and verbose output modes.
"""

from rich.console import Console
from rich.table import Table

from mcipy.models import Tool


class TableFormatter:
    """
    Formats tool information as Rich terminal tables.

    This class provides methods to format tool lists into beautiful
    terminal tables using the Rich library, with support for both
    basic and verbose output modes.
    """

    @staticmethod
    def format(tools: list[Tool], verbose: bool = False) -> str:
        """
        Format tools as a Rich table.

        Args:
            tools: List of Tool objects to format
            verbose: Whether to show verbose output with additional metadata

        Returns:
            Formatted table output as a string

        Example:
            >>> formatter = TableFormatter()
            >>> output = formatter.format(tools, verbose=False)
            >>> print(output)
        """
        if verbose:
            return TableFormatter.format_verbose(tools)
        else:
            return TableFormatter.format_basic(tools)

    @staticmethod
    def format_basic(tools: list[Tool]) -> str:
        """
        Format tools in basic table mode.

        Displays a table with columns: Name, Source, Description

        Args:
            tools: List of Tool objects to format

        Returns:
            Formatted basic table output as a string
        """
        console = Console()

        # Create table
        table = Table(
            title=f"🧩 Available Tools ({len(tools)})",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Source", style="blue")
        table.add_column("Description", style="white")

        # Add rows
        for tool in tools:
            name = tool.name
            source = tool.toolset_source or "main"
            description = tool.description or ""

            table.add_row(name, source, description)

        # Render to string
        with console.capture() as capture:
            console.print(table)

        return capture.get()

    @staticmethod
    def format_verbose(tools: list[Tool]) -> str:
        """
        Format tools in verbose mode with detailed information.

        Shows detailed information for each tool including tags,
        parameters, execution type, and other metadata.

        Args:
            tools: List of Tool objects to format

        Returns:
            Formatted verbose output as a string
        """
        console = Console()
        output_lines: list[str] = []

        output_lines.append(f"🧩 Available Tools ({len(tools)}):\n")

        for tool in tools:
            # Tool header
            source = tool.toolset_source or "main"
            output_lines.append(f"[bold green]{tool.name}[/bold green] [blue]({source})[/blue]")

            # Description
            if tool.description:
                output_lines.append(f"├── Description: {tool.description}")

            # Tags
            if tool.tags:
                tags_str = ", ".join(tool.tags)
                # Escape brackets for Rich markup
                output_lines.append(f"├── Tags: \\[{tags_str}]")

            # Execution type
            execution_type = tool.execution.type.value if hasattr(tool.execution.type, "value") else str(tool.execution.type)
            output_lines.append(f"├── Execution: {execution_type}")

            # Parameters from inputSchema
            if tool.inputSchema and "properties" in tool.inputSchema:
                params = tool.inputSchema["properties"]
                required = tool.inputSchema.get("required", [])

                param_strs = []
                for param_name, param_def in params.items():
                    param_type = param_def.get("type", "any")
                    is_required = param_name in required
                    req_indicator = "" if is_required else " (optional)"
                    param_strs.append(f"{param_name} ({param_type}){req_indicator}")

                if param_strs:
                    output_lines.append(f"└── Parameters: {', '.join(param_strs)}")
            else:
                output_lines.append("└── Parameters: none")

            output_lines.append("")  # Empty line between tools

        # Render to string with Rich formatting
        with console.capture() as capture:
            for line in output_lines:
                console.print(line)

        return capture.get()
