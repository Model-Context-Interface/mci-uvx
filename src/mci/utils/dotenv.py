"""
dotenv.py - Environment variable file parsing utilities

This module provides functionality to parse .env files in standard dotenv format
and merge environment variables from multiple sources. It supports:
- KEY=VALUE format
- Comments starting with #
- Blank lines
- Export keyword (which is ignored)
- Basic quoted values

The module is used to automatically load .env files from the project root
and ./mci directory when initializing MCI configurations.
"""

import os
import re
from pathlib import Path


def parse_dotenv_file(file_path: str | Path) -> dict[str, str]:
    """
    Parse a .env file and return a dictionary of environment variables.

    This function parses .env files in standard dotenv format:
    - KEY=VALUE format
    - Lines starting with # are comments (ignored)
    - Blank lines are ignored
    - Export keyword is ignored (e.g., "export KEY=VALUE" is treated as "KEY=VALUE")
    - Values can be quoted with single or double quotes
    - Basic variable expansion is NOT supported (for security)

    Args:
        file_path: Path to the .env file to parse

    Returns:
        Dictionary of environment variable key-value pairs

    Example:
        >>> env_vars = parse_dotenv_file(".env")
        >>> print(env_vars.get("API_KEY"))
        'my-secret-key'
    """
    env_vars: dict[str, str] = {}
    file_path = Path(file_path)

    if not file_path.exists():
        return env_vars

    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                # Strip whitespace
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Remove 'export ' prefix if present
                if line.startswith("export "):
                    line = line[7:].strip()

                # Parse KEY=VALUE format
                match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
                if match:
                    key = match.group(1)
                    value = match.group(2)

                    # Remove quotes if present (simple handling)
                    if len(value) >= 2:
                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]

                    env_vars[key] = value
                # If line doesn't match format, silently skip it
                # (could be malformed or a directive we don't support)

    except Exception:
        # If we can't read the file, return empty dict (silent failure)
        # This maintains the "no error if .env is missing" requirement
        pass

    return env_vars


def find_and_merge_dotenv_files(project_root: str | Path | None = None) -> dict[str, str]:
    """
    Find and merge .env files from project root and ./mci directory.

    This function looks for .env files in two locations:
    1. {project_root}/.env
    2. {project_root}/mci/.env

    If both files exist, variables are merged with project root taking precedence
    (root .env overrides ./mci/.env for duplicate keys).

    Args:
        project_root: Path to the project root directory. If None, uses current directory.

    Returns:
        Dictionary of merged environment variables

    Example:
        >>> env_vars = find_and_merge_dotenv_files()
        >>> # Variables from root .env override ./mci/.env
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    merged_env: dict[str, str] = {}

    # First, load from ./mci/.env (lower priority)
    mci_env_path = project_root / "mci" / ".env"
    if mci_env_path.exists():
        mci_env_vars = parse_dotenv_file(mci_env_path)
        merged_env.update(mci_env_vars)

    # Then, load from project root .env (higher priority, overrides ./mci/.env)
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
    1. ./mci/.env
    2. {project_root}/.env
    3. System environment variables (os.environ)
    4. Additional environment variables passed as argument

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
