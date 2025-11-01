"""
validation.py - File validation utilities for MCI

This module provides utility functions for file validation,
including file existence checks, format detection, and path validation.
"""

import os
from pathlib import Path


def is_valid_path(path: str) -> bool:
    """
    Check if a path is valid and accessible.

    Args:
        path: The path to validate

    Returns:
        True if the path is valid, False otherwise

    Example:
        >>> is_valid_path("./mci.json")
        True
        >>> is_valid_path("")
        False
    """
    if not path:
        return False

    try:
        Path(path)
        return True
    except (ValueError, TypeError):
        return False


def file_exists(path: str) -> bool:
    """
    Check if a file exists at the given path.

    Args:
        path: The file path to check

    Returns:
        True if the file exists and is a file, False otherwise

    Example:
        >>> file_exists("./mci.json")
        True
    """
    try:
        return Path(path).is_file()
    except (OSError, ValueError):
        return False


def is_readable(path: str) -> bool:
    """
    Check if a file is readable.

    Args:
        path: The file path to check

    Returns:
        True if the file is readable, False otherwise

    Example:
        >>> is_readable("./mci.json")
        True
    """
    try:
        return os.access(path, os.R_OK)
    except (OSError, ValueError, TypeError):
        return False


def get_absolute_path(path: str) -> str:
    """
    Get the absolute path from a relative or absolute path.

    Args:
        path: The path to resolve

    Returns:
        The absolute path

    Example:
        >>> get_absolute_path("./mci.json")
        '/path/to/current/dir/mci.json'
    """
    return str(Path(path).resolve())
