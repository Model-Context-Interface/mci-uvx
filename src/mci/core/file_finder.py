"""
file_finder.py - File discovery logic for MCI configuration files

This module provides functionality to locate MCI configuration files (mci.json or mci.yaml)
in a given directory. It prioritizes JSON files when both formats exist and provides
utilities for file format detection and validation.
"""

from pathlib import Path

from mci.utils.validation import file_exists


class MCIFileFinder:
    """
    Handles discovery of MCI configuration files in directories.

    This class provides methods to find MCI configuration files (mci.json or mci.yaml),
    with JSON files taking priority when both formats exist. It also includes utilities
    for file validation and format detection.
    """

    @staticmethod
    def find_mci_file(directory: str = ".") -> str | None:
        """
        Find an MCI configuration file in the specified directory.

        Searches for mci.json first, then mci.yaml/mci.yml if JSON is not found.
        This prioritizes JSON format when both formats exist in the same directory.

        Args:
            directory: The directory path to search in (default: current directory)

        Returns:
            The absolute path to the found MCI file, or None if no file is found

        Example:
            >>> finder = MCIFileFinder()
            >>> path = finder.find_mci_file("./my_project")
            >>> if path:
            ...     print(f"Found: {path}")
        """
        dir_path = Path(directory).resolve()

        # Check for mci.json first (priority)
        json_path = dir_path / "mci.json"
        if json_path.exists() and json_path.is_file():
            return str(json_path)

        # Check for mci.yaml
        yaml_path = dir_path / "mci.yaml"
        if yaml_path.exists() and yaml_path.is_file():
            return str(yaml_path)

        # Check for mci.yml as well
        yml_path = dir_path / "mci.yml"
        if yml_path.exists() and yml_path.is_file():
            return str(yml_path)

        return None

    @staticmethod
    def validate_file_exists(path: str) -> bool:
        """
        Check if a file exists at the given path.

        Delegates to the validation utility module to avoid code duplication.

        Args:
            path: The file path to validate

        Returns:
            True if the file exists and is a file, False otherwise

        Example:
            >>> finder = MCIFileFinder()
            >>> exists = finder.validate_file_exists("./mci.json")
        """
        return file_exists(path)

    @staticmethod
    def get_file_format(path: str) -> str | None:
        """
        Determine the file format based on the file extension.

        Args:
            path: The file path to check

        Returns:
            "json" for .json files, "yaml" for .yaml/.yml files, None for unknown formats

        Example:
            >>> finder = MCIFileFinder()
            >>> fmt = finder.get_file_format("./mci.json")
            >>> print(fmt)  # Output: "json"
        """
        file_path = Path(path)
        ext = file_path.suffix.lower()

        if ext == ".json":
            return "json"
        elif ext in [".yaml", ".yml"]:
            return "yaml"
        else:
            return None
