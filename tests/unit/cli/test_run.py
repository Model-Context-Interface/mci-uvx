"""
Unit tests for run.py - Run CLI command for starting MCP servers.

Tests the run CLI command that starts MCP servers from MCI schemas,
including file discovery, filtering, and error handling.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from mci.cli.run import run


def create_test_schema(schema_dict: dict, filename: str = "mci.json") -> str:
    """Helper to create a temporary schema file."""
    temp_dir = tempfile.mkdtemp()
    schema_path = Path(temp_dir) / filename
    with open(schema_path, "w") as f:
        json.dump(schema_dict, f)
    return str(schema_path)


@pytest.fixture
def basic_schema():
    """Create a basic test schema."""
    return {
        "schemaVersion": "1.0",
        "metadata": {"name": "Test Schema"},
        "tools": [
            {
                "name": "test_tool",
                "description": "A test tool",
                "execution": {"type": "text", "text": "Test output"},
            }
        ],
    }


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


def test_run_default_file(runner, basic_schema):
    """
    Test running server with default file discovery.

    Verifies that the run command finds and uses mci.json/mci.yaml
    from the current directory when --file is not specified.
    """
    schema_path = create_test_schema(basic_schema)

    try:
        # Mock run_server to avoid actually starting the server
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            # Copy schema to isolated filesystem as mci.json
            with runner.isolated_filesystem():
                # Create mci.json in current directory
                with open("mci.json", "w") as f:
                    json.dump(basic_schema, f)

                runner.invoke(run, [])

                # Verify command attempted to start server
                mock_run_server.assert_called_once()

    finally:
        Path(schema_path).unlink()


def test_run_custom_file(runner, basic_schema):
    """
    Test running server with custom file specified via --file option.

    Verifies that the run command uses the specified file when
    --file option is provided.
    """
    schema_path = create_test_schema(basic_schema, "custom.mci.json")

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            result = runner.invoke(run, ["--file", schema_path])

            # Verify run_server was called with correct file
            assert mock_run_server.called
            call_args = mock_run_server.call_args
            assert call_args[0][0] == schema_path
            assert result.exit_code == 0

    finally:
        Path(schema_path).unlink()


def test_run_with_filter(runner, basic_schema):
    """
    Test running server with --filter option.

    Verifies that the run command correctly passes filter specifications
    to the server creation logic.
    """
    schema_path = create_test_schema(basic_schema)

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            result = runner.invoke(run, ["--file", schema_path, "--filter", "tags:api"])
            assert result.exit_code == 0
            # Verify run_server was called with filter
            assert mock_run_server.called
            call_args = mock_run_server.call_args
            assert call_args[0][1] == "tags:api"

    finally:
        Path(schema_path).unlink()


def test_run_with_only_filter(runner, basic_schema):
    """Test running server with 'only' filter type."""
    schema_path = create_test_schema(basic_schema)

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            result = runner.invoke(run, ["--file", schema_path, "--filter", "only:tool1,tool2"])

            assert mock_run_server.called
            call_args = mock_run_server.call_args
            assert call_args[0][1] == "only:tool1,tool2"
            assert result.exit_code == 0

    finally:
        Path(schema_path).unlink()


def test_run_with_except_filter(runner, basic_schema):
    """Test running server with 'except' filter type."""
    schema_path = create_test_schema(basic_schema)

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            result = runner.invoke(run, ["--file", schema_path, "--filter", "except:tool3"])
            assert result.exit_code == 0
            assert mock_run_server.called
            call_args = mock_run_server.call_args
            assert call_args[0][1] == "except:tool3"

    finally:
        Path(schema_path).unlink()


def test_run_with_toolsets_filter(runner, basic_schema):
    """Test running server with 'toolsets' filter type."""
    schema_path = create_test_schema(basic_schema)

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            result = runner.invoke(run, ["--file", schema_path, "--filter", "toolsets:weather"])
            assert result.exit_code == 0
            assert mock_run_server.called
            call_args = mock_run_server.call_args
            assert call_args[0][1] == "toolsets:weather"

    finally:
        Path(schema_path).unlink()


def test_run_with_invalid_filter(runner, basic_schema):
    """
    Test that run command rejects invalid filter specifications.

    Verifies that the command validates filter format early and
    provides clear error messages.
    """
    schema_path = create_test_schema(basic_schema)

    try:
        result = runner.invoke(run, ["--file", schema_path, "--filter", "invalid-filter"])

        # Should fail with error about invalid filter
        assert result.exit_code != 0
        assert "Invalid filter" in result.output

    finally:
        Path(schema_path).unlink()


def test_run_without_file_not_found(runner):
    """
    Test that run command fails gracefully when no MCI file is found.

    Verifies that the command displays a helpful error message when
    no mci.json or mci.yaml exists in the current directory.
    """
    with runner.isolated_filesystem():
        result = runner.invoke(run, [])

        # Should fail with error about missing file
        assert result.exit_code != 0
        assert "No MCI schema file found" in result.output


def test_run_with_nonexistent_file(runner):
    """
    Test that run command fails gracefully for nonexistent files.

    Verifies that the command handles file not found errors properly.
    """
    result = runner.invoke(run, ["--file", "nonexistent.mci.json"])

    # Click should validate that file exists
    assert result.exit_code != 0


def test_run_displays_startup_message(runner, basic_schema):
    """
    Test that run command displays startup information.

    Verifies that the command shows the schema file path and filter
    information before starting the server.
    """
    schema_path = create_test_schema(basic_schema)

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock):
            result = runner.invoke(run, ["--file", schema_path, "--filter", "tags:api"])

            # Verify startup message is displayed
            assert "Starting MCP server" in result.output
            assert schema_path in result.output
            assert "tags:api" in result.output

    finally:
        Path(schema_path).unlink()


def test_run_handles_keyboard_interrupt(runner, basic_schema):
    """
    Test that run command handles Ctrl+C gracefully.

    Verifies that KeyboardInterrupt is caught and displays a
    graceful shutdown message.
    """
    schema_path = create_test_schema(basic_schema)

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            # Simulate KeyboardInterrupt
            mock_run_server.side_effect = KeyboardInterrupt()

            result = runner.invoke(run, ["--file", schema_path])

            # Should handle interrupt gracefully
            assert "Server stopped" in result.output or result.exit_code == 0

    finally:
        Path(schema_path).unlink()


def test_run_passes_environment_variables(runner, basic_schema):
    """
    Test that run command passes environment variables to server.

    Verifies that the command collects and passes environment variables
    for template substitution in tool definitions.
    """
    schema_path = create_test_schema(basic_schema)

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            runner.invoke(run, ["--file", schema_path])

            # Verify environment variables were passed
            assert mock_run_server.called
            call_args = mock_run_server.call_args
            env_vars = call_args[0][2]  # Third argument is env_vars
            assert isinstance(env_vars, dict)
            # Should have at least some environment variables
            assert len(env_vars) > 0

    finally:
        Path(schema_path).unlink()
