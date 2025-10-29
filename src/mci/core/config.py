"""
config.py - Configuration loading and validation for MCI files

This module provides functionality to load and validate MCI configuration files
using the MCIClient from mci-py. It handles schema validation, error handling,
and provides user-friendly error messages.
"""

from mcipy import MCIClient, MCIClientError


class MCIConfig:
    """
    Manages MCI configuration file loading and validation.

    This class provides methods to load MCI configuration files using the
    MCIClient from mci-py, which performs built-in schema validation.
    It also provides utilities for validating schemas and extracting
    user-friendly error messages.
    """

    @staticmethod
    def load(file_path: str, env_vars: dict[str, str] | None = None) -> MCIClient:
        """
        Load and parse an MCI configuration file using MCIClient.

        This method uses MCIClient from mci-py to load and validate the schema.
        The MCIClient performs comprehensive schema validation during initialization.

        Args:
            file_path: Path to the MCI schema file (.json, .yaml, or .yml)
            env_vars: Optional environment variables for template substitution

        Returns:
            An initialized MCIClient instance

        Raises:
            MCIClientError: If the schema file cannot be loaded or parsed, or if
                          validation fails

        Example:
            >>> config = MCIConfig()
            >>> try:
            ...     client = config.load("mci.json")
            ...     tools = client.tools()
            ... except MCIClientError as e:
            ...     print(f"Schema invalid: {e}")
        """
        try:
            client = MCIClient(schema_file_path=file_path, env_vars=env_vars or {})
            return client
        except MCIClientError:
            # Re-raise with the original error message from mci-py
            raise

    @staticmethod
    def validate_schema(file_path: str, env_vars: dict[str, str] | None = None) -> tuple[bool, str]:
        """
        Validate an MCI schema file using MCIClient.

        This method attempts to load the schema using MCIClient and returns
        validation results. MCIClient performs comprehensive validation including
        schema structure, required fields, and data types.

        Args:
            file_path: Path to the MCI schema file to validate
            env_vars: Optional environment variables for template substitution

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
            MCIConfig.load(file_path, env_vars)
            return (True, "")
        except MCIClientError as e:
            return (False, str(e))
        except FileNotFoundError:
            return (False, f"File not found: {file_path}")
        except Exception as e:
            return (False, f"Unexpected error: {str(e)}")
