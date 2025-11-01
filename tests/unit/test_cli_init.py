"""
Unit tests for CLI initialization.

Tests that the CLI can be initialized and basic Click functionality works.
"""

from click.testing import CliRunner

from mci.mci import main


def test_cli_main_exists():
    """Test that the main CLI function exists."""
    assert callable(main)


def test_cli_help():
    """Test that the CLI help command works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "MCI CLI" in result.output
    assert "Manage Model Context Interface schemas" in result.output


def test_cli_no_args():
    """Test that running CLI with no arguments shows usage."""
    runner = CliRunner()
    result = runner.invoke(main, [])
    # Click groups return exit code 2 when invoked without arguments
    # This is expected behavior
    assert "Usage:" in result.output
