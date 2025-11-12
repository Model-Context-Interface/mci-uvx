"""
env_formatter.py - Environment variable file formatter

This module provides formatting for environment variable output in .env file format.
"""

from pathlib import Path


class EnvFormatter:
    """
    Formats environment variable information as .env files.

    This formatter generates .env.example.mci files containing all detected
    environment variables with empty values, suitable for use as templates.
    """

    @staticmethod
    def format_to_string(env_vars: dict[str, list[str]]) -> str:
        """
        Format environment variables as a string in .env format.

        Args:
            env_vars: Dictionary mapping variable names to list of locations where used

        Returns:
            Formatted string in .env format

        Example:
            >>> env_vars = {"API_KEY": ["main"], "DB_URL": ["database-toolset"]}
            >>> print(EnvFormatter.format_to_string(env_vars))
            # .env.example.mci
            ...
        """
        # Sort variables alphabetically
        sorted_vars = sorted(env_vars.keys())

        # Generate content
        lines: list[str] = []
        lines.append("# .env.example.mci")
        lines.append("# Environment variables used in MCI configuration")
        lines.append("#")
        lines.append("# Copy this file to .env.mci and fill in your values")
        lines.append("")

        for var_name in sorted_vars:
            locations = env_vars[var_name]
            # Add comment showing where the variable is used
            location_str = ", ".join(sorted(locations))
            lines.append(f"# Used in: {location_str}")
            lines.append(f"{var_name}=")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def format_to_file(env_vars: dict[str, list[str]], output_path: str | None = None) -> str:
        """
        Format environment variables and write to .env.example.mci file.

        Args:
            env_vars: Dictionary mapping variable names to list of locations where used
            output_path: Optional custom output path (default: .env.example.mci)

        Returns:
            Path to the generated file

        Example:
            >>> env_vars = {
            ...     "API_KEY": ["main", "weather-toolset"],
            ...     "DB_URL": ["database-toolset"]
            ... }
            >>> path = EnvFormatter.format_to_file(env_vars)
            >>> print(path)
            .env.example.mci
        """
        if output_path is None:
            output_path = ".env.example.mci"

        content = EnvFormatter.format_to_string(env_vars)
        Path(output_path).write_text(content)

        return output_path
