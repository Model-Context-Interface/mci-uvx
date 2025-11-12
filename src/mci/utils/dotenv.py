"""
dotenv.py - Environment variable file parsing utilities

This module provides functionality to parse .env files using the python-dotenv library
and merge environment variables from multiple sources. It supports:
- Standard .env format via python-dotenv
- Comments starting with #
- Blank lines
- Export keyword (which is ignored)
- Quoted values

The module is used to automatically load .env files from the project root
and ./mci directory when initializing MCI configurations. It supports both
.env and .env.mci files, with .env.mci taking precedence for MCI-specific
configuration.
"""

import os
from pathlib import Path

from dotenv import dotenv_values


def parse_dotenv_file(file_path: str | Path) -> dict[str, str]:
    """
    Parse a .env file and return a dictionary of environment variables.

    This function uses python-dotenv to parse .env files, which supports:
    - KEY=VALUE format
    - Lines starting with # are comments (ignored)
    - Blank lines are ignored
    - Export keyword is ignored (e.g., "export KEY=VALUE" is treated as "KEY=VALUE")
    - Values can be quoted with single or double quotes
    - Variable expansion and interpolation (if needed)

    Args:
        file_path: Path to the .env file to parse

    Returns:
        Dictionary of environment variable key-value pairs (excluding None values)

    Example:
        >>> env_vars = parse_dotenv_file(".env")
        >>> print(env_vars.get("API_KEY"))
        'my-secret-key'
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return {}

    try:
        # Use dotenv_values to parse the file
        # This returns a dict with all variables, including None for empty values
        env_dict = dotenv_values(file_path)
        # Filter out None values and convert to strings
        return {k: str(v) for k, v in env_dict.items() if v is not None}
    except (OSError, UnicodeDecodeError):
        # If we can't read the file, return empty dict (silent failure)
        # This maintains the "no error if .env is missing" requirement
        return {}


def find_and_merge_dotenv_files(project_root: str | Path | None = None) -> dict[str, str]:
    """
    Find and merge .env files from project root and ./mci directory.

    This function looks for .env files with the following priority order:
    1. Check for .env.mci files first (MCI-specific configs have priority)
       a. {project_root}/mci/.env.mci (MCI library MCI-specific)
       b. {project_root}/.env.mci (project MCI-specific - highest priority)
    2. If no .env.mci files exist, check for .env files
       a. {project_root}/mci/.env (MCI library defaults)
       b. {project_root}/.env (project-level configs)

    Variables from files loaded later override those from earlier files.

    Args:
        project_root: Path to the project root directory. If None, uses current directory.

    Returns:
        Dictionary of merged environment variables

    Example:
        >>> env_vars = find_and_merge_dotenv_files()
        >>> # Variables from root .env.mci override all others
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    merged_env: dict[str, str] = {}

    # Check for .env.mci files first (MCI-specific configs)
    mci_env_mci_path = project_root / "mci" / ".env.mci"
    root_env_mci_path = project_root / ".env.mci"

    has_env_mci = mci_env_mci_path.exists() or root_env_mci_path.exists()

    if has_env_mci:
        # Priority order for .env.mci files (lowest to highest):
        # 1. ./mci/.env.mci (library MCI-specific)
        if mci_env_mci_path.exists():
            mci_env_mci_vars = parse_dotenv_file(mci_env_mci_path)
            merged_env.update(mci_env_mci_vars)

        # 2. .env.mci (project root MCI-specific - highest priority)
        if root_env_mci_path.exists():
            root_env_mci_vars = parse_dotenv_file(root_env_mci_path)
            merged_env.update(root_env_mci_vars)
    else:
        # No .env.mci files found, check for .env files
        # Priority order for .env files (lowest to highest):
        # 1. ./mci/.env (library defaults)
        mci_env_path = project_root / "mci" / ".env"
        if mci_env_path.exists():
            mci_env_vars = parse_dotenv_file(mci_env_path)
            merged_env.update(mci_env_vars)

        # 2. .env (project root - higher priority)
        root_env_path = project_root / ".env"
        if root_env_path.exists():
            root_env_vars = parse_dotenv_file(root_env_path)
            merged_env.update(root_env_vars)

    return merged_env


def get_env_with_dotenv(
    project_root: str | Path | None = None, additional_env: dict[str, str] | None = None
) -> dict[str, str]:
    """
    Get complete environment variables including system, .env files, and additional vars.

    The precedence order (lowest to highest):
    - If .env.mci files exist:
      1. ./mci/.env.mci (library MCI-specific)
      2. {project_root}/.env.mci (project MCI-specific)
    - If no .env.mci files exist:
      1. ./mci/.env (library defaults)
      2. {project_root}/.env (project-level)
    - Then:
      3. System environment variables (os.environ)
      4. Additional environment variables passed as argument (highest)

    Args:
        project_root: Path to the project root directory. If None, uses current directory.
        additional_env: Additional environment variables to merge (highest priority)

    Returns:
        Dictionary of merged environment variables with proper precedence

    Example:
        >>> # Get all env vars with .env files loaded
        >>> env_vars = get_env_with_dotenv()
        >>> # Add custom vars that override everything
        >>> env_vars = get_env_with_dotenv(additional_env={"API_KEY": "override"})
    """
    # Start with .env files (lowest priority)
    merged_env = find_and_merge_dotenv_files(project_root)

    # Merge with system environment variables (higher priority)
    merged_env.update(os.environ)

    # Merge with additional environment variables (highest priority)
    if additional_env:
        merged_env.update(additional_env)

    return merged_env
