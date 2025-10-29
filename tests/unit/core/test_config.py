"""
Unit tests for MCIConfig.

Tests the configuration loading and validation using MCIClient.
"""

import tempfile
from pathlib import Path

import pytest
from mcipy import MCIClientError

from mci.core.config import MCIConfig


def test_load_valid_schema_with_mciclient():
    """Test loading a valid schema using MCIClient."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid MCI schema file
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test MCI configuration"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        client = config.load(str(schema_file))

        # Should successfully load without errors
        assert client is not None
        # Should be able to get tools (even if empty)
        tools = client.tools()
        assert isinstance(tools, list)


def test_invalid_schema_caught_by_mciclient():
    """Test that MCIClient catches invalid schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an invalid schema (missing required fields)
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "invalid": "schema"
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        with pytest.raises(MCIClientError):
            config.load(str(schema_file))


def test_missing_file_error():
    """Test that loading a non-existent file raises MCIClientError."""
    config = MCIConfig()
    with pytest.raises(MCIClientError):
        config.load("/nonexistent/path/to/mci.json")


def test_validate_schema_valid():
    """Test validating a valid schema returns (True, '')."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid MCI schema file
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test MCI configuration"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        is_valid, error = config.validate_schema(str(schema_file))

        assert is_valid is True
        assert error == ""


def test_validate_schema_invalid():
    """Test validating an invalid schema returns (False, error_message)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an invalid schema
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "invalid": "schema"
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        is_valid, error = config.validate_schema(str(schema_file))

        assert is_valid is False
        assert error != ""
        assert len(error) > 0


def test_validate_schema_missing_file():
    """Test validating a non-existent file returns (False, error_message)."""
    config = MCIConfig()
    is_valid, error = config.validate_schema("/nonexistent/path/to/mci.json")

    assert is_valid is False
    assert error != ""
    assert "not found" in error.lower() or "error" in error.lower()


def test_error_message_extraction():
    """Test that error messages from MCIClient are properly extracted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an invalid schema
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "invalid": "schema"
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        is_valid, error = config.validate_schema(str(schema_file))

        # Error message should be extracted and non-empty
        assert is_valid is False
        assert isinstance(error, str)
        assert len(error) > 0


def test_load_with_env_vars():
    """Test loading schema with environment variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a schema with environment variable templates
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test MCI configuration"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        env_vars = {"TEST_VAR": "test_value"}
        client = config.load(str(schema_file), env_vars)

        # Should successfully load with env vars
        assert client is not None


def test_validate_schema_with_env_vars():
    """Test validating schema with environment variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid schema
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test MCI configuration"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        env_vars = {"TEST_VAR": "test_value"}
        is_valid, error = config.validate_schema(str(schema_file), env_vars)

        assert is_valid is True
        assert error == ""


def test_load_yaml_file():
    """Test loading a YAML schema file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid YAML schema file
        schema_file = Path(tmpdir) / "mci.yaml"
        schema_content = """
schemaVersion: '1.0'
metadata:
  name: Test Project
  description: Test MCI configuration
tools: []
toolsets: []
"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        client = config.load(str(schema_file))

        # Should successfully load YAML file
        assert client is not None
        tools = client.tools()
        assert isinstance(tools, list)


def test_malformed_json_error():
    """Test that malformed JSON is caught."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a malformed JSON file
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "invalid json
        }"""
        schema_file.write_text(schema_content)

        config = MCIConfig()
        with pytest.raises(MCIClientError):
            config.load(str(schema_file))
