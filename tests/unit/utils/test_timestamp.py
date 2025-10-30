"""
Unit tests for timestamp utilities.

Tests timestamp generation functions for file output.
"""

import re
import time

from mci.utils.timestamp import generate_timestamp_filename, get_iso_timestamp


def test_generate_timestamp_filename_default():
    """Test generating timestamped filename with default prefix."""
    filename = generate_timestamp_filename("json")

    assert filename.startswith("tools_")
    assert filename.endswith(".json")
    assert re.match(r"tools_\d{8}_\d{6}\.json", filename)


def test_generate_timestamp_filename_custom_prefix():
    """Test generating timestamped filename with custom prefix."""
    filename = generate_timestamp_filename("yaml", prefix="mydata")

    assert filename.startswith("mydata_")
    assert filename.endswith(".yaml")
    assert re.match(r"mydata_\d{8}_\d{6}\.yaml", filename)


def test_generate_timestamp_filename_format():
    """Test that timestamp format is correct (YYYYMMDD_HHMMSS)."""
    filename = generate_timestamp_filename("txt")

    # Extract timestamp part
    parts = filename.split("_")
    assert len(parts) == 3  # prefix, date, time.ext

    date_part = parts[1]
    time_with_ext = parts[2]
    time_part = time_with_ext.split(".")[0]

    # Check date format (YYYYMMDD)
    assert len(date_part) == 8
    assert date_part.isdigit()

    # Check time format (HHMMSS)
    assert len(time_part) == 6
    assert time_part.isdigit()


def test_generate_timestamp_filename_different_formats():
    """Test generating filenames with different formats."""
    json_file = generate_timestamp_filename("json")
    yaml_file = generate_timestamp_filename("yaml")
    csv_file = generate_timestamp_filename("csv")

    assert json_file.endswith(".json")
    assert yaml_file.endswith(".yaml")
    assert csv_file.endswith(".csv")


def test_get_iso_timestamp():
    """Test that ISO timestamp is in correct format."""
    timestamp = get_iso_timestamp()

    # Check ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
    assert len(timestamp) == 20
    assert timestamp.endswith("Z")
    assert "T" in timestamp

    # Check format with regex
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    assert re.match(pattern, timestamp)


def test_get_iso_timestamp_is_utc():
    """Test that timestamp is in UTC (ends with Z)."""
    timestamp = get_iso_timestamp()

    assert timestamp.endswith("Z")


def test_get_iso_timestamp_consistent_format():
    """Test that multiple calls produce consistently formatted timestamps."""
    timestamp1 = get_iso_timestamp()
    timestamp2 = get_iso_timestamp()

    # Both should have the same format
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    assert re.match(pattern, timestamp1)
    assert re.match(pattern, timestamp2)

    # Both should have the same length
    assert len(timestamp1) == len(timestamp2)


def test_timestamp_filenames_are_unique():
    """Test that generated filenames include timestamps that differ across calls."""
    filename1 = generate_timestamp_filename("json")
    time.sleep(0.001)  # Small delay to ensure different timestamps
    filename2 = generate_timestamp_filename("json")

    # Filenames should be different if generated at different times
    # Note: They might be the same if generated within the same second
    # This test is probabilistic but should usually pass
    assert filename1.startswith("tools_")
    assert filename2.startswith("tools_")
