"""
Unit tests for MCIFileFinder.

Tests the file discovery logic for MCI configuration files.
"""

import tempfile
from pathlib import Path

from mci.core.file_finder import MCIFileFinder


def test_find_json_file():
    """Test that MCIFileFinder can find mci.json file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci.json file
        json_file = Path(tmpdir) / "mci.json"
        json_file.write_text('{"schemaVersion": "1.0"}')

        finder = MCIFileFinder()
        result = finder.find_mci_file(tmpdir)

        assert result is not None
        assert result == str(json_file)
        assert "mci.json" in result


def test_find_yaml_file():
    """Test that MCIFileFinder can find mci.yaml file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci.yaml file
        yaml_file = Path(tmpdir) / "mci.yaml"
        yaml_file.write_text("schemaVersion: '1.0'")

        finder = MCIFileFinder()
        result = finder.find_mci_file(tmpdir)

        assert result is not None
        assert result == str(yaml_file)
        assert "mci.yaml" in result


def test_find_yml_file():
    """Test that MCIFileFinder can find mci.yml file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci.yml file
        yml_file = Path(tmpdir) / "mci.yml"
        yml_file.write_text("schemaVersion: '1.0'")

        finder = MCIFileFinder()
        result = finder.find_mci_file(tmpdir)

        assert result is not None
        assert result == str(yml_file)
        assert "mci.yml" in result


def test_find_priority_json_over_yaml():
    """Test that JSON is preferred when both JSON and YAML exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create both mci.json and mci.yaml
        json_file = Path(tmpdir) / "mci.json"
        json_file.write_text('{"schemaVersion": "1.0"}')

        yaml_file = Path(tmpdir) / "mci.yaml"
        yaml_file.write_text("schemaVersion: '1.0'")

        finder = MCIFileFinder()
        result = finder.find_mci_file(tmpdir)

        # Should return JSON file, not YAML
        assert result is not None
        assert result == str(json_file)
        assert "mci.json" in result
        assert "mci.yaml" not in result


def test_no_file_found():
    """Test that None is returned when no MCI file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Don't create any MCI files
        finder = MCIFileFinder()
        result = finder.find_mci_file(tmpdir)

        assert result is None


def test_validate_file_exists_true():
    """Test that validate_file_exists returns True for existing files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / "test.json"
        test_file.write_text("{}")

        finder = MCIFileFinder()
        result = finder.validate_file_exists(str(test_file))

        assert result is True


def test_validate_file_exists_false():
    """Test that validate_file_exists returns False for non-existing files."""
    finder = MCIFileFinder()
    result = finder.validate_file_exists("/nonexistent/path/to/file.json")

    assert result is False


def test_validate_file_exists_directory():
    """Test that validate_file_exists returns False for directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        finder = MCIFileFinder()
        result = finder.validate_file_exists(tmpdir)

        # Should return False for directories
        assert result is False


def test_get_file_format_json():
    """Test that get_file_format returns 'json' for .json files."""
    finder = MCIFileFinder()
    result = finder.get_file_format("path/to/mci.json")

    assert result == "json"


def test_get_file_format_yaml():
    """Test that get_file_format returns 'yaml' for .yaml files."""
    finder = MCIFileFinder()
    result = finder.get_file_format("path/to/mci.yaml")

    assert result == "yaml"


def test_get_file_format_yml():
    """Test that get_file_format returns 'yaml' for .yml files."""
    finder = MCIFileFinder()
    result = finder.get_file_format("path/to/mci.yml")

    assert result == "yaml"


def test_get_file_format_unknown():
    """Test that get_file_format returns None for unknown formats."""
    finder = MCIFileFinder()
    result = finder.get_file_format("path/to/file.txt")

    assert result is None


def test_get_file_format_case_insensitive():
    """Test that get_file_format handles uppercase extensions."""
    finder = MCIFileFinder()

    assert finder.get_file_format("path/to/file.JSON") == "json"
    assert finder.get_file_format("path/to/file.YAML") == "yaml"
    assert finder.get_file_format("path/to/file.YML") == "yaml"


def test_find_mci_file_default_directory():
    """Test that find_mci_file uses current directory by default."""
    finder = MCIFileFinder()
    # This should not raise an error even if no file is found
    result = finder.find_mci_file()

    # Result can be None or a path if mci.json/yaml exists in current dir
    assert result is None or isinstance(result, str)


def test_find_mci_file_absolute_path():
    """Test that find_mci_file returns absolute paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mci.json file
        json_file = Path(tmpdir) / "mci.json"
        json_file.write_text('{"schemaVersion": "1.0"}')

        finder = MCIFileFinder()
        result = finder.find_mci_file(tmpdir)

        assert result is not None
        # The result should be an absolute path
        assert Path(result).is_absolute()
