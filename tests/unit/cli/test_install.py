"""
Unit tests for the install CLI command.

Tests the installation functionality including file creation, directory
setup, and handling of existing files.
"""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from mci.cli.install import (
    copy_asset,
    create_example_toolset,
    create_mci_directory,
    create_mci_file,
    install,
)


def test_copy_asset_success():
    """Test copying an asset file to a destination."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = Path(tmpdir) / "mci.json"
        result = copy_asset("mci.json", dest_path)

        assert result is True
        assert dest_path.exists()
        # Verify content is not empty
        content = dest_path.read_text()
        assert len(content) > 0
        assert "schemaVersion" in content


def test_copy_asset_existing_file_no_overwrite():
    """Test that copy_asset doesn't overwrite existing files by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = Path(tmpdir) / "mci.json"
        dest_path.write_text("existing content")

        result = copy_asset("mci.json", dest_path, overwrite=False)

        assert result is False
        assert dest_path.read_text() == "existing content"


def test_copy_asset_existing_file_with_overwrite():
    """Test that copy_asset overwrites when overwrite=True."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = Path(tmpdir) / "mci.json"
        dest_path.write_text("existing content")

        result = copy_asset("mci.json", dest_path, overwrite=True)

        assert result is True
        content = dest_path.read_text()
        assert content != "existing content"
        assert "schemaVersion" in content


def test_create_mci_file_json(monkeypatch):
    """Test creating mci.json file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        monkeypatch.chdir(tmpdir)

        create_mci_file(format="json")

        mci_file = Path(tmpdir) / "mci.json"
        assert mci_file.exists()

        content = mci_file.read_text()
        assert "schemaVersion" in content
        assert "Example Project" in content
        assert "echo_test" in content


def test_create_mci_file_yaml(monkeypatch):
    """Test creating mci.yaml file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        monkeypatch.chdir(tmpdir)

        create_mci_file(format="yaml")

        mci_file = Path(tmpdir) / "mci.yaml"
        assert mci_file.exists()

        content = mci_file.read_text()
        assert "schemaVersion" in content
        assert "Example Project" in content
        assert "echo_test" in content


def test_create_mci_file_already_exists(monkeypatch, capsys):
    """Test that create_mci_file handles existing files gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Create the file first
        mci_file = Path(tmpdir) / "mci.json"
        mci_file.write_text("existing content")

        create_mci_file(format="json")

        # File should not be overwritten
        assert mci_file.read_text() == "existing content"

        # Should print a warning message
        captured = capsys.readouterr()
        assert "already exists" in captured.out


def test_create_mci_directory(monkeypatch):
    """Test creating ./mci directory and .gitignore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        create_mci_directory()

        mci_dir = Path(tmpdir) / "mci"
        assert mci_dir.exists()
        assert mci_dir.is_dir()

        gitignore = mci_dir / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "mcp/" in content


def test_create_mci_directory_updates_existing_gitignore(monkeypatch):
    """Test that create_mci_directory updates existing .gitignore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Create directory and .gitignore without mcp/ entry
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()
        gitignore = mci_dir / ".gitignore"
        gitignore.write_text("# Existing content\nnode_modules/\n")

        create_mci_directory()

        content = gitignore.read_text()
        assert "# Existing content" in content
        assert "node_modules/" in content
        assert "mcp/" in content


def test_create_mci_directory_skips_if_mcp_exists(monkeypatch, capsys):
    """Test that create_mci_directory skips if mcp/ already in .gitignore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Create directory and .gitignore with mcp/ entry
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()
        gitignore = mci_dir / ".gitignore"
        gitignore.write_text("mcp/\n")

        create_mci_directory()

        # Should not add duplicate entry
        content = gitignore.read_text()
        assert content.count("mcp/") == 1

        # Should print a message
        captured = capsys.readouterr()
        assert "already contains mcp/" in captured.out


def test_create_example_toolset(monkeypatch):
    """Test creating example_toolset.mci.json file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Create mci directory first
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()

        create_example_toolset()

        toolset_file = mci_dir / "example_toolset.mci.json"
        assert toolset_file.exists()

        content = toolset_file.read_text()
        assert "schemaVersion" in content
        assert "list_files" in content
        assert "ls" in content


def test_create_example_toolset_already_exists(monkeypatch, capsys):
    """Test that create_example_toolset handles existing files gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Create mci directory and file
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()
        toolset_file = mci_dir / "example_toolset.mci.json"
        toolset_file.write_text("existing content")

        create_example_toolset()

        # File should not be overwritten
        assert toolset_file.read_text() == "existing content"

        # Should print a warning message
        captured = capsys.readouterr()
        assert "already exists" in captured.out


def test_create_example_toolset_yaml(monkeypatch):
    """Test creating example_toolset.mci.yaml file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Create mci directory first
        mci_dir = Path(tmpdir) / "mci"
        mci_dir.mkdir()

        create_example_toolset(format="yaml")

        toolset_file = mci_dir / "example_toolset.mci.yaml"
        assert toolset_file.exists()

        content = toolset_file.read_text()
        assert "schemaVersion" in content
        assert "list_files" in content
        assert "ls" in content


def test_install_command_json():
    """Test the install command with JSON format (default)."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(install)

        assert result.exit_code == 0
        assert "Initializing MCI project" in result.output
        assert "Created mci.json" in result.output
        assert "Created ./mci/ directory" in result.output
        assert "Created ./mci/.gitignore" in result.output
        assert "Created ./mci/example_toolset.mci.json" in result.output

        # Verify files exist
        assert Path("mci.json").exists()
        assert Path("mci").exists()
        assert Path("mci/.gitignore").exists()
        assert Path("mci/example_toolset.mci.json").exists()


def test_install_command_yaml():
    """Test the install command with --yaml flag."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(install, ["--yaml"])

        assert result.exit_code == 0
        assert "Created mci.yaml" in result.output
        assert "Created ./mci/example_toolset.mci.yaml" in result.output

        # Verify YAML file exists
        assert Path("mci.yaml").exists()
        assert not Path("mci.json").exists()

        # Verify YAML example toolset exists
        assert Path("mci/example_toolset.mci.yaml").exists()
        assert not Path("mci/example_toolset.mci.json").exists()


def test_install_command_existing_files():
    """Test the install command with existing files."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create files first
        Path("mci.json").write_text("existing")
        Path("mci").mkdir()
        Path("mci/.gitignore").write_text("mcp/\n")
        Path("mci/example_toolset.mci.json").write_text("existing")

        result = runner.invoke(install)

        assert result.exit_code == 0
        assert "already exists" in result.output
        assert "already contains mcp/" in result.output

        # Verify files weren't overwritten
        assert Path("mci.json").read_text() == "existing"
        assert Path("mci/example_toolset.mci.json").read_text() == "existing"


def test_install_command_help():
    """Test that the install command has proper help text."""
    runner = CliRunner()
    result = runner.invoke(install, ["--help"])

    assert result.exit_code == 0
    assert "Initialize an MCI project structure" in result.output
    assert "--yaml" in result.output
