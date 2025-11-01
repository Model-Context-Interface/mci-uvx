"""
Unit tests for ErrorFormatter class.

Tests error and warning formatting utilities for CLI display.
"""

import pytest
from io import StringIO

from rich.console import Console

from mci.utils.error_formatter import (
    ErrorFormatter,
    ValidationError,
    ValidationWarning,
)


@pytest.fixture
def formatter():
    """Create an ErrorFormatter with StringIO console for testing."""
    console = Console(file=StringIO(), force_terminal=True)
    return ErrorFormatter(console)


def test_format_validation_errors_with_single_error(formatter):
    """Test formatting a single validation error."""
    errors = [ValidationError(message="Missing required field: name")]
    formatter.format_validation_errors(errors)
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert "❌ Validation Errors" in output
    assert "Missing required field: name" in output
    assert "Schema Validation Failed" in output


def test_format_validation_errors_with_multiple_errors(formatter):
    """Test formatting multiple validation errors."""
    errors = [
        ValidationError(message="Missing required field: name"),
        ValidationError(message="Invalid type for field: age", location="tools[0]"),
    ]
    formatter.format_validation_errors(errors)
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert "❌ Validation Errors" in output
    assert "Missing required field: name" in output
    assert "Invalid type for field: age" in output
    assert "[tools[0]]" in output


def test_format_validation_errors_with_empty_list(formatter):
    """Test formatting with empty error list (should not output anything)."""
    formatter.format_validation_errors([])
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert output == ""


def test_format_validation_warnings_with_single_warning(formatter):
    """Test formatting a single validation warning."""
    warnings = [
        ValidationWarning(
            message="Toolset file not found: weather.mci.json",
            suggestion="Create the file or update your schema",
        )
    ]
    formatter.format_validation_warnings(warnings)
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert "⚠️  Validation Warnings" in output
    assert "Toolset file not found" in output
    assert "💡 Create the file or update your schema" in output


def test_format_validation_warnings_with_no_suggestion(formatter):
    """Test formatting a warning without suggestion."""
    warnings = [ValidationWarning(message="Potential issue detected")]
    formatter.format_validation_warnings(warnings)
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert "⚠️  Validation Warnings" in output
    assert "Potential issue detected" in output


def test_format_validation_warnings_with_empty_list(formatter):
    """Test formatting with empty warning list (should not output anything)."""
    formatter.format_validation_warnings([])
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert output == ""


def test_format_validation_success(formatter):
    """Test formatting validation success message."""
    formatter.format_validation_success("mci.json")
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert "✅ Schema is valid!" in output
    assert "File: mci.json" in output
    assert "Validation Successful" in output


def test_format_mci_error(formatter):
    """Test formatting an MCI error message."""
    formatter.format_mci_error("Failed to load schema: Invalid JSON")
    
    output = formatter.console.file.getvalue()  # type: ignore[attr-defined]
    assert "❌ MCI Error" in output
    assert "Failed to load schema: Invalid JSON" in output


def test_error_formatter_default_console():
    """Test ErrorFormatter with default console."""
    formatter = ErrorFormatter()
    assert formatter.console is not None
    
    # Should not raise any errors
    formatter.format_validation_success("test.json")


def test_validation_error_with_location():
    """Test ValidationError with location."""
    error = ValidationError(message="Test error", location="tools[0].name")
    assert error.message == "Test error"
    assert error.location == "tools[0].name"


def test_validation_error_without_location():
    """Test ValidationError without location."""
    error = ValidationError(message="Test error")
    assert error.message == "Test error"
    assert error.location is None


def test_validation_warning_with_suggestion():
    """Test ValidationWarning with suggestion."""
    warning = ValidationWarning(message="Test warning", suggestion="Fix it")
    assert warning.message == "Test warning"
    assert warning.suggestion == "Fix it"


def test_validation_warning_without_suggestion():
    """Test ValidationWarning without suggestion."""
    warning = ValidationWarning(message="Test warning")
    assert warning.message == "Test warning"
    assert warning.suggestion is None
