"""
Unit tests for envs.py - Environment variables command
"""

import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from mci.cli.envs import envs_command, extract_env_vars_from_schema


def test_extract_env_vars_simple_schema():
    """Test extracting env vars from a simple schema."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "test_tool",
                    "execution": {
                        "type": "http",
                        "url": "{{env.API_URL}}",
                        "headers": {"Authorization": "{{env.API_KEY}}"},
                    },
                }
            ],
        }
        json.dump(schema, f)
        schema_path = f.name

    try:
        result = extract_env_vars_from_schema(schema_path)
        assert result == {
            "API_URL": ["main"],
            "API_KEY": ["main"],
        }
    finally:
        Path(schema_path).unlink()


def test_extract_env_vars_with_toolsets():
    """Test extracting env vars from schema with toolsets."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create main schema
        main_schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "main_tool",
                    "execution": {"type": "text", "text": "{{env.MAIN_VAR}}"},
                }
            ],
            "toolsets": ["toolset1"],
        }
        main_file = tmpdir_path / "test.mci.json"
        main_file.write_text(json.dumps(main_schema))

        # Create toolset directory and file
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()
        toolset_schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "toolset_tool",
                    "execution": {
                        "type": "http",
                        "url": "{{env.TOOLSET_URL}}",
                    },
                }
            ],
        }
        toolset_file = mci_dir / "toolset1.mci.json"
        toolset_file.write_text(json.dumps(toolset_schema))

        result = extract_env_vars_from_schema(str(main_file))
        assert result == {
            "MAIN_VAR": ["main"],
            "TOOLSET_URL": ["toolset1"],
        }


def test_extract_env_vars_with_mcp_servers():
    """Test extracting env vars from MCP server configs."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [],
            "mcp_servers": {
                "server1": {
                    "url": "{{env.SERVER_URL}}",
                    "headers": {"Auth": "{{env.SERVER_TOKEN}}"},
                }
            },
        }
        json.dump(schema, f)
        schema_path = f.name

    try:
        result = extract_env_vars_from_schema(schema_path)
        assert result == {
            "SERVER_URL": ["mcp:server1"],
            "SERVER_TOKEN": ["mcp:server1"],
        }
    finally:
        Path(schema_path).unlink()


def test_extract_env_vars_deduplication():
    """Test that env vars used in multiple places are deduplicated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create main schema
        main_schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "tool1",
                    "execution": {"type": "text", "text": "{{env.SHARED_VAR}}"},
                }
            ],
            "toolsets": ["toolset1"],
        }
        main_file = tmpdir_path / "test.mci.json"
        main_file.write_text(json.dumps(main_schema))

        # Create toolset that also uses SHARED_VAR
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()
        toolset_schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "tool2",
                    "execution": {
                        "type": "http",
                        "url": "{{env.SHARED_VAR}}/api",
                    },
                }
            ],
        }
        toolset_file = mci_dir / "toolset1.mci.json"
        toolset_file.write_text(json.dumps(toolset_schema))

        result = extract_env_vars_from_schema(str(main_file))
        # SHARED_VAR should appear in both locations
        assert result == {
            "SHARED_VAR": ["main", "toolset1"],
        }


def test_extract_env_vars_missing_toolset():
    """Test that missing toolset files don't cause errors."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "test_tool",
                    "execution": {"type": "text", "text": "{{env.MAIN_VAR}}"},
                }
            ],
            "toolsets": ["missing_toolset"],
        }
        json.dump(schema, f)
        schema_path = f.name

    try:
        # Should not raise error even though toolset is missing
        result = extract_env_vars_from_schema(schema_path)
        assert result == {"MAIN_VAR": ["main"]}
    finally:
        Path(schema_path).unlink()


def test_envs_command_table_format():
    """Test envs command with table format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "test_tool",
                    "execution": {
                        "type": "http",
                        "url": "{{env.API_URL}}",
                    },
                }
            ],
        }
        json.dump(schema, f)
        schema_path = f.name

    try:
        runner = CliRunner()
        result = runner.invoke(envs_command, ["--file", schema_path, "--format", "table"])

        assert result.exit_code == 0
        assert "API_URL" in result.output
        assert "main" in result.output
    finally:
        Path(schema_path).unlink()


def test_envs_command_env_format():
    """Test envs command with env format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create schema file
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "test_tool",
                    "execution": {
                        "type": "http",
                        "url": "{{env.API_URL}}",
                        "headers": {"Key": "{{env.API_KEY}}"},
                    },
                }
            ],
        }
        schema_file = tmpdir_path / "test.mci.json"
        schema_file.write_text(json.dumps(schema))

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmpdir):
            result = runner.invoke(
                envs_command,
                ["--file", str(schema_file), "--format", "env"],
                catch_exceptions=False,
            )

            assert result.exit_code == 0
            assert "exported to" in result.output

            # Check generated file
            env_file = Path(".env.example.mci")
            assert env_file.exists()

            content = env_file.read_text()
            assert "API_URL=" in content
            assert "API_KEY=" in content
            assert "# Used in: main" in content


def test_envs_command_no_env_vars():
    """Test envs command when no environment variables are found."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "test_tool",
                    "execution": {"type": "text", "text": "Hello world"},
                }
            ],
        }
        json.dump(schema, f)
        schema_path = f.name

    try:
        runner = CliRunner()
        result = runner.invoke(envs_command, ["--file", schema_path])

        assert result.exit_code == 0
        assert "No environment variables found" in result.output
    finally:
        Path(schema_path).unlink()


def test_envs_command_yaml_schema():
    """Test envs command with YAML schema."""
    import yaml

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.yaml", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "test_tool",
                    "execution": {
                        "type": "http",
                        "url": "{{env.YAML_VAR}}",
                    },
                }
            ],
        }
        yaml.dump(schema, f)
        schema_path = f.name

    try:
        runner = CliRunner()
        result = runner.invoke(envs_command, ["--file", schema_path])

        assert result.exit_code == 0
        assert "YAML_VAR" in result.output
    finally:
        Path(schema_path).unlink()
