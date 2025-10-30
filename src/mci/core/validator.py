"""
validator.py - Schema validation logic using mci-py

This module provides validation functionality for MCI schemas,
leveraging mci-py's built-in MCIClient validation and adding
additional checks for toolset files and MCP command availability.
"""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import yaml

from mci.core.config import MCIConfig
from mci.utils.error_formatter import ValidationError, ValidationWarning


@dataclass
class ValidationResult:
    """
    Result of validating an MCI schema.

    Attributes:
        errors: List of validation errors from MCIClient
        warnings: List of validation warnings from additional checks
        is_valid: True if no errors were found (warnings are OK)
    """

    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    is_valid: bool


class MCIValidator:
    """
    Validates MCI schemas using MCIClient and performs additional checks.

    This class uses mci-py's built-in validation via MCIClient and adds
    extra validation for toolset file existence and MCP command availability.
    """

    def __init__(self, file_path: str, env_vars: dict[str, str] | None = None):
        """
        Initialize the validator.

        Args:
            file_path: Path to the MCI schema file to validate
            env_vars: Optional environment variables for template substitution
        """
        self.file_path: str = file_path
        self.env_vars: dict[str, str] = env_vars or {}
        self.schema_data: dict[str, object] | None = None

    def validate_schema(self) -> ValidationResult:
        """
        Validate the MCI schema file using MCIClient.

        This method uses MCIConfig.validate_schema which wraps MCIClient
        validation. It then performs additional checks for toolset files
        and MCP commands.

        Returns:
            ValidationResult with errors, warnings, and validity status

        Example:
            >>> validator = MCIValidator("mci.json")
            >>> result = validator.validate_schema()
            >>> if not result.is_valid:
            ...     print("Schema has errors!")
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # First, validate using MCIClient (primary validation)
        config = MCIConfig()
        is_valid, error_message = config.validate_schema(self.file_path, self.env_vars)

        if not is_valid:
            # Parse the error message from MCIClient
            errors.append(ValidationError(message=error_message))
            # If schema is invalid, we can't perform additional checks
            return ValidationResult(errors=errors, warnings=warnings, is_valid=False)

        # Load schema data for additional checks
        try:
            self._load_schema_data()
        except Exception as e:
            errors.append(ValidationError(message=f"Failed to load schema data: {str(e)}"))
            return ValidationResult(errors=errors, warnings=warnings, is_valid=False)

        # Perform additional checks (as warnings)
        toolset_warnings = self.check_toolset_files()
        warnings.extend(toolset_warnings)

        mcp_warnings = self.check_mcp_commands()
        warnings.extend(mcp_warnings)

        return ValidationResult(errors=errors, warnings=warnings, is_valid=True)

    def _load_schema_data(self) -> None:
        """
        Load the raw schema data from the file.

        This is used for additional validation checks beyond what MCIClient provides.

        Raises:
            Exception: If the file cannot be loaded or parsed
        """
        file_path = Path(self.file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.file_path}")

        with open(file_path) as f:
            if file_path.suffix == ".json":
                self.schema_data = json.load(f)
            elif file_path.suffix in [".yaml", ".yml"]:
                self.schema_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def check_toolset_files(self) -> list[ValidationWarning]:
        """
        Check that referenced toolset files exist.

        Returns:
            List of ValidationWarning for missing toolset files

        Example:
            >>> validator = MCIValidator("mci.json")
            >>> validator._load_schema_data()
            >>> warnings = validator.check_toolset_files()
        """
        warnings: list[ValidationWarning] = []

        if not self.schema_data:
            return warnings

        toolsets = self.schema_data.get("toolsets", [])
        if not toolsets:
            return warnings

        schema_dir = Path(self.file_path).parent
        mci_dir = schema_dir / "mci"

        # Type narrowing: toolsets should be a list
        if not isinstance(toolsets, list):
            return warnings

        for toolset in toolsets:
            if isinstance(toolset, str):
                # Toolset is a string reference (e.g., "weather")
                # Should correspond to mci/weather.mci.json or mci/weather.mci.yaml
                toolset_json = mci_dir / f"{toolset}.mci.json"
                toolset_yaml = mci_dir / f"{toolset}.mci.yaml"

                if not toolset_json.exists() and not toolset_yaml.exists():
                    warnings.append(
                        ValidationWarning(
                            message=f"Toolset file not found: {toolset}",
                            suggestion=f"Create {toolset_json} or {toolset_yaml}, or update the toolset reference",
                        )
                    )

        return warnings

    def check_mcp_commands(self) -> list[ValidationWarning]:
        """
        Check that MCP server commands are available in PATH.

        Returns:
            List of ValidationWarning for missing MCP commands

        Example:
            >>> validator = MCIValidator("mci.json")
            >>> validator._load_schema_data()
            >>> warnings = validator.check_mcp_commands()
        """
        warnings: list[ValidationWarning] = []

        if not self.schema_data:
            return warnings

        mcp_servers = self.schema_data.get("mcp_servers", {})
        if not mcp_servers:
            return warnings

        # Type narrowing: mcp_servers should be a dict
        if not isinstance(mcp_servers, dict):
            return warnings

        for server_name, server_config in mcp_servers.items():
            if isinstance(server_config, dict):
                command = server_config.get("command")
                if command:
                    # Check if command is available in PATH
                    if not shutil.which(command):
                        warnings.append(
                            ValidationWarning(
                                message=f"MCP server command not found in PATH: {command} (server: {server_name})",
                                suggestion="Install the command or ensure it's in your PATH",
                            )
                        )

        return warnings
