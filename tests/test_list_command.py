"""
Feature test for the list command - End-to-end testing.

Tests the complete list command workflow including file discovery,
filtering, formatting, and output generation.
"""

import json
import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner

from mci.cli.list import list_command


def test_list_command_full_workflow():
    """Test complete list command workflow with all features."""
    # Create a comprehensive test schema
    schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Test Project",
            "description": "Full feature test schema",
        },
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "tags": ["api", "data", "weather"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Location name"},
                        "units": {"type": "string", "description": "Temperature units"},
                    },
                    "required": ["location"],
                },
                "execution": {"type": "text", "text": "Weather for {{props.location}}"},
            },
            {
                "name": "get_forecast",
                "description": "Get weather forecast",
                "tags": ["api", "data", "weather"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "days": {"type": "number"},
                    },
                    "required": ["location"],
                },
                "execution": {"type": "text", "text": "Forecast for {{props.location}}"},
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyze text sentiment",
                "tags": ["data", "ml", "text"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "model": {"type": "string"},
                    },
                    "required": ["text"],
                },
                "execution": {"type": "text", "text": "Sentiment: positive"},
            },
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    runner = CliRunner()

    try:
        # Test 1: Basic table output
        result = runner.invoke(list_command, ["--file", schema_path])
        assert result.exit_code == 0
        assert "Available Tools (3)" in result.output
        assert "get_weather" in result.output
        assert "get_forecast" in result.output
        assert "analyze_sentiment" in result.output

        # Test 2: Verbose table output
        result = runner.invoke(list_command, ["--file", schema_path, "--verbose"])
        assert result.exit_code == 0
        assert "get_weather" in result.output
        # Parameters should be shown
        assert "location (string)" in result.output

        # Test 3: Filter by tags
        result = runner.invoke(
            list_command, ["--file", schema_path, "--filter", "tags:weather"]
        )
        assert result.exit_code == 0
        assert "Available Tools (2)" in result.output
        assert "get_weather" in result.output
        assert "get_forecast" in result.output
        assert "analyze_sentiment" not in result.output

        # Test 4: Filter by tool name (only)
        result = runner.invoke(
            list_command, ["--file", schema_path, "--filter", "only:get_weather"]
        )
        assert result.exit_code == 0
        assert "Available Tools (1)" in result.output
        assert "get_weather" in result.output
        assert "get_forecast" not in result.output

        # Test 5: JSON output
        with runner.isolated_filesystem():
            result = runner.invoke(list_command, ["--file", schema_path, "--format", "json"])
            assert result.exit_code == 0
            assert "Tools exported to:" in result.output

            # Verify JSON file
            json_files = list(Path(".").glob("tools_*.json"))
            assert len(json_files) == 1

            with open(json_files[0]) as json_f:
                data = json.load(json_f)

            assert data["total"] == 3
            assert len(data["tools"]) == 3
            assert data["mci_file"] == schema_path

        # Test 6: YAML output with verbose
        with runner.isolated_filesystem():
            result = runner.invoke(
                list_command, ["--file", schema_path, "--format", "yaml", "--verbose"]
            )
            assert result.exit_code == 0
            assert "Tools exported to:" in result.output

            # Verify YAML file
            yaml_files = list(Path(".").glob("tools_*.yaml"))
            assert len(yaml_files) == 1

            with open(yaml_files[0]) as yaml_f:
                data = yaml.safe_load(yaml_f)

            assert data["total"] == 3
            # Verbose mode should include tags
            assert "tags" in data["tools"][0]

        # Test 7: JSON output with filter
        with runner.isolated_filesystem():
            result = runner.invoke(
                list_command,
                ["--file", schema_path, "--format", "json", "--filter", "tags:ml"],
            )
            assert result.exit_code == 0

            # Verify filtered JSON
            json_files = list(Path(".").glob("tools_*.json"))
            assert len(json_files) == 1

            with open(json_files[0]) as json_f:
                data = json.load(json_f)

            assert data["total"] == 1
            assert data["filters_applied"] == ["tags:ml"]
            assert data["tools"][0]["name"] == "analyze_sentiment"

    finally:
        Path(schema_path).unlink()


def test_list_command_auto_file_discovery():
    """Test that list command finds mci.json automatically."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create mci.json in current directory
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "auto_tool",
                    "description": "Auto-discovered tool",
                    "execution": {"type": "text", "text": "Auto"},
                }
            ],
        }

        with open("mci.json", "w") as f:
            json.dump(schema, f)

        # Run without --file option
        result = runner.invoke(list_command)

        assert result.exit_code == 0
        assert "auto_tool" in result.output


def test_list_command_error_handling():
    """Test error handling in list command."""
    runner = CliRunner()

    # Test 1: File not found
    with runner.isolated_filesystem():
        result = runner.invoke(list_command)
        assert result.exit_code != 0
        assert "No MCI schema file found" in result.output

    # Test 2: Invalid filter
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

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        result = runner.invoke(list_command, ["--file", schema_path, "--filter", "invalid"])
        assert result.exit_code != 0
        assert "Invalid filter" in result.output
    finally:
        Path(schema_path).unlink()
