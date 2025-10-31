"""
Unit tests for MCIValidator.

Tests the schema validation using MCIClient and additional checks.
"""

import json
import tempfile
from pathlib import Path

from mci.core.validator import MCIValidator


def test_valid_schema_via_mciclient():
    """Test validation of a valid schema using MCIClient."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test schema"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        validator = MCIValidator(str(schema_file))
        result = validator.validate_schema()

        assert result.is_valid is True
        assert len(result.errors) == 0


def test_invalid_schema_caught_by_mciclient():
    """Test that MCIClient catches invalid schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {"invalid": "schema"}
        schema_file.write_text(json.dumps(schema_content))

        validator = MCIValidator(str(schema_file))
        result = validator.validate_schema()

        assert result.is_valid is False
        assert len(result.errors) > 0
        # Should have an error message from MCIClient
        assert any("schemaVersion" in error.message for error in result.errors)


def test_missing_required_field():
    """Test detection of missing required fields via MCIClient."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        # Completely invalid schema - missing schemaVersion which is required
        schema_content = {"tools": []}
        schema_file.write_text(json.dumps(schema_content))

        validator = MCIValidator(str(schema_file))
        result = validator.validate_schema()

        # MCIClient should catch this as an error
        assert result.is_valid is False
        assert len(result.errors) > 0


def test_invalid_toolset_reference():
    """Test that MCIClient catches missing toolset files as errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci directory for toolsets
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()

        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
            "toolsets": ["missing"],  # Reference to missing.mci.json in mci/ directory
        }
        schema_file.write_text(json.dumps(schema_content))

        validator = MCIValidator(str(schema_file))
        result = validator.validate_schema()

        # MCIClient treats missing toolsets as validation errors
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("missing" in error.message.lower() for error in result.errors)


def test_missing_mcp_command():
    """Test detection of missing MCP commands in PATH (as warning)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
            "mcp_servers": {
                "test_server": {
                    "command": "definitely_not_a_real_command_12345",
                    "args": [],
                }
            },
        }
        schema_file.write_text(json.dumps(schema_content))

        validator = MCIValidator(str(schema_file))
        result = validator.validate_schema()

        # Schema should be valid (MCP command is a warning, not error)
        assert result.is_valid is True
        assert len(result.errors) == 0
        # But should have a warning about missing command
        assert len(result.warnings) > 0
        assert any(
            "definitely_not_a_real_command_12345" in warning.message
            for warning in result.warnings
        )


def test_warning_collection():
    """Test that MCP command warnings are collected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
            "toolsets": [],
            "mcp_servers": {
                "server1": {"command": "fake_command_1", "args": []},
                "server2": {"command": "fake_command_2", "args": []},
            },
        }
        schema_file.write_text(json.dumps(schema_content))

        validator = MCIValidator(str(schema_file))
        result = validator.validate_schema()

        # Schema should be valid (MCP commands are warnings, not errors)
        assert result.is_valid is True
        assert len(result.errors) == 0
        # Should have warnings about missing MCP commands
        assert len(result.warnings) >= 2


def test_file_not_found():
    """Test handling of non-existent file."""
    validator = MCIValidator("/nonexistent/file.json")
    result = validator.validate_schema()

    assert result.is_valid is False
    assert len(result.errors) > 0


def test_validation_with_env_vars():
    """Test validation with environment variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        env_vars = {"TEST_VAR": "test_value"}
        validator = MCIValidator(str(schema_file), env_vars=env_vars)
        result = validator.validate_schema()

        assert result.is_valid is True


def test_check_toolset_files_with_existing_file():
    """Test that existing toolset files don't generate warnings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci directory and toolset file
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()
        toolset_file = mci_dir / "toolset.mci.json"
        toolset_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Toolset", "description": "Test toolset"},
            "tools": [],
        }
        toolset_file.write_text(json.dumps(toolset_content))

        # Create the main schema file
        schema_file = Path(tmpdir) / "mci.json"
        # Reference the existing toolset
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test", "description": "Test"},
            "tools": [],
            "toolsets": ["toolset"],  # Reference to toolset.mci.json in mci/ directory
        }
        schema_file.write_text(json.dumps(schema_content))

        validator = MCIValidator(str(schema_file))
        result = validator.validate_schema()

        # Should be valid with no warnings about missing toolset
        assert result.is_valid is True
        assert len(result.errors) == 0
        # Check that there's no warning about toolset
        toolset_warnings = [w for w in result.warnings if "toolset" in w.message.lower()]
        assert len(toolset_warnings) == 0
