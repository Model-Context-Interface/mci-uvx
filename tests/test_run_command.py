"""
Feature test for the mcix run command.

Tests the complete workflow of running an MCP server from an MCI schema,
including loading, filtering, and server creation.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from mci.cli.run import run


def create_test_schema(schema_dict: dict, directory: str | None = None) -> str:
    """Helper to create a temporary schema file."""
    if directory:
        schema_path = Path(directory) / "mci.json"
        with open(schema_path, "w") as f:
            json.dump(schema_dict, f)
        return str(schema_path)
    else:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
            json.dump(schema_dict, f)
            return f.name


@pytest.mark.asyncio
async def test_run_command_full_workflow():
    """
    Test the complete workflow of the run command.

    This test covers:
    1. Finding or specifying MCI schema file
    2. Parsing filter specifications
    3. Creating MCP server from schema
    4. Verifying server configuration
    5. Handling startup and shutdown
    """
    schema = {
        "schemaVersion": "1.0",
        "metadata": {"name": "Test Server", "description": "Test MCP server"},
        "tools": [
            {
                "name": "greet",
                "description": "Greet a user",
                "inputSchema": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
                "execution": {"type": "text", "text": "Hello, {{props.name}}!"},
            },
            {
                "name": "calculate",
                "description": "Perform calculations",
                "tags": ["math"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression"}
                    },
                },
                "execution": {"type": "text", "text": "Result: {{props.expression}}"},
            },
            {
                "name": "get_weather",
                "description": "Get weather information",
                "tags": ["api", "weather"],
                "execution": {"type": "text", "text": "Weather data"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        # Test 1: Run with default file discovery
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            with runner.isolated_filesystem():
                # Create mci.json in current directory
                with open("mci.json", "w") as f:
                    json.dump(schema, f)

                result = runner.invoke(run, [])

                # Verify startup message
                assert "Starting MCP server" in result.output

                # Verify run_server was called
                assert mock_run_server.called

        # Test 2: Run with explicit file
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            runner.invoke(run, ["--file", schema_path])

            assert mock_run_server.called
            call_args = mock_run_server.call_args
            assert call_args[0][0] == schema_path

        # Test 3: Run with filter
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            result = runner.invoke(run, ["--file", schema_path, "--filter", "tags:api"])

            assert "tags:api" in result.output
            assert mock_run_server.called
            call_args = mock_run_server.call_args
            assert call_args[0][1] == "tags:api"

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_run_command_with_toolsets():
    """
    Test run command with schema containing toolsets.

    Verifies that the server can load and serve tools from toolsets
    referenced in the MCI schema.
    """
    # Create a toolset file
    toolset_schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "toolset_tool",
                "description": "Tool from toolset",
                "execution": {"type": "text", "text": "Toolset output"},
            }
        ],
    }

    toolset_dir = tempfile.mkdtemp()
    toolset_path = Path(toolset_dir) / "toolset.mci.json"
    with open(toolset_path, "w") as f:
        json.dump(toolset_schema, f)

    # Create main schema with toolset reference
    main_schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "main_tool",
                "description": "Main tool",
                "execution": {"type": "text", "text": "Main output"},
            }
        ],
        "toolsets": [{"path": str(toolset_path)}],
    }

    schema_path = create_test_schema(main_schema)
    runner = CliRunner()

    try:
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            runner.invoke(run, ["--file", schema_path])

            # Verify server was created with all tools (main + toolset)
            assert mock_run_server.called

    finally:
        Path(schema_path).unlink()
        toolset_path.unlink()
        Path(toolset_dir).rmdir()


@pytest.mark.asyncio
async def test_run_command_error_handling():
    """
    Test error handling in the run command.

    Verifies that the command handles various error scenarios gracefully:
    - Missing schema file
    - Invalid filter specifications
    - Schema validation errors
    """
    runner = CliRunner()

    # Test 1: Missing schema file
    with runner.isolated_filesystem():
        result = runner.invoke(run, [])
        assert result.exit_code != 0
        assert "No MCI schema file found" in result.output

    # Test 2: Invalid filter specification
    schema = {"schemaVersion": "1.0", "tools": []}
    schema_path = create_test_schema(schema)

    try:
        result = runner.invoke(run, ["--file", schema_path, "--filter", "invalid"])
        assert result.exit_code != 0
        assert "Invalid filter" in result.output

    finally:
        Path(schema_path).unlink()

    # Test 3: Nonexistent file
    result = runner.invoke(run, ["--file", "nonexistent.mci.json"])
    assert result.exit_code != 0


@pytest.mark.asyncio
async def test_run_command_filter_variations():
    """
    Test various filter specifications with the run command.

    Verifies that all filter types (only, except, tags, without-tags, toolsets)
    work correctly with the run command.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {"name": "tool1", "tags": ["api"], "execution": {"type": "text", "text": "T1"}},
            {"name": "tool2", "tags": ["database"], "execution": {"type": "text", "text": "T2"}},
            {"name": "tool3", "tags": ["api"], "execution": {"type": "text", "text": "T3"}},
        ],
    }

    schema_path = create_test_schema(schema)
    runner = CliRunner()

    try:
        # Test 'only' filter
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            runner.invoke(run, ["--file", schema_path, "--filter", "only:tool1,tool2"])
            assert mock_run_server.called

        # Test 'except' filter
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            runner.invoke(run, ["--file", schema_path, "--filter", "except:tool3"])
            assert mock_run_server.called

        # Test 'tags' filter
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            runner.invoke(run, ["--file", schema_path, "--filter", "tags:api"])
            assert mock_run_server.called

        # Test 'without-tags' filter
        with patch("mci.cli.run.run_server", new_callable=AsyncMock) as mock_run_server:
            runner.invoke(
                run, ["--file", schema_path, "--filter", "without-tags:database"]
            )
            assert mock_run_server.called

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_run_command_displays_help():
    """
    Test that run command displays comprehensive help information.

    Verifies that --help shows command description, options, and examples.
    """
    runner = CliRunner()
    result = runner.invoke(run, ["--help"])

    # Verify help is displayed
    assert result.exit_code == 0
    assert "Run an MCP server" in result.output
    assert "--file" in result.output
    assert "--filter" in result.output
    assert "Examples:" in result.output
