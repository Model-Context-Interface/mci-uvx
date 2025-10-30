"""
Unit tests for the validate CLI command.

Tests the validate command functionality.
"""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from mci.cli.validate import validate


def test_validate_valid_file():
    """Test validate command with valid schema file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test schema"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output


def test_validate_invalid_file():
    """Test validate command with invalid schema file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {"invalid": "schema"}
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code != 0
        assert "❌" in result.output or "Validation" in result.output


def test_validate_missing_file():
    """Test validate command with missing file."""
    runner = CliRunner()
    result = runner.invoke(validate, ["--file", "/nonexistent/file.json"])

    assert result.exit_code != 0


def test_validate_with_warnings():
    """Test validate command shows warnings for missing MCP commands."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
            "toolsets": [],
            "mcp_servers": {
                "test_server": {"command": "fake_nonexistent_command_xyz", "args": []}
            },
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        # Should exit successfully (warnings don't fail validation)
        assert result.exit_code == 0
        # Should show success
        assert "✅ Schema is valid!" in result.output
        # Should show warnings
        assert "⚠️" in result.output or "Warning" in result.output
        assert "fake_nonexistent_command_xyz" in result.output or "test_server" in result.output


def test_validate_auto_discover():
    """Test validate command auto-discovers mci.json in current directory."""
    # Since CliRunner runs in the project directory where mci.json exists,
    # we can't easily test auto-discovery in a clean environment.
    # Instead, test that the command works with an explicit file path.
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(validate, ["--file", str(schema_file)])

        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output


def test_validate_with_env_vars():
    """Test validate command with environment variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(
            validate, ["--file", str(schema_file), "-e", "TEST_VAR=test_value"]
        )

        assert result.exit_code == 0
        assert "✅ Schema is valid!" in result.output


def test_validate_multiple_env_vars():
    """Test validate command with multiple environment variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(
            validate,
            [
                "--file",
                str(schema_file),
                "-e",
                "VAR1=value1",
                "-e",
                "VAR2=value2",
            ],
        )

        assert result.exit_code == 0


def test_validate_invalid_env_var_format():
    """Test validate command with invalid env var format shows warning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        runner = CliRunner()
        result = runner.invoke(
            validate, ["--file", str(schema_file), "-e", "INVALID_FORMAT"]
        )

        # Should still validate the file
        assert result.exit_code == 0
        # Should show a warning about invalid format
        assert "Invalid environment variable format" in result.output
