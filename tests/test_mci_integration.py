"""
Feature test for MCI-PY integration.

Tests end-to-end integration with mci-py library using real schema files.
"""

import json
import tempfile
from pathlib import Path

import pytest
from mcipy import MCIClientError

from mci.core.mci_client import MCIClientWrapper
from mci.core.tool_manager import ToolManager


def create_comprehensive_schema() -> dict:
    """Create a comprehensive test schema with multiple tools and features."""
    return {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Integration Test Schema",
            "description": "Comprehensive schema for testing MCI-PY integration",
            "version": "1.0.0",
        },
        "tools": [
            {
                "name": "weather_api",
                "description": "Get weather information",
                "tags": ["api", "read", "weather"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"},
                        "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
                "execution": {
                    "type": "http",
                    "method": "GET",
                    "url": "https://api.weather.example.com/current",
                    "params": {
                        "location": "{{props.location}}",
                        "units": "{{props.units}}",
                        "api_key": "{{env.WEATHER_API_KEY}}",
                    },
                },
            },
            {
                "name": "list_files_cli",
                "description": "List files in directory",
                "tags": ["cli", "filesystem"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["directory"],
                },
                "execution": {
                    "type": "cli",
                    "command": "ls",
                    "args": ["-la", "{{props.directory}}"],
                },
            },
            {
                "name": "echo_text",
                "description": "Simple echo tool",
                "tags": ["text", "simple"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Message to echo"}
                    },
                    "required": ["message"],
                },
                "execution": {"type": "text", "text": "Echo: {{props.message}}"},
            },
            {
                "name": "read_config_file",
                "description": "Read configuration file",
                "tags": ["file", "config"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "config_path": {"type": "string", "description": "Path to config file"}
                    },
                },
                "execution": {
                    "type": "file",
                    "path": "{{props.config_path}}",
                    "enableTemplating": True,
                },
            },
            {
                "name": "deprecated_tool",
                "description": "A deprecated tool",
                "tags": ["deprecated"],
                "execution": {"type": "text", "text": "This tool is deprecated"},
            },
        ],
    }


def test_mci_integration_load_schema():
    """Test loading a comprehensive schema via MCIClient."""
    schema = create_comprehensive_schema()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        wrapper = MCIClientWrapper(schema_path)
        assert wrapper is not None

        # Verify all tools are loaded
        tools = wrapper.get_tools()
        assert len(tools) == 5
        tool_names = {t.name for t in tools}
        assert tool_names == {
            "weather_api",
            "list_files_cli",
            "echo_text",
            "read_config_file",
            "deprecated_tool",
        }
    finally:
        Path(schema_path).unlink()


def test_mci_integration_filter_only():
    """Test filtering with 'only' specification."""
    schema = create_comprehensive_schema()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        wrapper = MCIClientWrapper(schema_path)

        # Filter to only specific tools
        tools = ToolManager.apply_filter_spec(wrapper, "only:weather_api,echo_text")
        assert len(tools) == 2
        assert {t.name for t in tools} == {"weather_api", "echo_text"}
    finally:
        Path(schema_path).unlink()


def test_mci_integration_filter_except():
    """Test filtering with 'except' specification."""
    schema = create_comprehensive_schema()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        wrapper = MCIClientWrapper(schema_path)

        # Exclude specific tools
        tools = ToolManager.apply_filter_spec(wrapper, "except:deprecated_tool")
        assert len(tools) == 4
        tool_names = {t.name for t in tools}
        assert "deprecated_tool" not in tool_names
    finally:
        Path(schema_path).unlink()


def test_mci_integration_filter_tags():
    """Test filtering by tags."""
    schema = create_comprehensive_schema()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        wrapper = MCIClientWrapper(schema_path)

        # Filter by single tag
        api_tools = ToolManager.apply_filter_spec(wrapper, "tags:api")
        assert len(api_tools) == 1
        assert api_tools[0].name == "weather_api"

        # Filter by multiple tags (OR logic)
        cli_or_file_tools = ToolManager.apply_filter_spec(wrapper, "tags:cli,file")
        assert len(cli_or_file_tools) == 2
        assert {t.name for t in cli_or_file_tools} == {"list_files_cli", "read_config_file"}
    finally:
        Path(schema_path).unlink()


def test_mci_integration_filter_without_tags():
    """Test filtering to exclude tags."""
    schema = create_comprehensive_schema()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        wrapper = MCIClientWrapper(schema_path)

        # Exclude deprecated tools
        non_deprecated = ToolManager.apply_filter_spec(wrapper, "without-tags:deprecated")
        assert len(non_deprecated) == 4
        tool_names = {t.name for t in non_deprecated}
        assert "deprecated_tool" not in tool_names
    finally:
        Path(schema_path).unlink()


def test_mci_integration_yaml_support():
    """Test loading YAML schema files."""
    yaml_content = """
schemaVersion: "1.0"
metadata:
  name: "YAML Test Schema"
  description: "Testing YAML support"
tools:
  - name: yaml_tool_1
    description: First YAML tool
    tags:
      - yaml
      - test
    execution:
      type: text
      text: "YAML Tool 1"
  - name: yaml_tool_2
    description: Second YAML tool
    tags:
      - yaml
    execution:
      type: text
      text: "YAML Tool 2"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    try:
        wrapper = MCIClientWrapper(yaml_path)

        # Verify tools are loaded
        tools = wrapper.get_tools()
        assert len(tools) == 2
        assert {t.name for t in tools} == {"yaml_tool_1", "yaml_tool_2"}

        # Test filtering on YAML-loaded tools
        yaml_tools = ToolManager.apply_filter_spec(wrapper, "tags:yaml")
        assert len(yaml_tools) == 2
    finally:
        Path(yaml_path).unlink()


def test_mci_integration_env_vars():
    """Test environment variable templating."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "api_with_key",
                "description": "API requiring environment variable",
                "execution": {
                    "type": "http",
                    "method": "GET",
                    "url": "https://api.example.com/data",
                    "params": {"api_key": "{{env.API_KEY}}"},
                },
            }
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        env_vars = {"API_KEY": "test-key-123"}
        wrapper = MCIClientWrapper(schema_path, env_vars=env_vars)

        # Verify the tool is loaded (templating is validated at execution time)
        tools = wrapper.get_tools()
        assert len(tools) == 1
        assert tools[0].name == "api_with_key"
    finally:
        Path(schema_path).unlink()


def test_mci_integration_tool_properties():
    """Test accessing tool properties from Pydantic models."""
    schema = create_comprehensive_schema()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = wrapper.get_tools()

        # Find the weather_api tool
        weather_tool = next(t for t in tools if t.name == "weather_api")

        # Verify tool properties (Pydantic model from mci-py)
        assert weather_tool.name == "weather_api"
        assert weather_tool.description == "Get weather information"
        assert "api" in weather_tool.tags
        assert "read" in weather_tool.tags
        assert weather_tool.inputSchema is not None
        assert weather_tool.inputSchema["type"] == "object"
        assert "location" in weather_tool.inputSchema["properties"]
    finally:
        Path(schema_path).unlink()


def test_mci_integration_invalid_schema():
    """Test error handling for invalid schemas."""
    invalid_schema = {
        "schemaVersion": "1.0",
        # Missing required 'tools' field
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(invalid_schema, f)
        schema_path = f.name

    try:
        with pytest.raises(MCIClientError):
            MCIClientWrapper(schema_path)
    finally:
        Path(schema_path).unlink()
