"""
Manual test for the list command - Visual verification.

This script creates a test MCI schema and runs the list command
with various options to manually verify the output formatting.

Run this script with:
    uv run python testsManual/test_list_output.py
"""

import json
import subprocess
import tempfile
from pathlib import Path


def create_test_schema():
    """Create a comprehensive test schema for manual testing."""
    schema = {
        "schemaVersion": "1.0",
        "metadata": {
            "name": "Manual Test Project",
            "description": "Schema for manual testing of list command output",
        },
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "tags": ["api", "data", "weather", "read"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City or location name",
                        },
                        "units": {
                            "type": "string",
                            "description": "Temperature units (celsius or fahrenheit)",
                        },
                    },
                    "required": ["location"],
                },
                "execution": {"type": "text", "text": "Weather data for {{props.location}}"},
            },
            {
                "name": "get_forecast",
                "description": "Get weather forecast for upcoming days",
                "tags": ["api", "data", "weather", "read"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "days": {"type": "number"},
                    },
                    "required": ["location"],
                },
                "execution": {"type": "text", "text": "Forecast for {{props.location}}"},
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyze text sentiment using ML models",
                "tags": ["data", "ml", "text", "analyze"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"},
                        "model": {"type": "string", "description": "ML model to use"},
                    },
                    "required": ["text"],
                },
                "execution": {"type": "text", "text": "Sentiment: {{result}}"},
            },
            {
                "name": "summarize_data",
                "description": "Summarize large datasets into key insights",
                "tags": ["data", "analyze"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset": {"type": "string"},
                        "max_length": {"type": "number"},
                    },
                    "required": ["dataset"],
                },
                "execution": {"type": "text", "text": "Summary of {{props.dataset}}"},
            },
            {
                "name": "send_notification",
                "description": "Send notifications to users",
                "tags": ["api", "write", "notify"],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "message": {"type": "string"},
                        "priority": {"type": "string"},
                    },
                    "required": ["user_id", "message"],
                },
                "execution": {"type": "text", "text": "Notification sent to {{props.user_id}}"},
            },
        ],
    }

    return schema


def run_command(cmd: list[str], description: str):
    """Run a command and display the output."""
    print("\n" + "=" * 80)
    print(f"TEST: {description}")
    print("=" * 80)
    print(f"Command: {' '.join(cmd)}")
    print("-" * 80)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print("✓ Command succeeded")
    else:
        print("✗ Command failed with exit code:", result.returncode)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

    return result.returncode


def main():
    """Run manual tests for the list command."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "MCI LIST COMMAND - MANUAL TEST" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")

    # Create test schema
    schema = create_test_schema()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mci.json", delete=False, dir="."
    ) as f:
        json.dump(schema, f)
        schema_path = f.name

    try:
        # Test 1: Basic table output
        run_command(
            ["uv", "run", "mci", "list", "--file", schema_path],
            "Basic table output (default)",
        )

        # Test 2: Verbose table output
        run_command(
            ["uv", "run", "mci", "list", "--file", schema_path, "--verbose"],
            "Verbose table output with tags and parameters",
        )

        # Test 3: Filter by tags (weather)
        run_command(
            ["uv", "run", "mci", "list", "--file", schema_path, "--filter", "tags:weather"],
            "Filter by tags: weather",
        )

        # Test 4: Filter by tags (ml)
        run_command(
            ["uv", "run", "mci", "list", "--file", schema_path, "--filter", "tags:ml,analyze"],
            "Filter by tags: ml OR analyze",
        )

        # Test 5: Filter with only
        run_command(
            [
                "uv",
                "run",
                "mci",
                "list",
                "--file",
                schema_path,
                "--filter",
                "only:get_weather,send_notification",
            ],
            "Filter with only: specific tools",
        )

        # Test 6: Filter with except
        run_command(
            [
                "uv",
                "run",
                "mci",
                "list",
                "--file",
                schema_path,
                "--filter",
                "except:send_notification",
            ],
            "Filter with except: exclude tools",
        )

        # Test 7: JSON output
        result = run_command(
            ["uv", "run", "mci", "list", "--file", schema_path, "--format", "json"],
            "JSON file output",
        )

        if result == 0:
            # Show JSON file content
            json_files = list(Path(".").glob("tools_*.json"))
            if json_files:
                print("\n--- JSON File Content (first 500 chars) ---")
                with open(json_files[0]) as f:
                    content = f.read()
                    print(content[:500])
                    if len(content) > 500:
                        print("... (truncated)")
                # Clean up JSON file
                json_files[0].unlink()

        # Test 8: YAML output with verbose
        result = run_command(
            [
                "uv",
                "run",
                "mci",
                "list",
                "--file",
                schema_path,
                "--format",
                "yaml",
                "--verbose",
            ],
            "YAML file output with verbose mode",
        )

        if result == 0:
            # Show YAML file content
            yaml_files = list(Path(".").glob("tools_*.yaml"))
            if yaml_files:
                print("\n--- YAML File Content (first 500 chars) ---")
                with open(yaml_files[0]) as f:
                    content = f.read()
                    print(content[:500])
                    if len(content) > 500:
                        print("... (truncated)")
                # Clean up YAML file
                yaml_files[0].unlink()

        # Test 9: JSON output with filter
        result = run_command(
            [
                "uv",
                "run",
                "mci",
                "list",
                "--file",
                schema_path,
                "--format",
                "json",
                "--filter",
                "tags:api",
            ],
            "JSON output with tag filter",
        )

        if result == 0:
            # Show filtered JSON
            json_files = list(Path(".").glob("tools_*.json"))
            if json_files:
                print("\n--- Filtered JSON Content ---")
                with open(json_files[0]) as f:
                    data = json.load(f)
                    print(f"Total tools: {data['total']}")
                    print(f"Filters applied: {data['filters_applied']}")
                    print(f"Tool names: {[t['name'] for t in data['tools']]}")
                # Clean up JSON file
                json_files[0].unlink()

        print("\n" + "=" * 80)
        print("Manual testing complete!")
        print("Please review the output above to verify:")
        print("  ✓ Table formatting is clear and readable")
        print("  ✓ Verbose mode shows tags and parameters correctly")
        print("  ✓ Filters work as expected")
        print("  ✓ JSON/YAML files are created with correct structure")
        print("  ✓ Rich formatting (colors, styling) looks good")
        print("=" * 80)

    finally:
        # Clean up test schema file
        Path(schema_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
