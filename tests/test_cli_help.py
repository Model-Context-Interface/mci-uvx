"""
Feature tests for CLI help and command discovery.

Tests that the CLI help system works correctly and commands can be discovered.
"""

from click.testing import CliRunner

from mci import main


def test_cli_help_output():
    """Test that the CLI help output is properly formatted."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "MCI CLI" in result.output
    assert "Options:" in result.output
    assert "--help" in result.output
    assert "--version" in result.output


def test_cli_help_flag_variations():
    """Test that the --help flag works (Click doesn't support -h by default)."""
    runner = CliRunner()

    # Test --help
    result_help = runner.invoke(main, ["--help"])
    assert result_help.exit_code == 0
    assert len(result_help.output) > 0


def test_cli_command_group():
    """Test that the CLI is a Click command group."""
    # The main function should be a Click group
    assert hasattr(main, "commands")


def test_cli_invalid_command():
    """Test that invalid commands are handled properly."""
    runner = CliRunner()
    result = runner.invoke(main, ["nonexistent-command"])

    # Should exit with error
    assert result.exit_code != 0
    # Should show error message
    assert "Error" in result.output or "No such command" in result.output
