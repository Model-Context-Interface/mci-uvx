"""
Unit tests for the YAMLFormatter class.

Tests the YAML file output formatting with metadata.
"""

import os

import yaml
from mcipy.models import Tool

from mci.cli.formatters.yaml_formatter import YAMLFormatter


def test_yaml_output_structure():
    """Test that YAML output has correct structure."""
    tools = [
        Tool(
            name="test_tool",
            description="Test tool",
            tags=["api"],
            execution={"type": "text", "text": "test"},
        )
    ]

    filename = YAMLFormatter.format_to_file(
        tools=tools, mci_file="test.mci.json", filters_applied=[], verbose=False
    )

    try:
        assert filename.endswith(".yaml")
        assert filename.startswith("tools_")
        assert os.path.exists(filename)

        # Read and parse the YAML
        with open(filename) as f:
            data = yaml.safe_load(f)

        # Check structure
        assert "timestamp" in data
        assert "mci_file" in data
        assert "filters_applied" in data
        assert "total" in data
        assert "tools" in data

        # Check values
        assert data["mci_file"] == "test.mci.json"
        assert data["filters_applied"] == []
        assert data["total"] == 1
        assert len(data["tools"]) == 1

        # Check tool data
        tool_data = data["tools"][0]
        assert tool_data["name"] == "test_tool"
        assert tool_data["description"] == "Test tool"
        assert tool_data["source"] == "main"

    finally:
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)


def test_yaml_output_with_filters():
    """Test YAML output includes filters_applied."""
    tools = [
        Tool(
            name="test",
            description="Test",
            execution={"type": "text", "text": "test"},
        )
    ]

    filename = YAMLFormatter.format_to_file(
        tools=tools,
        mci_file="test.mci.json",
        filters_applied=["tags:api,database"],
        verbose=False,
    )

    try:
        with open(filename) as f:
            data = yaml.safe_load(f)

        assert data["filters_applied"] == ["tags:api,database"]

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_yaml_verbose_output():
    """Test that verbose mode includes additional fields."""
    tool = Tool(
        name="verbose_test",
        description="Test verbose",
        tags=["api", "test"],
        inputSchema={
            "type": "object",
            "properties": {"param": {"type": "string"}},
        },
        execution={"type": "text", "text": "output"},
        disabled=True,
    )

    filename = YAMLFormatter.format_to_file(
        tools=[tool], mci_file="test.mci.json", filters_applied=[], verbose=True
    )

    try:
        with open(filename) as f:
            data = yaml.safe_load(f)

        tool_data = data["tools"][0]

        # Verbose fields should be present
        assert "tags" in tool_data
        assert "execution_type" in tool_data
        assert "inputSchema" in tool_data
        assert "disabled" in tool_data

        assert tool_data["tags"] == ["api", "test"]
        assert tool_data["execution_type"] == "text"
        assert tool_data["disabled"] is True

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_yaml_basic_output_no_verbose_fields():
    """Test that basic mode doesn't include verbose fields."""
    tool = Tool(
        name="basic_test",
        description="Test basic",
        tags=["api"],
        inputSchema={"type": "object"},
        execution={"type": "text", "text": "output"},
    )

    filename = YAMLFormatter.format_to_file(
        tools=[tool], mci_file="test.mci.json", filters_applied=[], verbose=False
    )

    try:
        with open(filename) as f:
            data = yaml.safe_load(f)

        tool_data = data["tools"][0]

        # Verbose fields should NOT be present
        assert "tags" not in tool_data
        assert "execution_type" not in tool_data
        assert "inputSchema" not in tool_data

        # Basic fields should be present
        assert "name" in tool_data
        assert "source" in tool_data
        assert "description" in tool_data

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_yaml_multiple_tools():
    """Test YAML output with multiple tools."""
    tools = [
        Tool(
            name="tool1",
            description="First",
            execution={"type": "text", "text": "1"},
        ),
        Tool(
            name="tool2",
            description="Second",
            execution={"type": "text", "text": "2"},
        ),
        Tool(
            name="tool3",
            description="Third",
            execution={"type": "text", "text": "3"},
        ),
    ]

    filename = YAMLFormatter.format_to_file(
        tools=tools, mci_file="test.mci.json", filters_applied=[], verbose=False
    )

    try:
        with open(filename) as f:
            data = yaml.safe_load(f)

        assert data["total"] == 3
        assert len(data["tools"]) == 3

        # Check all tools are present
        tool_names = [t["name"] for t in data["tools"]]
        assert "tool1" in tool_names
        assert "tool2" in tool_names
        assert "tool3" in tool_names

    finally:
        if os.path.exists(filename):
            os.remove(filename)


def test_yaml_with_custom_toolset_source():
    """Test YAML output includes toolset source."""
    tool = Tool(
        name="sourced_tool",
        description="From toolset",
        execution={"type": "text", "text": "test"},
        toolset_source="custom-toolset",
    )

    filename = YAMLFormatter.format_to_file(
        tools=[tool], mci_file="test.mci.json", filters_applied=[], verbose=False
    )

    try:
        with open(filename) as f:
            data = yaml.safe_load(f)

        assert data["tools"][0]["source"] == "custom-toolset"

    finally:
        if os.path.exists(filename):
            os.remove(filename)
