"""
config.py - Configuration loading and validation for MCI files

This module provides functionality to load and validate MCI configuration files
using the MCIClient from mci-py. It handles schema validation, error handling,
and provides user-friendly error messages. It also automatically loads environment
variables from .env files in the project root and ./mci directory.
"""

from pathlib import Path

from mcipy import MCIClient, MCIClientError

from mci.utils.dotenv import get_env_with_dotenv


class MCIConfig:
    """
    Manages MCI configuration file loading and validation.

    This class provides methods to load MCI configuration files using the
    MCIClient from mci-py, which performs built-in schema validation.
    It also provides utilities for validating schemas and extracting
    user-friendly error messages.

    The class automatically loads environment variables from .env files in:
    - The project root directory (same location as the MCI schema file)
    - The ./mci directory

    Variables are merged with project root taking precedence over ./mci/.env.
    """

    @staticmethod
    def load(
        file_path: str, env_vars: dict[str, str] | None = None, auto_load_dotenv: bool = True
    ) -> MCIClient:
        """
        Load and parse an MCI configuration file using MCIClient.

        This method uses MCIClient from mci-py to load and validate the schema.
        The MCIClient performs comprehensive schema validation during initialization.

        If auto_load_dotenv is True (default), automatically loads environment variables
        from .env and .env.mci files. Priority order:
        - If .env.mci files exist:
          1. ./mci/.env.mci (library MCI-specific)
          2. Project root .env.mci (project MCI-specific)
        - If no .env.mci files exist:
          1. ./mci/.env (library defaults)
          2. Project root .env (project-level)
        - Then:
          3. System environment variables
          4. env_vars argument (highest priority)

        Args:
            file_path: Path to the MCI schema file (.json, .yaml, or .yml)
            env_vars: Optional environment variables for template substitution (highest priority)
            auto_load_dotenv: Whether to automatically load .env files (default: True)

        Returns:
            An initialized MCIClient instance

        Raises:
            MCIClientError: If the schema file cannot be loaded or parsed, or if
                          validation fails

        Example:
            >>> config = MCIConfig()
            >>> try:
            ...     # Auto-loads .env files from project root and ./mci
            ...     client = config.load("mci.json")
            ...     tools = client.tools()
            ... except MCIClientError as e:
            ...     print(f"Schema invalid: {e}")
        """
        try:
            # Determine project root from schema file location
            project_root = Path(file_path).parent.resolve()

            # Load environment variables with proper precedence
            if auto_load_dotenv:
                merged_env = get_env_with_dotenv(project_root, env_vars)
            else:
                # If auto-loading is disabled, just use provided env_vars
                merged_env = env_vars or {}

            client = MCIClient(schema_file_path=file_path, env_vars=merged_env)
            return client
        except MCIClientError:
            # Re-raise with the original error message from mci-py
            raise

    @staticmethod
    def validate_schema(
        file_path: str, env_vars: dict[str, str] | None = None, auto_load_dotenv: bool = True
    ) -> tuple[bool, str]:
        """
        Validate an MCI schema file using MCIClient.

        This method validates the schema using MCIClient in validation-only mode,
        which skips template resolution for MCP servers and other runtime concerns.
        MCIClient performs comprehensive validation including schema structure,
        required fields, and data types.

        If auto_load_dotenv is True (default), automatically loads environment variables
        from .env files in the project root and ./mci directory.

        Args:
            file_path: Path to the MCI schema file to validate
            env_vars: Optional environment variables for template substitution
            auto_load_dotenv: Whether to automatically load .env files (default: True)

        Returns:
            A tuple of (is_valid, error_message) where:
            - is_valid is True if the schema is valid, False otherwise
            - error_message is empty string if valid, or contains error details if invalid

        Example:
            >>> config = MCIConfig()
            >>> is_valid, error = config.validate_schema("mci.json")
            >>> if not is_valid:
            ...     print(f"Validation failed: {error}")
        """
        try:
            # Determine project root from schema file location
            project_root = Path(file_path).parent.resolve()

            # Load environment variables with proper precedence
            if auto_load_dotenv:
                merged_env = get_env_with_dotenv(project_root, env_vars)
            else:
                # If auto-loading is disabled, just use provided env_vars
                merged_env = env_vars or {}

            # Use validating=True to skip template resolution for MCP servers
            # This allows validation without requiring all env_vars at validation time
            MCIClient(schema_file_path=file_path, env_vars=merged_env, validating=True)
            return (True, "")
        except MCIClientError as e:
            return (False, str(e))
        except FileNotFoundError:
            return (False, f"File not found: {file_path}")
        except Exception as e:
            return (False, f"Unexpected error: {str(e)}")
