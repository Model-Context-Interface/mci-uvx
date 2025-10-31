"""
error_formatter.py - Format validation errors and warnings for CLI display

This module provides utilities for formatting validation errors and warnings
in a user-friendly way with color-coded output using Rich library.
"""

from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


@dataclass
class ValidationError:
    """Represents a validation error with message and optional location."""

    message: str
    location: str | None = None


@dataclass
class ValidationWarning:
    """Represents a validation warning with message and optional suggestion."""

    message: str
    suggestion: str | None = None


class ErrorFormatter:
    """
    Formats validation errors and warnings for CLI display.

    This class provides methods to format validation results using the Rich library
    for beautiful, color-coded terminal output.
    """

    def __init__(self, console: Console | None = None):
        """
        Initialize the ErrorFormatter.

        Args:
            console: Rich Console instance. Defaults to a new Console if not provided.
        """
        self.console: Console = console if console is not None else Console()

    def format_validation_errors(self, errors: list[ValidationError]) -> None:
        """
        Display validation errors with color-coded output.

        Args:
            errors: List of ValidationError objects to display

        Example:
            >>> formatter = ErrorFormatter()
            >>> errors = [ValidationError(message="Missing required field: name")]
            >>> formatter.format_validation_errors(errors)
        """
        if not errors:
            return

        self.console.print()
        error_text = Text()
        error_text.append("❌ Validation Errors\n\n", style="bold red")

        for i, error in enumerate(errors, 1):
            error_text.append(f"{i}. ", style="red")
            if error.location:
                error_text.append(f"[{error.location}] ", style="yellow")
            error_text.append(f"{error.message}\n", style="red")

        panel = Panel(
            error_text,
            title="[bold red]Schema Validation Failed",
            border_style="red",
            expand=False,
        )
        self.console.print(panel)

    def format_validation_warnings(self, warnings: list[ValidationWarning]) -> None:
        """
        Display validation warnings with color-coded output.

        Args:
            warnings: List of ValidationWarning objects to display

        Example:
            >>> formatter = ErrorFormatter()
            >>> warnings = [ValidationWarning(
            ...     message="Toolset file not found: weather.mci.json",
            ...     suggestion="Create the file or update your schema"
            ... )]
            >>> formatter.format_validation_warnings(warnings)
        """
        if not warnings:
            return

        self.console.print()
        warning_text = Text()
        warning_text.append("⚠️  Validation Warnings\n\n", style="bold yellow")

        for i, warning in enumerate(warnings, 1):
            warning_text.append(f"{i}. ", style="yellow")
            warning_text.append(f"{warning.message}\n", style="yellow")
            if warning.suggestion:
                warning_text.append(f"   💡 {warning.suggestion}\n", style="cyan dim")

        panel = Panel(
            warning_text,
            title="[bold yellow]Warnings",
            border_style="yellow",
            expand=False,
        )
        self.console.print(panel)

    def format_validation_success(self, file_path: str) -> None:
        """
        Display validation success message.

        Args:
            file_path: Path to the validated file

        Example:
            >>> formatter = ErrorFormatter()
            >>> formatter.format_validation_success("mci.json")
        """
        self.console.print()
        success_text = Text()
        success_text.append("✅ Schema is valid!\n\n", style="bold green")
        success_text.append(f"File: {file_path}", style="green")

        panel = Panel(
            success_text,
            title="[bold green]Validation Successful",
            border_style="green",
            expand=False,
        )
        self.console.print(panel)
        self.console.print()

    def format_mci_error(self, error_message: str) -> None:
        """
        Display an MCIClient error message.

        Args:
            error_message: Error message from MCIClient

        Example:
            >>> formatter = ErrorFormatter()
            >>> formatter.format_mci_error("Failed to load schema: Invalid JSON")
        """
        self.console.print()
        error_text = Text()
        error_text.append("❌ MCI Error\n\n", style="bold red")
        error_text.append(error_message, style="red")

        panel = Panel(
            error_text,
            title="[bold red]Error",
            border_style="red",
            expand=False,
        )
        self.console.print(panel)
        self.console.print()
