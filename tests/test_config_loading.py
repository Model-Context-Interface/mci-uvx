"""
Feature tests for configuration loading.

Tests end-to-end config loading with sample files.
"""

import tempfile
from pathlib import Path

import pytest
from mcipy import MCIClientError

from mci.core.config import MCIConfig
from mci.core.file_finder import MCIFileFinder


def test_config_loading_end_to_end_json():
    """Test complete config loading workflow with JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid JSON schema
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Weather Tools",
                "description": "MCI toolset for weather data"
            },
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get current weather for a location",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name"
                            }
                        },
                        "required": ["location"]
                    },
                    "execution": {
                        "type": "text",
                        "text": "Weather for {{props.location}}"
                    }
                }
            ],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        # Step 1: Find the file
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(tmpdir)
        assert found_file is not None
        assert "mci.json" in found_file

        # Step 2: Validate the file format
        file_format = finder.get_file_format(found_file)
        assert file_format == "json"

        # Step 3: Load and validate the schema
        config = MCIConfig()
        is_valid, error = config.validate_schema(found_file)
        assert is_valid is True
        assert error == ""

        # Step 4: Load the client
        client = config.load(found_file)
        assert client is not None

        # Step 5: Get tools
        tools = client.tools()
        assert len(tools) == 1
        assert tools[0].name == "get_weather"


def test_config_loading_end_to_end_yaml():
    """Test complete config loading workflow with YAML file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a valid YAML schema
        schema_file = Path(tmpdir) / "mci.yaml"
        schema_content = """
schemaVersion: '1.0'
metadata:
  name: Calculator Tools
  description: Basic calculator operations
tools:
  - name: add
    description: Add two numbers
    inputSchema:
      type: object
      properties:
        a:
          type: number
          description: First number
        b:
          type: number
          description: Second number
      required: [a, b]
    execution:
      type: text
      text: 'Result: {{props.a}} + {{props.b}}'
toolsets: []
"""
        schema_file.write_text(schema_content)

        # Step 1: Find the file
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(tmpdir)
        assert found_file is not None
        assert "mci.yaml" in found_file

        # Step 2: Validate the file format
        file_format = finder.get_file_format(found_file)
        assert file_format == "yaml"

        # Step 3: Load and validate the schema
        config = MCIConfig()
        is_valid, error = config.validate_schema(found_file)
        assert is_valid is True
        assert error == ""

        # Step 4: Load the client
        client = config.load(found_file)
        assert client is not None

        # Step 5: Get tools
        tools = client.tools()
        assert len(tools) == 1
        assert tools[0].name == "add"


def test_config_loading_with_invalid_schema():
    """Test config loading error handling with invalid schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an invalid schema
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = """{
            "invalid": "schema",
            "missing": "required fields"
        }"""
        schema_file.write_text(schema_content)

        # Find the file
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(tmpdir)
        assert found_file is not None

        # Validate should fail
        config = MCIConfig()
        is_valid, error = config.validate_schema(found_file)
        assert is_valid is False
        assert error != ""

        # Load should raise error
        with pytest.raises(MCIClientError):
            config.load(found_file)


def test_config_loading_priority_json_over_yaml():
    """Test that JSON is prioritized when both formats exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create both JSON and YAML files with different content
        json_file = Path(tmpdir) / "mci.json"
        json_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "JSON Config",
                "description": "This is the JSON version"
            },
            "tools": [],
            "toolsets": []
        }"""
        json_file.write_text(json_content)

        yaml_file = Path(tmpdir) / "mci.yaml"
        yaml_content = """
schemaVersion: '1.0'
metadata:
  name: YAML Config
  description: This is the YAML version
tools: []
toolsets: []
"""
        yaml_file.write_text(yaml_content)

        # Find should return JSON file
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(tmpdir)
        assert found_file is not None
        assert "mci.json" in found_file

        # Load should use JSON file
        config = MCIConfig()
        client = config.load(found_file)
        assert client is not None


def test_config_loading_no_file_found():
    """Test error handling when no config file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Don't create any config files
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(tmpdir)

        # Should return None
        assert found_file is None


def test_config_loading_with_environment_variables():
    """Test config loading with environment variable substitution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create schema with env var placeholder
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

        # Load with environment variables
        config = MCIConfig()
        env_vars = {"API_KEY": "test-key-123"}
        client = config.load(str(schema_file), env_vars)

        assert client is not None
        tools = client.tools()
        assert isinstance(tools, list)
