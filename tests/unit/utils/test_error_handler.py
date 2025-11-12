"""
Unit tests for ErrorHandler class.

Tests error formatting utilities for CLI display.
"""

from mcipy import MCIClientError

from mci.utils.error_handler import ErrorHandler


def test_format_file_not_found_error():
    """Test formatting file not found error."""
    error = MCIClientError("Failed to load schema from test.json: [Errno 2] No such file or directory: 'test.json'")
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    assert "❌" in formatted
    assert "Schema file not found" in formatted
    assert "💡 Suggestions:" in formatted
    assert "mcix install" in formatted


def test_format_unsupported_file_extension_error():
    """Test formatting unsupported file extension error."""
    msg = (
        "Failed to load schema from file.txt: Unsupported file extension '.txt'. "
        "Supported extensions: .json, .yaml, .yml"
    )
    error = MCIClientError(msg)
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    assert "❌" in formatted
    assert "Unsupported file format" in formatted
    assert ".json" in formatted
    assert ".yaml" in formatted


def test_format_schema_load_error():
    """Test formatting schema loading error."""
    error = MCIClientError("Failed to load schema from test.json: Invalid JSON syntax")
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    assert "❌" in formatted
    assert "Failed to load schema" in formatted
    assert "mcix validate" in formatted


def test_format_tool_not_found_error():
    """Test formatting tool not found error."""
    error = MCIClientError("Tool not found: nonexistent_tool")
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    assert "❌" in formatted
    assert "Tool not found" in formatted
    assert "mcix list" in formatted


def test_format_template_variable_error():
    """Test formatting template variable error."""
    error = MCIClientError("Template variable not found: env.API_KEY")
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    assert "❌" in formatted
    assert "Missing template variable" in formatted
    assert "environment variables" in formatted


def test_format_validation_error():
    """Test formatting validation error."""
    error = MCIClientError("Validation error: Missing required field 'name'")
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    assert "❌" in formatted
    assert "Schema validation error" in formatted
    assert "mcix validate" in formatted


def test_format_generic_mci_error():
    """Test formatting generic MCIClientError."""
    error = MCIClientError("Some unexpected error occurred")
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    assert "❌" in formatted
    assert "Some unexpected error occurred" in formatted


def test_format_generic_error():
    """Test formatting generic exception."""
    error = ValueError("Invalid value provided")
    
    formatted = ErrorHandler.format_generic_error(error)
    
    assert "❌" in formatted
    assert "ValueError" in formatted
    assert "Invalid value provided" in formatted


def test_format_file_not_found_helper():
    """Test file not found error helper."""
    formatted = ErrorHandler.format_file_not_found_error("mci.json")
    
    assert "❌" in formatted
    assert "File not found: mci.json" in formatted
    assert "mcix install" in formatted
    assert "💡 Suggestions:" in formatted


def test_format_validation_error_helper():
    """Test validation error helper."""
    formatted = ErrorHandler.format_validation_error("Missing required field: name")
    
    assert "❌" in formatted
    assert "Validation Error" in formatted
    assert "Missing required field: name" in formatted
    assert "mcix validate" in formatted


def test_error_messages_contain_helpful_suggestions():
    """Test that error messages include helpful suggestions."""
    test_cases = [
        (
            MCIClientError("No such file or directory"),
            ["mcix install", "file path"]
        ),
        (
            MCIClientError("Tool not found: test_tool"),
            ["mcix list", "tool name"]
        ),
        (
            MCIClientError("Template variable not found: env.VAR"),
            ["environment variables", "{{env.VARIABLE}}"]
        ),
    ]
    
    for error, expected_hints in test_cases:
        formatted = ErrorHandler.format_mci_client_error(error)
        for hint in expected_hints:
            assert hint.lower() in formatted.lower(), f"Expected hint '{hint}' not found in error message"


def test_error_messages_are_user_friendly():
    """Test that error messages use friendly language."""
    error = MCIClientError("Failed to load schema from test.json: [Errno 2] No such file or directory")
    
    formatted = ErrorHandler.format_mci_client_error(error)
    
    # Should not be overly technical
    assert "❌" in formatted  # Uses emoji for visual clarity
    assert "💡" in formatted  # Uses emoji for suggestions
    
    # Should provide actionable suggestions
    assert "Run 'mci" in formatted  # Suggests specific commands


def test_multiple_error_types_formatting():
    """Test that different error types are formatted appropriately."""
    errors = [
        MCIClientError("No such file or directory: test.json"),
        MCIClientError("Unsupported file extension '.txt'"),
        MCIClientError("Failed to load schema: Invalid JSON"),
        MCIClientError("Tool not found: my_tool"),
        MCIClientError("Template variable not found: env.KEY"),
        MCIClientError("Validation failed: missing field"),
    ]
    
    for error in errors:
        formatted = ErrorHandler.format_mci_client_error(error)
        # Each should have error indicator
        assert "❌" in formatted
        # Each should be non-empty
        assert len(formatted) > 10
        # Each should have some helpful content
        assert "Error" in formatted or "error" in formatted
