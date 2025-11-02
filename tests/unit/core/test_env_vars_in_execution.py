"""
Unit tests for environment variable handling in tool execution.

Tests that environment variables are properly resolved when tools are
executed through the MCP server.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from mci.core.dynamic_server import DynamicMCPServer


def create_test_schema(schema_dict: dict) -> str:
    """Helper to create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema_dict, f)
        return f.name


@pytest.mark.asyncio
async def test_env_vars_resolved_in_text_execution():
    """
    Test that environment variables are resolved in tool execution.

    Verifies that when a tool uses {{env.VARNAME}} in its execution config,
    the actual environment variable value is substituted at execution time.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "echo_with_env",
                "description": "Echo with environment variable",
                "inputSchema": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                },
                "execution": {
                    "type": "text",
                    "text": "Message: {{props.message}}, Env: {{env.TEST_VAR}}",
                },
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        # Create server with environment variables
        env_vars = {"TEST_VAR": "test-value-123"}
        server = DynamicMCPServer(schema_path, env_vars=env_vars)
        instance = await server.create_from_mci_schema()

        # Execute the tool
        result = await instance.handle_tool_call(
            "echo_with_env", {"message": "Hello"}
        )

        # Verify environment variable was resolved
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].type == "text"
        result_text = result[0].text

        # The result should contain both the message and the env var value
        assert "Hello" in result_text
        assert "test-value-123" in result_text

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_env_vars_from_os_environ():
    """
    Test that environment variables are properly passed through the MCP server.

    This test simulates how env vars are collected from os.environ in the
    run.py command and passed through to the server.
    """
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "check_env",
                "description": "Check environment variable",
                "execution": {
                    "type": "text",
                    "text": "Value: {{env.CUSTOM_ENV_VAR}}",
                },
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        # Simulate what run.py does: collect from os.environ
        test_env_vars = {"CUSTOM_ENV_VAR": "production"}

        server = DynamicMCPServer(schema_path, env_vars=test_env_vars)
        instance = await server.create_from_mci_schema()

        # Execute through MCP server
        result = await instance.handle_tool_call("check_env", {})

        # Verify the environment variable was resolved
        assert isinstance(result, list)
        assert len(result) > 0
        assert "production" in result[0].text

    finally:
        Path(schema_path).unlink()


@pytest.mark.asyncio
async def test_multiple_env_vars_in_execution():
    """Test that multiple environment variables can be resolved in one tool."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "multi_env",
                "description": "Tool using multiple env vars",
                "execution": {
                    "type": "text",
                    "text": "API: {{env.API_KEY}}, URL: {{env.API_URL}}, Port: {{env.API_PORT}}",
                },
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        env_vars = {
            "API_KEY": "secret-key-xyz",
            "API_URL": "https://api.example.com",
            "API_PORT": "8080",
        }

        server = DynamicMCPServer(schema_path, env_vars=env_vars)
        instance = await server.create_from_mci_schema()

        result = await instance.handle_tool_call("multi_env", {})

        assert isinstance(result, list)
        result_text = result[0].text

        # All env vars should be resolved
        assert "secret-key-xyz" in result_text
        assert "https://api.example.com" in result_text
        assert "8080" in result_text

    finally:
        Path(schema_path).unlink()
