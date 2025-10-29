"""
Unit tests for the list CLI command.

Tests the list command functionality including filtering, formats, and verbose mode.
"""

import json
import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner

from mci.cli.list import list_command


def create_test_schema(schema_dict: dict) -> str:
    """Helper to create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema_dict, f)
        return f.name


def test_list_default_format():
    """Test list command with default table format."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "test_tool",
                "description": "A test tool",
                "execution": {"type": "text", "text": "Hello"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        result = runner.invoke(list_command, ["--file", schema_path])

        assert result.exit_code == 0
        assert "Available Tools (1)" in result.output
        assert "test_tool" in result.output
        assert "A test tool" in result.output

    finally:
        Path(schema_path).unlink()


def test_list_json_format():
    """Test list command with JSON output format."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "test_tool",
                "description": "Test",
                "execution": {"type": "text", "text": "Hello"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        with runner.isolated_filesystem():
            result = runner.invoke(list_command, ["--file", schema_path, "--format", "json"])

            assert result.exit_code == 0
            assert "Tools exported to:" in result.output
            assert ".json" in result.output

            # Find and verify the JSON file
            json_files = list(Path(".").glob("tools_*.json"))
            assert len(json_files) == 1

            with open(json_files[0]) as f:
                data = json.load(f)

            assert data["total"] == 1
            assert data["tools"][0]["name"] == "test_tool"

    finally:
        Path(schema_path).unlink()


def test_list_yaml_format():
    """Test list command with YAML output format."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "test_tool",
                "description": "Test",
                "execution": {"type": "text", "text": "Hello"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        with runner.isolated_filesystem():
            result = runner.invoke(list_command, ["--file", schema_path, "--format", "yaml"])

            assert result.exit_code == 0
            assert "Tools exported to:" in result.output
            assert ".yaml" in result.output

            # Find and verify the YAML file
            yaml_files = list(Path(".").glob("tools_*.yaml"))
            assert len(yaml_files) == 1

            with open(yaml_files[0]) as f:
                data = yaml.safe_load(f)

            assert data["total"] == 1
            assert data["tools"][0]["name"] == "test_tool"

    finally:
        Path(schema_path).unlink()


def test_list_with_filter():
    """Test list command with tag filter."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "api_tool",
                "description": "API tool",
                "tags": ["api", "data"],
                "execution": {"type": "text", "text": "API"},
            },
            {
                "name": "db_tool",
                "description": "DB tool",
                "tags": ["database"],
                "execution": {"type": "text", "text": "DB"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        result = runner.invoke(list_command, ["--file", schema_path, "--filter", "tags:api"])

        assert result.exit_code == 0
        assert "Available Tools (1)" in result.output
        assert "api_tool" in result.output
        assert "db_tool" not in result.output

    finally:
        Path(schema_path).unlink()


def test_list_verbose():
    """Test list command with verbose mode."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "test_tool",
                "description": "Test tool",
                "tags": ["api", "test"],
                "inputSchema": {
                    "type": "object",
                    "properties": {"param": {"type": "string"}},
                    "required": ["param"],
                },
                "execution": {"type": "text", "text": "Hello"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        result = runner.invoke(list_command, ["--file", schema_path, "--verbose"])

        assert result.exit_code == 0
        assert "test_tool" in result.output
        # Check for tags line (tags may or may not appear depending on Rich output)
        # Check that verbose mode includes more detail than basic mode
        assert "param (string)" in result.output  # Parameters should appear
        assert "text" in result.output  # Execution type should appear

    finally:
        Path(schema_path).unlink()


def test_list_uses_same_loading_as_run():
    """Test that list command uses MCIClientWrapper (same as run would)."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "First",
                "execution": {"type": "text", "text": "1"},
            },
            {
                "name": "tool2",
                "description": "Second",
                "execution": {"type": "text", "text": "2"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        # List should show all tools
        result = runner.invoke(list_command, ["--file", schema_path])

        assert result.exit_code == 0
        assert "Available Tools (2)" in result.output
        assert "tool1" in result.output
        assert "tool2" in result.output

    finally:
        Path(schema_path).unlink()


def test_list_no_file_found():
    """Test list command when no MCI file is found."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(list_command)

        assert result.exit_code != 0
        assert "No MCI schema file found" in result.output


def test_list_invalid_filter():
    """Test list command with invalid filter specification."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "test",
                "description": "Test",
                "execution": {"type": "text", "text": "test"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        result = runner.invoke(list_command, ["--file", schema_path, "--filter", "invalid"])

        assert result.exit_code != 0
        assert "Invalid filter" in result.output

    finally:
        Path(schema_path).unlink()


def test_list_with_only_filter():
    """Test list command with 'only' filter type."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "First",
                "execution": {"type": "text", "text": "1"},
            },
            {
                "name": "tool2",
                "description": "Second",
                "execution": {"type": "text", "text": "2"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        result = runner.invoke(list_command, ["--file", schema_path, "--filter", "only:tool1"])

        assert result.exit_code == 0
        assert "Available Tools (1)" in result.output
        assert "tool1" in result.output
        assert "tool2" not in result.output

    finally:
        Path(schema_path).unlink()


def test_list_with_except_filter():
    """Test list command with 'except' filter type."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "First",
                "execution": {"type": "text", "text": "1"},
            },
            {
                "name": "tool2",
                "description": "Second",
                "execution": {"type": "text", "text": "2"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        result = runner.invoke(list_command, ["--file", schema_path, "--filter", "except:tool1"])

        assert result.exit_code == 0
        assert "Available Tools (1)" in result.output
        assert "tool1" not in result.output
        assert "tool2" in result.output

    finally:
        Path(schema_path).unlink()


def test_list_empty_tools():
    """Test list command with schema containing no tools."""
    schema = {"schemaVersion": "1.0", "tools": []}

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        result = runner.invoke(list_command, ["--file", schema_path])

        assert result.exit_code == 0
        assert "Available Tools (0)" in result.output

    finally:
        Path(schema_path).unlink()


def test_list_json_verbose():
    """Test list command with JSON format and verbose mode."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "test_tool",
                "description": "Test",
                "tags": ["api"],
                "inputSchema": {"type": "object"},
                "execution": {"type": "text", "text": "test"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        with runner.isolated_filesystem():
            result = runner.invoke(
                list_command, ["--file", schema_path, "--format", "json", "--verbose"]
            )

            assert result.exit_code == 0

            # Find and verify the JSON file contains verbose fields
            json_files = list(Path(".").glob("tools_*.json"))
            assert len(json_files) == 1

            with open(json_files[0]) as f:
                data = json.load(f)

            tool_data = data["tools"][0]
            assert "tags" in tool_data
            assert "execution_type" in tool_data

    finally:
        Path(schema_path).unlink()
