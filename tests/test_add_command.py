"""
Feature tests for the add command.

These tests exercise the complete workflow from CLI invocation through file modification,
verifying end-to-end behavior and integration. Unlike unit tests (located in tests/unit/),
which test individual components in isolation, these feature tests ensure that the add
command works as expected in real usage scenarios, including format preservation and
various filter types.
"""

import json
import tempfile
from pathlib import Path

import yaml
from click.testing import CliRunner

from mci.cli.add import add


def test_add_simple_toolset_json():
    """Test adding a simple toolset to JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test Project", "description": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()
        result = runner.invoke(add, ["weather-tools", "--path", str(schema_file)])

        assert result.exit_code == 0
        assert "✅ Added toolset 'weather-tools'" in result.output

        # Verify the change
        with open(schema_file) as f:
            data = json.load(f)
        assert "weather-tools" in data["toolsets"]
        assert data["schemaVersion"] == "1.0"  # Other fields preserved


def test_add_toolset_with_only_filter_json():
    """Test adding a toolset with 'only' filter to JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()
        result = runner.invoke(
            add, ["analytics", "--filter", "only:SummarizeData,AnalyzeSentiment", "--path", str(schema_file)]
        )

        assert result.exit_code == 0
        assert "Filter: only:SummarizeData,AnalyzeSentiment" in result.output

        # Verify the filter was applied correctly
        with open(schema_file) as f:
            data = json.load(f)
        
        toolsets = data["toolsets"]
        assert len(toolsets) == 1
        assert toolsets[0]["name"] == "analytics"
        assert toolsets[0]["filter"] == "only"
        assert toolsets[0]["filterValue"] == "SummarizeData,AnalyzeSentiment"


def test_add_simple_toolset_yaml():
    """Test adding a simple toolset to YAML file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.yaml"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test Project", "description": "Test"},
            "tools": [],
            "toolsets": [],
        }
        with open(schema_file, "w") as f:
            yaml.safe_dump(schema_content, f, default_flow_style=False, sort_keys=False)

        runner = CliRunner()
        result = runner.invoke(add, ["weather-tools", "--path", str(schema_file)])

        assert result.exit_code == 0

        # Verify the change and format preservation
        with open(schema_file) as f:
            data = yaml.safe_load(f)
        assert "weather-tools" in data["toolsets"]

        # Verify file is still YAML format
        content = schema_file.read_text()
        assert "schemaVersion:" in content  # YAML key-value format


def test_add_toolset_with_filter_yaml():
    """Test adding a toolset with filter to YAML file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.yaml"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        with open(schema_file, "w") as f:
            yaml.safe_dump(schema_content, f, default_flow_style=False, sort_keys=False)

        runner = CliRunner()
        result = runner.invoke(
            add, ["analytics", "--filter", "tags:api,database", "--path", str(schema_file)]
        )

        assert result.exit_code == 0

        # Verify the change
        with open(schema_file) as f:
            data = yaml.safe_load(f)
        
        toolsets = data["toolsets"]
        assert len(toolsets) == 1
        assert toolsets[0]["name"] == "analytics"
        assert toolsets[0]["filter"] == "tags"
        assert toolsets[0]["filterValue"] == "api,database"


def test_add_multiple_toolsets():
    """Test adding multiple toolsets sequentially."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()

        # Add first toolset
        result1 = runner.invoke(add, ["weather-tools", "--path", str(schema_file)])
        assert result1.exit_code == 0

        # Add second toolset
        result2 = runner.invoke(add, ["analytics", "--path", str(schema_file)])
        assert result2.exit_code == 0

        # Add third toolset with filter
        result3 = runner.invoke(
            add, ["api-tools", "--filter", "tags:api", "--path", str(schema_file)]
        )
        assert result3.exit_code == 0

        # Verify all toolsets are present
        with open(schema_file) as f:
            data = json.load(f)
        
        assert len(data["toolsets"]) == 3
        assert "weather-tools" in data["toolsets"]
        assert "analytics" in data["toolsets"]
        # Third one is an object with filter
        toolset_names = [
            t if isinstance(t, str) else t["name"] for t in data["toolsets"]
        ]
        assert "api-tools" in toolset_names


def test_update_existing_toolset_with_filter():
    """Test updating an existing toolset by adding a filter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": ["weather-tools"],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()
        result = runner.invoke(
            add, ["weather-tools", "--filter", "tags:api", "--path", str(schema_file)]
        )

        assert result.exit_code == 0

        # Verify toolset was updated, not duplicated
        with open(schema_file) as f:
            data = json.load(f)
        
        assert len(data["toolsets"]) == 1
        assert isinstance(data["toolsets"][0], dict)
        assert data["toolsets"][0]["name"] == "weather-tools"
        assert data["toolsets"][0]["filter"] == "tags"


def test_update_existing_filtered_toolset():
    """Test updating an existing toolset that already has a filter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [
                {"name": "analytics", "filter": "only", "filterValue": "Tool1"}
            ],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()
        result = runner.invoke(
            add, ["analytics", "--filter", "except:BadTool", "--path", str(schema_file)]
        )

        assert result.exit_code == 0

        # Verify filter was updated
        with open(schema_file) as f:
            data = json.load(f)
        
        assert len(data["toolsets"]) == 1
        assert data["toolsets"][0]["filter"] == "except"
        assert data["toolsets"][0]["filterValue"] == "BadTool"


def test_add_preserves_existing_toolsets():
    """Test that adding a new toolset preserves existing ones."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [
                "existing-toolset",
                {"name": "filtered-toolset", "filter": "tags", "filterValue": "api"},
            ],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()
        result = runner.invoke(add, ["new-toolset", "--path", str(schema_file)])

        assert result.exit_code == 0

        # Verify all toolsets are present
        with open(schema_file) as f:
            data = json.load(f)
        
        assert len(data["toolsets"]) == 3
        assert "existing-toolset" in data["toolsets"]
        assert "new-toolset" in data["toolsets"]
        # Find the filtered toolset
        filtered = next(t for t in data["toolsets"] if isinstance(t, dict))
        assert filtered["name"] == "filtered-toolset"


def test_add_creates_toolsets_array_if_missing():
    """Test that add creates toolsets array if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()
        result = runner.invoke(add, ["weather-tools", "--path", str(schema_file)])

        assert result.exit_code == 0

        # Verify toolsets array was created
        with open(schema_file) as f:
            data = json.load(f)
        
        assert "toolsets" in data
        assert "weather-tools" in data["toolsets"]


def test_add_with_all_filter_types():
    """Test adding toolsets with all supported filter types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        schema_file = Path(tmpdir) / "mci.json"
        schema_content = {
            "schemaVersion": "1.0",
            "metadata": {"name": "Test"},
            "tools": [],
            "toolsets": [],
        }
        schema_file.write_text(json.dumps(schema_content, indent=2))

        runner = CliRunner()

        # Test 'only' filter
        runner.invoke(add, ["toolset1", "--filter", "only:T1,T2", "--path", str(schema_file)])

        # Test 'except' filter
        runner.invoke(add, ["toolset2", "--filter", "except:T3", "--path", str(schema_file)])

        # Test 'tags' filter
        runner.invoke(add, ["toolset3", "--filter", "tags:api,db", "--path", str(schema_file)])

        # Test 'withoutTags' filter
        runner.invoke(
            add, ["toolset4", "--filter", "withoutTags:old", "--path", str(schema_file)]
        )

        # Verify all filters were applied correctly
        with open(schema_file) as f:
            data = json.load(f)
        
        assert len(data["toolsets"]) == 4
        assert data["toolsets"][0]["filter"] == "only"
        assert data["toolsets"][1]["filter"] == "except"
        assert data["toolsets"][2]["filter"] == "tags"
        assert data["toolsets"][3]["filter"] == "withoutTags"
