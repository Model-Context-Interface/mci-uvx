"""
env_scanner.py - Environment variable scanning utilities

This module provides utilities to scan MCI schemas and extract all
referenced environment variables from template placeholders.
"""

import re
from typing import Any


class EnvScanner:
    """
    Scans MCI schemas to find all environment variable references.

    Environment variables can appear in templates as {{env.VARIABLE_NAME}}.
    This scanner recursively searches through dictionaries, lists, and strings
    to find all such references.
    """

    # Regex pattern to match {{env.VARIABLE_NAME}}
    ENV_PATTERN: re.Pattern[str] = re.compile(r"\{\{env\.([A-Za-z_][A-Za-z0-9_]*)\}\}")

    @staticmethod
    def scan_value(value: Any) -> set[str]:
        """
        Scan a single value for environment variable references.

        Args:
            value: Value to scan (can be str, dict, list, or other types)

        Returns:
            Set of environment variable names found

        Example:
            >>> EnvScanner.scan_value("{{env.API_KEY}}")
            {'API_KEY'}
            >>> EnvScanner.scan_value("Hello {{env.USER}}, your key is {{env.API_KEY}}")
            {'USER', 'API_KEY'}
        """
        env_vars: set[str] = set()

        if isinstance(value, str):
            # Extract all env variable names from the string
            matches = EnvScanner.ENV_PATTERN.findall(value)
            env_vars.update(matches)

        elif isinstance(value, dict):
            # Recursively scan all values in the dictionary
            for v in value.values():
                env_vars.update(EnvScanner.scan_value(v))

        elif isinstance(value, list):
            # Recursively scan all items in the list
            for item in value:
                env_vars.update(EnvScanner.scan_value(item))

        return env_vars

    @staticmethod
    def scan_dict(data: dict[str, Any]) -> set[str]:
        """
        Scan a dictionary for environment variable references.

        This is a convenience wrapper around scan_value() for dictionaries.

        Args:
            data: Dictionary to scan

        Returns:
            Set of environment variable names found

        Example:
            >>> schema = {
            ...     "execution": {
            ...         "type": "http",
            ...         "url": "{{env.BASE_URL}}/api",
            ...         "headers": {"Authorization": "Bearer {{env.API_KEY}}"}
            ...     }
            ... }
            >>> EnvScanner.scan_dict(schema)
            {'BASE_URL', 'API_KEY'}
        """
        return EnvScanner.scan_value(data)
