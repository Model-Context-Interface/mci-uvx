"""
Feature test for the envs command - End-to-end testing.

Tests the complete envs command workflow including file discovery,
env variable extraction, and output generation.
"""

import json
import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner

from mci.cli.envs import envs_command


def test_envs_command_full_workflow():
    """Test complete envs command workflow with all features."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create comprehensive main schema
        main_schema = {
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Full Test Schema",
                "description": "Complete feature test",
            },
            "tools": [
                {
                    "name": "http_tool",
                    "description": "HTTP API tool",
                    "execution": {
                        "type": "http",
                        "method": "POST",
                        "url": "{{env.API_BASE_URL}}/endpoint",
                        "headers": {
                            "Authorization": "Bearer {{env.API_TOKEN}}",
                            "X-Custom": "{{env.CUSTOM_HEADER}}",
                        },
                    },
                },
                {
                    "name": "cli_tool",
                    "description": "CLI tool",
                    "execution": {
                        "type": "cli",
                        "command": "echo",
                        "args": ["{{env.MESSAGE}}"],
                        "cwd": "{{env.PROJECT_ROOT}}",
                    },
                },
            ],
            "toolsets": ["weather", "database"],
            "mcp_servers": {
                "github": {
                    "type": "http",
                    "url": "{{env.GITHUB_MCP_URL}}",
                    "headers": {"Authorization": "token {{env.GITHUB_TOKEN}}"},
                },
                "slack": {
                    "type": "http",
                    "url": "{{env.SLACK_MCP_URL}}",
                },
            },
            "directoryAllowList": ["{{env.ALLOWED_DIR}}"],
        }

        main_file = tmpdir_path / "test.mci.json"
        main_file.write_text(json.dumps(main_schema))

        # Create toolsets
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # Weather toolset
        weather_schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "get_weather",
                    "execution": {
                        "type": "http",
                        "url": "{{env.WEATHER_API_URL}}/weather",
                        "headers": {"X-API-Key": "{{env.WEATHER_API_KEY}}"},
                    },
                }
            ],
        }
        (mci_dir / "weather.mci.json").write_text(json.dumps(weather_schema))

        # Database toolset
        database_schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "query_db",
                    "execution": {
                        "type": "cli",
                        "command": "psql",
                        "args": ["-h", "{{env.DB_HOST}}"],
                    },
                }
            ],
            "directoryAllowList": ["{{env.DB_BACKUP_DIR}}"],
        }
        (mci_dir / "database.mci.json").write_text(json.dumps(database_schema))

        runner = CliRunner()

        # Test 1: Table format
        result = runner.invoke(
            envs_command, ["--file", str(main_file), "--format", "table"]
        )
        assert result.exit_code == 0
        assert "Environment Variables" in result.output
        # Check main schema vars
        assert "API_BASE_URL" in result.output
        assert "API_TOKEN" in result.output
        assert "CUSTOM_HEADER" in result.output
        assert "MESSAGE" in result.output
        assert "PROJECT_ROOT" in result.output
        assert "ALLOWED_DIR" in result.output
        # Check toolset vars
        assert "WEATHER_API_URL" in result.output
        assert "WEATHER_API_KEY" in result.output
        assert "DB_HOST" in result.output
        assert "DB_BACKUP_DIR" in result.output
        # Check MCP server vars
        assert "GITHUB_MCP_URL" in result.output
        assert "GITHUB_TOKEN" in result.output
        assert "SLACK_MCP_URL" in result.output

        # Test 2: Env format
        with runner.isolated_filesystem(temp_dir=tmpdir):
            result = runner.invoke(
                envs_command, ["--file", str(main_file), "--format", "env"]
            )
            assert result.exit_code == 0
            assert "exported to" in result.output

            # Verify generated .env file
            env_file = Path(".env.example.mci")
            assert env_file.exists()
            content = env_file.read_text()

            # Check all variables are present
            assert "API_BASE_URL=" in content
            assert "API_TOKEN=" in content
            assert "WEATHER_API_URL=" in content
            assert "DB_HOST=" in content
            assert "GITHUB_TOKEN=" in content

            # Check comments showing usage
            assert "# Used in: main" in content
            assert "# Used in: weather" in content
            assert "# Used in: database" in content
            assert "# Used in: mcp:github" in content


def test_envs_command_yaml_schema():
    """Test envs command with YAML schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create YAML schema
        schema = {
            "schemaVersion": "1.0",
            "metadata": {"name": "YAML Test"},
            "tools": [
                {
                    "name": "yaml_tool",
                    "execution": {
                        "type": "http",
                        "url": "{{env.YAML_API_URL}}",
                        "headers": {"Auth": "{{env.YAML_API_KEY}}"},
                    },
                }
            ],
        }

        schema_file = tmpdir_path / "test.mci.yaml"
        schema_file.write_text(yaml.dump(schema))

        runner = CliRunner()
        result = runner.invoke(envs_command, ["--file", str(schema_file)])

        assert result.exit_code == 0
        assert "YAML_API_URL" in result.output
        assert "YAML_API_KEY" in result.output


def test_envs_command_mixed_json_yaml_toolsets():
    """Test envs command with mixed JSON and YAML toolsets."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create JSON main schema
        main_schema = {
            "schemaVersion": "1.0",
            "tools": [
                {"name": "main_tool", "execution": {"type": "text", "text": "{{env.MAIN_VAR}}"}}
            ],
            "toolsets": ["json_toolset", "yaml_toolset"],
        }
        main_file = tmpdir_path / "test.mci.json"
        main_file.write_text(json.dumps(main_schema))

        # Create mci directory
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # Create JSON toolset
        json_toolset = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "json_tool",
                    "execution": {"type": "text", "text": "{{env.JSON_VAR}}"},
                }
            ],
        }
        (mci_dir / "json_toolset.mci.json").write_text(json.dumps(json_toolset))

        # Create YAML toolset
        yaml_toolset = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "yaml_tool",
                    "execution": {"type": "text", "text": "{{env.YAML_VAR}}"},
                }
            ],
        }
        (mci_dir / "yaml_toolset.mci.yaml").write_text(yaml.dump(yaml_toolset))

        runner = CliRunner()
        result = runner.invoke(envs_command, ["--file", str(main_file)])

        assert result.exit_code == 0
        assert "MAIN_VAR" in result.output
        assert "JSON_VAR" in result.output
        assert "YAML_VAR" in result.output


def test_envs_command_no_file_specified():
    """Test envs command without --file option (should look for default)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create default mci.json in directory
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {"name": "tool", "execution": {"type": "text", "text": "{{env.DEFAULT_VAR}}"}}
            ],
        }
        (tmpdir_path / "mci.json").write_text(json.dumps(schema))

        runner = CliRunner()
        # Change to the directory containing mci.json and run
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir_path)
            result = runner.invoke(envs_command, [])

            assert result.exit_code == 0
            assert "DEFAULT_VAR" in result.output
        finally:
            os.chdir(old_cwd)


def test_envs_command_empty_schema():
    """Test envs command with schema that has no env variables."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {"name": "simple_tool", "execution": {"type": "text", "text": "Hello world"}}
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


def test_envs_command_complex_nesting():
    """Test envs command with deeply nested env variable references."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        schema = {
            "schemaVersion": "1.0",
            "tools": [
                {
                    "name": "nested_tool",
                    "execution": {
                        "type": "http",
                        "url": "{{env.BASE_URL}}",
                        "headers": {
                            "nested": {
                                "deep": {
                                    "value": "{{env.DEEP_VAR}}",
                                }
                            }
                        },
                    },
                }
            ],
            "directoryAllowList": [
                "{{env.DIR1}}",
                "{{env.DIR2}}",
                ["{{env.DIR3}}"],
            ],
        }
        json.dump(schema, f)
        schema_path = f.name

    try:
        runner = CliRunner()
        result = runner.invoke(envs_command, ["--file", schema_path])

        assert result.exit_code == 0
        assert "BASE_URL" in result.output
        assert "DEEP_VAR" in result.output
        assert "DIR1" in result.output
        assert "DIR2" in result.output
        assert "DIR3" in result.output
    finally:
        Path(schema_path).unlink()
