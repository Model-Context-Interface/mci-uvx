"""
Unit tests for the SchemaEditor class.

Tests schema file editing functionality including adding toolsets,
preserving file format, and handling duplicates.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from mci.core.schema_editor import SchemaEditor, parse_add_filter


def test_load_json_schema():
    """Test loading a JSON schema file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        loaded_schema = editor.load_schema(str(schema_file))

        assert loaded_schema == schema_content
        assert editor.preserve_format() == "json"


def test_load_yaml_schema():
    """Test loading a YAML schema file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.yaml"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        with open(schema_file, "w") as f:
            yaml.safe_dump(schema_content, f)

        editor = SchemaEditor()
        loaded_schema = editor.load_schema(str(schema_file))

        assert loaded_schema["schemaVersion"] == "1.0"
        assert editor.preserve_format() == "yaml"


def test_load_missing_file():
    """Test loading a non-existent file raises FileNotFoundError."""
    editor = SchemaEditor()
    with pytest.raises(FileNotFoundError):
        editor.load_schema("/nonexistent/file.json")


def test_load_unsupported_format():
    """Test loading a file with unsupported format raises ValueError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.txt"
        schema_file.write_text("invalid")

        editor = SchemaEditor()
        with pytest.raises(ValueError, match="Unsupported file format"):
            editor.load_schema(str(schema_file))


def test_add_simple_toolset():
    """Test adding a simple toolset without filter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools")

        assert "weather-tools" in editor.schema_data["toolsets"]


def test_add_toolset_with_filter():
    """Test adding a toolset with filter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("analytics", "only", "Tool1,Tool2")

        toolsets = editor.schema_data["toolsets"]
        assert len(toolsets) == 1
        assert isinstance(toolsets[0], dict)
        assert toolsets[0]["name"] == "analytics"
        assert toolsets[0]["filter"] == "only"
        assert toolsets[0]["filterValue"] == "Tool1,Tool2"


def test_add_duplicate_toolset():
    """Test adding a duplicate toolset updates the existing one."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": ["weather-tools"],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools", "tags", "api")

        toolsets = editor.schema_data["toolsets"]
        assert len(toolsets) == 1
        assert isinstance(toolsets[0], dict)
        assert toolsets[0]["name"] == "weather-tools"
        assert toolsets[0]["filter"] == "tags"


def test_add_duplicate_object_toolset():
    """Test adding a duplicate object toolset updates it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [{"name": "analytics", "filter": "only", "filterValue": "Tool1"}],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("analytics", "except", "Tool2,Tool3")

        toolsets = editor.schema_data["toolsets"]
        assert len(toolsets) == 1
        assert toolsets[0]["filter"] == "except"
        assert toolsets[0]["filterValue"] == "Tool2,Tool3"


def test_preserve_json_format():
    """Test saving back as JSON preserves format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools")
        editor.save_schema()

        # Verify file is still JSON
        with open(schema_file) as f:
            saved_data = json.load(f)
        assert "weather-tools" in saved_data["toolsets"]


def test_preserve_yaml_format():
    """Test saving back as YAML preserves format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.yaml"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        with open(schema_file, "w") as f:
            yaml.safe_dump(schema_content, f)

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools")
        editor.save_schema()

        # Verify file is still YAML
        with open(schema_file) as f:
            saved_data = yaml.safe_load(f)
        assert "weather-tools" in saved_data["toolsets"]


def test_save_to_different_path():
    """Test saving to a different path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        new_file = Path(tmpdir) / "custom.mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools")
        editor.save_schema(str(new_file))

        # Verify new file exists
        assert new_file.exists()
        with open(new_file) as f:
            saved_data = json.load(f)
        assert "weather-tools" in saved_data["toolsets"]


def test_add_without_loading_raises_error():
    """Test adding toolset without loading schema raises ValueError."""
    editor = SchemaEditor()
    with pytest.raises(ValueError, match="No schema loaded"):
        editor.add_toolset("weather-tools")


def test_save_without_loading_raises_error():
    """Test saving without loading schema raises ValueError."""
    editor = SchemaEditor()
    with pytest.raises(ValueError, match="No schema loaded"):
        editor.save_schema()


def test_preserve_format_without_loading_raises_error():
    """Test preserve_format without loading schema raises ValueError."""
    editor = SchemaEditor()
    with pytest.raises(ValueError, match="No schema loaded"):
        editor.preserve_format()


def test_add_toolset_creates_toolsets_array():
    """Test add_toolset creates toolsets array if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))
        editor.add_toolset("weather-tools")

        assert "toolsets" in editor.schema_data
        assert "weather-tools" in editor.schema_data["toolsets"]


def test_filter_validation():
    """Test filter validation requires both type and value."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content))

        editor = SchemaEditor()
        editor.load_schema(str(schema_file))

        # Should raise error if filter_type provided without filter_value
        with pytest.raises(ValueError, match="must both be provided"):
            editor.add_toolset("weather-tools", filter_type="only", filter_value=None)

        # Should raise error if filter_value provided without filter_type
        with pytest.raises(ValueError, match="must both be provided"):
            editor.add_toolset("weather-tools", filter_type=None, filter_value="Tool1")


def test_parse_add_filter_only():
    """Test parsing 'only' filter specification."""
    filter_type, filter_value = parse_add_filter("only:Tool1,Tool2,Tool3")
    assert filter_type == "only"
    assert filter_value == "Tool1,Tool2,Tool3"


def test_parse_add_filter_except():
    """Test parsing 'except' filter specification."""
    filter_type, filter_value = parse_add_filter("except:Tool1,Tool2")
    assert filter_type == "except"
    assert filter_value == "Tool1,Tool2"


def test_parse_add_filter_tags():
    """Test parsing 'tags' filter specification."""
    filter_type, filter_value = parse_add_filter("tags:api,database")
    assert filter_type == "tags"
    assert filter_value == "api,database"


def test_parse_add_filter_without_tags():
    """Test parsing 'withoutTags' filter specification."""
    filter_type, filter_value = parse_add_filter("withoutTags:internal,deprecated")
    assert filter_type == "withoutTags"
    assert filter_value == "internal,deprecated"


def test_parse_add_filter_invalid_format():
    """Test parsing invalid filter format raises ValueError."""
    with pytest.raises(ValueError, match="Invalid filter specification"):
        parse_add_filter("invalid_format")

    with pytest.raises(ValueError, match="Invalid filter specification"):
        parse_add_filter("only")


def test_parse_add_filter_invalid_type():
    """Test parsing invalid filter type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid filter type"):
        parse_add_filter("invalid:Tool1,Tool2")


def test_parse_add_filter_empty_values():
    """Test parsing filter with empty values raises ValueError."""
    with pytest.raises(ValueError, match="No values provided"):
        parse_add_filter("only:")

    with pytest.raises(ValueError, match="No valid values found"):
        parse_add_filter("only:,,,")
