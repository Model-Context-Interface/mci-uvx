"""
timestamp.py - Timestamp utilities for file output

This module provides utilities for generating timestamped filenames
and ISO 8601 timestamps for use in CLI output files.
"""

from datetime import UTC, datetime


def generate_timestamp_filename(format: str, prefix: str = "tools") -> str:
    """
    Generate a timestamped filename for output files.

    Creates a filename in the format: {prefix}_YYYYMMDD_HHMMSS.{format}
    Uses UTC time for consistency.

    Args:
        format: File extension (e.g., "json", "yaml")
        prefix: Filename prefix (default: "tools")

    Returns:
        Timestamped filename string (e.g., "tools_20241029_143022.json")

    Example:
        >>> filename = generate_timestamp_filename("json")
        >>> print(filename)
        tools_20241029_143022.json
    """
    now = datetime.now(UTC)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{format}"


def get_iso_timestamp() -> str:
    """
    Get current timestamp in ISO 8601 format.

    Returns UTC timestamp in ISO 8601 format for use in metadata.

    Returns:
        ISO 8601 formatted timestamp string

    Example:
        >>> timestamp = get_iso_timestamp()
        >>> print(timestamp)
        2024-10-29T14:30:22Z
    """
    now = datetime.now(UTC)
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")
