"""
Unit tests for ToolManager class.

Tests the tool filtering and filter specification parsing logic.
"""

import json
import tempfile
from pathlib import Path

import pytest

from mci.core.mci_client import MCIClientWrapper
from mci.core.tool_manager import ToolManager


def create_test_schema(schema_dict: dict) -> str:
    """Helper to create a temporary schema file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mci.json", delete=False) as f:
        json.dump(schema_dict, f)
        return f.name


def test_parse_filter_spec_only():
    """Test parsing 'only' filter specification."""
    filter_type, values = ToolManager.parse_filter_spec("only:tool1,tool2,tool3")
    assert filter_type == "only"
    assert values == ["tool1", "tool2", "tool3"]


def test_parse_filter_spec_except():
    """Test parsing 'except' filter specification."""
    filter_type, values = ToolManager.parse_filter_spec("except:tool1,tool2")
    assert filter_type == "except"
    assert values == ["tool1", "tool2"]


def test_parse_filter_spec_tags():
    """Test parsing 'tags' filter specification."""
    filter_type, values = ToolManager.parse_filter_spec("tags:api,database")
    assert filter_type == "tags"
    assert values == ["api", "database"]


def test_parse_filter_spec_without_tags():
    """Test parsing 'without-tags' filter specification."""
    filter_type, values = ToolManager.parse_filter_spec("without-tags:deprecated,beta")
    assert filter_type == "without-tags"
    assert values == ["deprecated", "beta"]


def test_parse_filter_spec_toolsets():
    """Test parsing 'toolsets' filter specification."""
    filter_type, values = ToolManager.parse_filter_spec("toolsets:weather,database")
    assert filter_type == "toolsets"
    assert values == ["weather", "database"]


def test_parse_filter_spec_single_value():
    """Test parsing filter spec with single value."""
    filter_type, values = ToolManager.parse_filter_spec("only:single_tool")
    assert filter_type == "only"
    assert values == ["single_tool"]


def test_parse_filter_spec_with_spaces():
    """Test parsing filter spec with spaces around values."""
    filter_type, values = ToolManager.parse_filter_spec("tags: api , database , web ")
    assert filter_type == "tags"
    assert values == ["api", "database", "web"]


def test_parse_filter_spec_invalid_no_colon():
    """Test parsing invalid filter spec without colon."""
    with pytest.raises(ValueError, match="Invalid filter specification"):
        ToolManager.parse_filter_spec("invalidspec")


def test_parse_filter_spec_invalid_empty():
    """Test parsing empty filter spec."""
    with pytest.raises(ValueError, match="Invalid filter specification"):
        ToolManager.parse_filter_spec("")


def test_parse_filter_spec_invalid_type():
    """Test parsing filter spec with invalid type."""
    with pytest.raises(ValueError, match="Invalid filter type"):
        ToolManager.parse_filter_spec("invalid:value1,value2")


def test_parse_filter_spec_no_values():
    """Test parsing filter spec with no values."""
    with pytest.raises(ValueError, match="No values provided"):
        ToolManager.parse_filter_spec("only:")


def test_parse_filter_spec_empty_values():
    """Test parsing filter spec with empty values after splitting."""
    with pytest.raises(ValueError, match="No valid values found"):
        ToolManager.parse_filter_spec("tags:,,,")


def test_apply_filter_only():
    """Test applying 'only' filter via MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "Tool 1",
                "execution": {"type": "text", "text": "1"},
            },
            {
                "name": "tool2",
                "description": "Tool 2",
                "execution": {"type": "text", "text": "2"},
            },
            {
                "name": "tool3",
                "description": "Tool 3",
                "execution": {"type": "text", "text": "3"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = ToolManager.apply_filter_spec(wrapper, "only:tool1,tool3")
        assert len(tools) == 2
        assert {t.name for t in tools} == {"tool1", "tool3"}
    finally:
        Path(schema_path).unlink()


def test_apply_filter_except():
    """Test applying 'except' filter via MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "Tool 1",
                "execution": {"type": "text", "text": "1"},
            },
            {
                "name": "tool2",
                "description": "Tool 2",
                "execution": {"type": "text", "text": "2"},
            },
            {
                "name": "tool3",
                "description": "Tool 3",
                "execution": {"type": "text", "text": "3"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = ToolManager.apply_filter_spec(wrapper, "except:tool2")
        assert len(tools) == 2
        assert {t.name for t in tools} == {"tool1", "tool3"}
    finally:
        Path(schema_path).unlink()


def test_apply_filter_tags():
    """Test applying 'tags' filter via MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "Tool 1",
                "tags": ["api", "read"],
                "execution": {"type": "text", "text": "1"},
            },
            {
                "name": "tool2",
                "description": "Tool 2",
                "tags": ["database", "write"],
                "execution": {"type": "text", "text": "2"},
            },
            {
                "name": "tool3",
                "description": "Tool 3",
                "tags": ["api", "write"],
                "execution": {"type": "text", "text": "3"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = ToolManager.apply_filter_spec(wrapper, "tags:api")
        assert len(tools) == 2
        assert {t.name for t in tools} == {"tool1", "tool3"}
    finally:
        Path(schema_path).unlink()


def test_apply_filter_without_tags():
    """Test applying 'without-tags' filter via MCIClient."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "Tool 1",
                "tags": ["api", "deprecated"],
                "execution": {"type": "text", "text": "1"},
            },
            {
                "name": "tool2",
                "description": "Tool 2",
                "tags": ["database"],
                "execution": {"type": "text", "text": "2"},
            },
            {
                "name": "tool3",
                "description": "Tool 3",
                "tags": ["api"],
                "execution": {"type": "text", "text": "3"},
            },
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        tools = ToolManager.apply_filter_spec(wrapper, "without-tags:deprecated")
        assert len(tools) == 2
        assert {t.name for t in tools} == {"tool2", "tool3"}
    finally:
        Path(schema_path).unlink()


def test_apply_filter_invalid_spec():
    """Test applying invalid filter specification raises error."""
    schema = {
        "schemaVersion": "1.0",
        "tools": [
            {
                "name": "tool1",
                "description": "Tool 1",
                "execution": {"type": "text", "text": "1"},
            }
        ],
    }

    schema_path = create_test_schema(schema)
    try:
        wrapper = MCIClientWrapper(schema_path)
        with pytest.raises(ValueError, match="Invalid filter specification"):
            ToolManager.apply_filter_spec(wrapper, "invalidspec")
    finally:
        Path(schema_path).unlink()



