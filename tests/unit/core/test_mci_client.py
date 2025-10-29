"""
Unit tests for MCIClientWrapper class.

Tests the wrapper around MCIClient from mci-py, ensuring it properly
delegates operations and provides CLI-friendly interfaces.
"""

import json
import tempfile
from pathlib import Path

import pytest
from mcipy import MCIClientError

from mci.core.mci_client import MCIClientWrapper


def create_test_schema(schema_dict: dict) -> str:
    """Helper to create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema_dict, f)
        return f.name


def test_load_valid_schema():
    """Test loading a valid schema using MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        "metadata": {"name": "Test Schema", "description": "Test"},
        "tools": [
            {
                "name": "test_tool",
                "description": "A test tool",
                "execution": {"type": "text", "text": "Hello {{props.name}}"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        assert wrapper is not None
        assert wrapper.client is not None
    finally:
        Path(schema_path).unlink()


def test_invalid_schema_error():
    """Test handling of invalid schema from MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        # Missing required 'tools' field
        "metadata": {"name": "Invalid Schema"},
    }

    schema_path = create_test_schema(schema)
    try:
        with pytest.raises(MCIClientError):
            MCIClientWrapper(schema_path)
    finally:
        Path(schema_path).unlink()


def test_missing_file_error():
    """Test handling of missing file."""
    with pytest.raises(MCIClientError, match="Schema file not found"):
        MCIClientWrapper("/nonexistent/path/to/schema.mci.json")


def test_env_var_substitution():
    """Test environment variable templating via MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "env_test",
                "description": "Test environment variables",
                "execution": {"type": "text", "text": "API Key: {{env.TEST_API_KEY}}"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        env_vars = {"TEST_API_KEY": "secret-key-123"}
        wrapper = MCIClientWrapper(schema_path, env_vars=env_vars)

        # Verify the client was initialized with env vars
        tools = wrapper.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "env_test"
    finally:
        Path(schema_path).unlink()


def test_use_mciclient_filtering():
    """Test that filtering methods delegate to MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "First tool",
                "tags": ["api", "read"],
                "execution": {"type": "text", "text": "Tool 1"},
            },
            {
                "name": "tool2",
                "description": "Second tool",
                "tags": ["api", "write"],
                "execution": {"type": "text", "text": "Tool 2"},
            },
            {
                "name": "tool3",
                "description": "Third tool",
                "tags": ["database"],
                "execution": {"type": "text", "text": "Tool 3"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)

        # Test get_tools
        all_tools = wrapper.get_tools()
        assert len(all_tools) == 3
        assert [t.name for t in all_tools] == ["tool1", "tool2", "tool3"]

        # Test filter_only
        only_tools = wrapper.filter_only(["tool1", "tool3"])
        assert len(only_tools) == 2
        assert {t.name for t in only_tools} == {"tool1", "tool3"}

        # Test filter_except
        except_tools = wrapper.filter_except(["tool2"])
        assert len(except_tools) == 2
        assert {t.name for t in except_tools} == {"tool1", "tool3"}

        # Test filter_tags
        api_tools = wrapper.filter_tags(["api"])
        assert len(api_tools) == 2
        assert {t.name for t in api_tools} == {"tool1", "tool2"}

        # Test filter_without_tags
        no_api_tools = wrapper.filter_without_tags(["api"])
        assert len(no_api_tools) == 1
        assert no_api_tools[0].name == "tool3"

        # Test list_tool_names
        tool_names = wrapper.list_tool_names()
        assert tool_names == ["tool1", "tool2", "tool3"]
    finally:
        Path(schema_path).unlink()


def test_get_tools():
    """Test get_tools returns all tools."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool_a",
                "description": "Tool A",
                "execution": {"type": "text", "text": "A"},
            },
            {
                "name": "tool_b",
                "description": "Tool B",
                "execution": {"type": "text", "text": "B"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = wrapper.get_tools()
        assert len(tools) == 2
        assert {t.name for t in tools} == {"tool_a", "tool_b"}
    finally:
        Path(schema_path).unlink()


def test_filter_only_nonexistent():
    """Test filter_only with nonexistent tools returns empty list."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "existing_tool",
                "description": "Exists",
                "execution": {"type": "text", "text": "OK"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = wrapper.filter_only(["nonexistent_tool"])
        assert len(tools) == 0
    finally:
        Path(schema_path).unlink()


def test_filter_tags_no_match():
    """Test filter_tags with no matching tags returns empty list."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "Tool with tags",
                "tags": ["api"],
                "execution": {"type": "text", "text": "OK"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = wrapper.filter_tags(["nonexistent_tag"])
        assert len(tools) == 0
    finally:
        Path(schema_path).unlink()


def test_yaml_file_support():
    """Test loading YAML schema files."""
    yaml_content = """
schemaVersion: "1.0"
tools:
  - name: yaml_tool
    description: Tool from YAML
    execution:
      type: text
      text: "Hello from YAML"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    try:
        wrapper = MCIClientWrapper(yaml_path)
        tools = wrapper.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "yaml_tool"
    finally:
        Path(yaml_path).unlink()


def test_empty_tools_list():
    """Test schema with empty tools list."""
    schema = {"schemaVersion": "1.0", "tools": []}

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = wrapper.get_tools()
        assert len(tools) == 0
        assert wrapper.list_tool_names() == []
    finally:
        Path(schema_path).unlink()
