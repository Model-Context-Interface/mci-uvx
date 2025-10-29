"""
Unit tests for the TableFormatter class.

Tests the Rich table formatting for both basic and verbose output modes.
"""

from mcipy.models import Tool

from mci.cli.formatters.table_formatter import TableFormatter


def test_basic_table():
    """Test basic table format with multiple tools."""
    tools = [
        Tool(
            name="tool1",
            description="First tool",
            tags=["api"],
            execution={"type": "text", "text": "hello"},
        ),
        Tool(
            name="tool2",
            description="Second tool",
            tags=["database"],
            execution={"type": "text", "text": "world"},
        ),
    ]

    output = TableFormatter.format_basic(tools)

    # Check that output contains expected elements
    assert "Available Tools (2)" in output
    assert "tool1" in output
    assert "tool2" in output
    assert "First tool" in output
    assert "Second tool" in output
    assert "main" in output  # Default source


def test_basic_table_empty():
    """Test basic table with empty tools list."""
    tools = []

    output = TableFormatter.format_basic(tools)

    assert "Available Tools (0)" in output


def test_basic_table_with_toolset_source():
    """Test basic table shows toolset source correctly."""
    tool = Tool(
        name="sourced_tool",
        description="Tool from toolset",
        execution={"type": "text", "text": "test"},
        toolset_source="custom-toolset",
    )

    output = TableFormatter.format_basic([tool])

    assert "sourced_tool" in output
    assert "custom-toolset" in output


def test_verbose_table():
    """Test verbose table format with detailed information."""
    tools = [
        Tool(
            name="test_tool",
            description="A test tool",
            tags=["api", "test"],
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "First param"},
                    "param2": {"type": "number", "description": "Second param"},
                },
                "required": ["param1"],
            },
            execution={"type": "text", "text": "Test output"},
        )
    ]

    output = TableFormatter.format_verbose(tools)

    # Check all expected elements are present
    assert "Available Tools (1)" in output
    assert "test_tool" in output
    assert "A test tool" in output
    assert "api, test" in output  # Tags
    assert "text" in output  # Execution type
    assert "param1 (string)" in output
    assert "param2 (number) (optional)" in output


def test_verbose_table_no_parameters():
    """Test verbose format for tool without parameters."""
    tool = Tool(
        name="simple_tool",
        description="Simple tool",
        execution={"type": "text", "text": "output"},
    )

    output = TableFormatter.format_verbose([tool])

    assert "simple_tool" in output
    assert "Parameters: none" in output


def test_verbose_table_no_tags():
    """Test verbose format for tool without tags."""
    tool = Tool(
        name="untagged_tool",
        description="Tool without tags",
        execution={"type": "text", "text": "output"},
    )

    output = TableFormatter.format_verbose([tool])

    assert "untagged_tool" in output
    # Tags line should not appear if there are no tags
    assert "Tags:" not in output or "Tags: []" not in output


def test_format_delegates_to_basic_or_verbose():
    """Test that format() method delegates correctly."""
    tool = Tool(
        name="test",
        description="Test",
        tags=["test"],
        execution={"type": "text", "text": "output"},
    )

    # Test basic mode
    basic_output = TableFormatter.format([tool], verbose=False)
    assert "test" in basic_output

    # Test verbose mode
    verbose_output = TableFormatter.format([tool], verbose=True)
    assert "test" in verbose_output
    assert "test" in verbose_output  # Tags should appear in verbose


def test_verbose_table_with_cli_execution():
    """Test verbose format shows CLI execution type correctly."""
    tool = Tool(
        name="cli_tool",
        description="CLI tool",
        execution={"type": "cli", "command": "ls"},
    )

    output = TableFormatter.format_verbose([tool])

    assert "cli_tool" in output
    assert "cli" in output


def test_verbose_table_multiple_tools():
    """Test verbose format with multiple tools."""
    tools = [
        Tool(
            name="tool1",
            description="First",
            tags=["api"],
            execution={"type": "text", "text": "1"},
        ),
        Tool(
            name="tool2",
            description="Second",
            tags=["db"],
            execution={"type": "text", "text": "2"},
        ),
    ]

    output = TableFormatter.format_verbose(tools)

    assert "Available Tools (2)" in output
    assert "tool1" in output
    assert "tool2" in output
    assert "api" in output
    assert "db" in output
