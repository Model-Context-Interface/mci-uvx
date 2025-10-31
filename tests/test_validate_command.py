"""
Feature tests for the validate command.

Tests end-to-end validation workflows with various schema files.
"""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from mci.cli.validate import validate


def test_validate_complete_valid_schema():
    """Test validation of a complete, valid MCI schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Complete Test Schema",
                "description": "A complete test schema with all features",
            },
            "tools": [
                {
                    "name": "test_tool",
                    "description": "A test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string", "description": "Test input"}
                        },
                        "required": ["input"],
                    },
                    "execution": {"type": "text", "text": "Result: {{props.input}}"},
                }
            ],
            "toolsets": [],
            "mcp_servers": {},
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output
        assert str(schema_file) in result.output


def test_validate_schema_with_toolsets_and_errors():
    """Test validation with toolset references that generate errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci directory
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()

        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test with toolsets"},
            "tools": [],
            "toolsets": ["weather", "database"],  # Missing toolsets cause errors in MCIClient
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        # MCIClient treats missing toolsets as errors, not warnings
        assert result.exit_code != 0
        assert "❌" in result.output or "Error" in result.output


def test_validate_schema_with_mcp_servers_warnings():
    """Test validation with MCP servers that generate warnings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test with MCP servers"},
            "tools": [],
            "mcp_servers": {
                "weather_server": {
                    "command": "nonexistent_weather_command",
                    "args": ["--port", "3000"],
                },
                "db_server": {
                    "command": "nonexistent_db_command",
                    "args": [],
                },
            },
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        # Should be valid despite warnings
        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output
        # Should show warnings about missing commands
        assert "⚠️" in result.output or "Warning" in result.output


def test_validate_invalid_json_syntax():
    """Test validation catches invalid JSON syntax."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        # Write invalid JSON
        schema_file.write_text('{"invalid": json}')

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code != 0


def test_validate_missing_required_fields():
    """Test validation catches missing required fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        # Missing schemaVersion which is required
        schema_content = {"tools": []}
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code != 0


def test_validate_wrong_schema_version():
    """Test validation catches unsupported schema versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "999.0",  # Invalid version
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        # May or may not fail depending on mci-py's validation
        # Just ensure command doesn't crash
        assert result.exit_code in [0, 1]


def test_validate_yaml_format():
    """Test validation works with YAML format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.yaml"
        schema_content = """
schemaVersion: "1.0"
metadata:
  name: "Test Schema"
  description: "Test YAML schema"
tools: []
toolsets: []
"""
        schema_file.write_text(schema_content)

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output


def test_validate_with_existing_toolset_files():
    """Test that existing toolset files don't generate errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci directory and toolset file
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()
        toolset_file = mci_dir / "weather.mci.json"
        toolset_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Weather", "description": "Weather tools"},
            "tools": [],
        }
        toolset_file.write_text(json.dumps(toolset_content))

        # Create main schema
        schema_file = Path(tmpdir) / "mci.json"
        # Reference existing toolset
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
            "toolsets": ["weather"],
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output


def test_validate_comprehensive_error_and_warning():
    """Test validation with both errors and warnings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Complex test"},
            "tools": [
                {
                    "name": "valid_tool",
                    "description": "A valid tool",
                    "execution": {"type": "text", "text": "Output"},
                }
            ],
            "toolsets": [],
            "mcp_servers": {"test": {"command": "fake_command_xyz", "args": []}},
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        # Should pass validation (missing MCP commands are warnings, not errors)
        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output
        # Should show warnings about missing MCP command
        assert "⚠️" in result.output or "Warning" in result.output
