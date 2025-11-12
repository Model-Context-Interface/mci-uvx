"""
error_handler.py - Error handling utilities for CLI

This module provides utilities for formatting errors from mci-py
in a CLI-friendly way, with helpful messages and suggestions.
"""

from mcipy import MCIClientError


class ErrorHandler:
    """
    Handles and formats errors for CLI display.

    This class provides methods to format exceptions from mci-py
    into user-friendly error messages suitable for terminal output.
    """

    @staticmethod
    def format_mci_client_error(error: MCIClientError) -> str:
        """
        Format MCIClientError for CLI display.

        Converts technical error messages from MCIClient into
        user-friendly messages with helpful suggestions.

        Args:
            error: MCIClientError exception from mci-py

        Returns:
            Formatted error message string

        Example:
            >>> from mcipy import MCIClientError
            >>> try:
            ...     # Some MCIClient operation
            ...     pass
            ... except MCIClientError as e:
            ...     msg = ErrorHandler.format_mci_client_error(e)
            ...     print(msg)
        """
        error_str = str(error)

        # Check for common error patterns and provide helpful messages
        if "No such file or directory" in error_str:
            return (
                f"❌ Schema file not found\n\n"
                f"Error: {error_str}\n\n"
                f"💡 Suggestions:\n"
                f"  • Check that the file path is correct\n"
                f"  • Run 'mcix install' to create a default mci.json file\n"
                f"  • Use --file option to specify a different schema file"
            )

        if "Unsupported file extension" in error_str:
            return (
                f"❌ Unsupported file format\n\n"
                f"Error: {error_str}\n\n"
                f"💡 Supported formats:\n"
                f"  • .json (JSON format)\n"
                f"  • .yaml or .yml (YAML format)"
            )

        if "Failed to load schema" in error_str:
            # Try to extract the specific parse error
            return (
                f"❌ Failed to load schema\n\n"
                f"Error: {error_str}\n\n"
                f"💡 Suggestions:\n"
                f"  • Check that the file contains valid JSON or YAML\n"
                f"  • Run 'mcix validate' to see detailed validation errors\n"
                f"  • Check for syntax errors like missing commas or brackets"
            )

        if "Tool not found" in error_str:
            return (
                f"❌ Tool not found\n\n"
                f"Error: {error_str}\n\n"
                f"💡 Suggestions:\n"
                f"  • Run 'mcix list' to see all available tools\n"
                f"  • Check the tool name for typos\n"
                f"  • Ensure the tool is defined in your schema"
            )

        if "Template variable not found" in error_str:
            return (
                f"❌ Missing template variable\n\n"
                f"Error: {error_str}\n\n"
                f"💡 Suggestions:\n"
                f"  • Set required environment variables before running the tool\n"
                f"  • Check your schema for {{{{env.VARIABLE}}}} placeholders\n"
                f"  • Use --env option to provide environment variables"
            )

        if "validation" in error_str.lower() or "invalid" in error_str.lower():
            return (
                f"❌ Schema validation error\n\n"
                f"Error: {error_str}\n\n"
                f"💡 Suggestions:\n"
                f"  • Run 'mcix validate' for detailed validation errors\n"
                f"  • Check that all required fields are present\n"
                f"  • Verify that field types match the schema specification"
            )

        # Default formatting for other errors
        return f"❌ Error\n\n{error_str}"

    @staticmethod
    def format_generic_error(error: Exception) -> str:
        """
        Format a generic exception for CLI display.

        Args:
            error: Any Python exception

        Returns:
            Formatted error message string

        Example:
            >>> try:
            ...     # Some operation
            ...     pass
            ... except Exception as e:
            ...     msg = ErrorHandler.format_generic_error(e)
            ...     print(msg)
        """
        error_str = str(error)
        error_type = type(error).__name__

        return f"❌ {error_type}\n\n{error_str}"

    @staticmethod
    def format_file_not_found_error(file_path: str) -> str:
        """
        Format a file not found error with helpful suggestions.

        Args:
            file_path: Path to the file that was not found

        Returns:
            Formatted error message string

        Example:
            >>> msg = ErrorHandler.format_file_not_found_error("mci.json")
            >>> print(msg)
        """
        return (
            f"❌ File not found: {file_path}\n\n"
            f"💡 Suggestions:\n"
            f"  • Run 'mcix install' to create a default mci.json file\n"
            f"  • Check that you're in the correct directory\n"
            f"  • Use --file option to specify a different schema file"
        )

    @staticmethod
    def format_validation_error(message: str) -> str:
        """
        Format a validation error message.

        Args:
            message: Validation error message

        Returns:
            Formatted error message string

        Example:
            >>> msg = ErrorHandler.format_validation_error("Missing required field: name")
            >>> print(msg)
        """
        return (
            f"❌ Validation Error\n\n"
            f"{message}\n\n"
            f"💡 Run 'mcix validate' for detailed validation information"
        )
