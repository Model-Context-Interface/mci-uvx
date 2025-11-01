"""
Unit tests for validation utilities.

Tests file validation functions including path validation,
file existence checks, and path resolution.
"""

import os
import tempfile
from pathlib import Path

from mci.utils.validation import (
    file_exists,
    get_absolute_path,
    is_readable,
    is_valid_path,
)


def test_is_valid_path_with_valid_path():
    """Test is_valid_path with a valid path."""
    assert is_valid_path("./mci.json") is True
    assert is_valid_path("/tmp/test.json") is True
    assert is_valid_path("test.yaml") is True


def test_is_valid_path_with_empty_string():
    """Test is_valid_path with empty string."""
    assert is_valid_path("") is False


def test_is_valid_path_with_none():
    """Test is_valid_path with None (should handle TypeError)."""
    # Type ignore because we're testing error handling
    assert is_valid_path(None) is False  # type: ignore[arg-type]


def test_is_valid_path_with_invalid_type():
    """Test is_valid_path with invalid type."""
    # Test with number (should handle TypeError)
    assert is_valid_path(123) is False  # type: ignore[arg-type]


def test_file_exists_with_existing_file():
    """Test file_exists with an existing file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name

    try:
        assert file_exists(tmp_path) is True
    finally:
        os.unlink(tmp_path)


def test_file_exists_with_nonexistent_file():
    """Test file_exists with a nonexistent file."""
    temp_path = os.path.join(tempfile.gettempdir(), "nonexistent_file_12345.json")
    assert file_exists(temp_path) is False


def test_file_exists_with_directory():
    """Test file_exists with a directory (should return False)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        assert file_exists(tmp_dir) is False


def test_file_exists_with_invalid_path():
    """Test file_exists with invalid path."""
    # Test with empty string
    assert file_exists("") is False


def test_is_readable_with_readable_file():
    """Test is_readable with a readable file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
        tmp.write("test content")
        tmp_path = tmp.name

    try:
        assert is_readable(tmp_path) is True
    finally:
        os.unlink(tmp_path)


def test_is_readable_with_nonexistent_file():
    """Test is_readable with a nonexistent file."""
    temp_path = os.path.join(tempfile.gettempdir(), "nonexistent_file_12345.json")
    assert is_readable(temp_path) is False


def test_is_readable_with_empty_path():
    """Test is_readable with empty path."""
    assert is_readable("") is False


def test_get_absolute_path_with_relative_path():
    """Test get_absolute_path with a relative path."""
    result = get_absolute_path("./test.json")
    assert Path(result).is_absolute()
    assert result.endswith("test.json")


def test_get_absolute_path_with_absolute_path():
    """Test get_absolute_path with an absolute path."""
    result = get_absolute_path("/tmp/test.json")
    assert result == "/tmp/test.json"


def test_get_absolute_path_with_current_dir():
    """Test get_absolute_path with current directory."""
    result = get_absolute_path(".")
    assert Path(result).is_absolute()


def test_file_exists_with_oserror_path():
    """Test file_exists with path that causes OSError."""
    # Test with extremely long path that might cause OSError
    long_path = "x" * 5000
    assert file_exists(long_path) is False


def test_is_readable_with_invalid_type():
    """Test is_readable with invalid type to trigger TypeError."""
    # Using type ignore since we're testing error handling
    # os.access raises TypeError for None, which should be caught
    assert is_readable(None) is False  # type: ignore[arg-type]
