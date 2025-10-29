"""
Feature tests for the install command.

Tests the full install workflow including file creation, validation,
and integration with other CLI components.
"""

from pathlib import Path

from click.testing import CliRunner

from mci import main
from mci.core.config import MCIConfig
from mci.core.file_finder import MCIFileFinder


def test_install_command_full_workflow_json():
    """Test complete install workflow with JSON format."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Run install command
        result = runner.invoke(main, ["install"])
        assert result.exit_code == 0

        # Verify all files created
        assert Path("mci.json").exists()
        assert Path("mci").is_dir()
        assert Path("mci/.gitignore").exists()
        assert Path("mci/example_toolset.mci.json").exists()

        # Verify main config file can be found
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(".")
        assert found_file is not None
        assert "mci.json" in found_file

        # Verify config can be loaded and validated
        config = MCIConfig()
        is_valid, error = config.validate_schema(found_file)
        assert is_valid is True, f"Validation failed: {error}"

        # Verify MCIClient can load the file
        client = config.load(found_file)
        assert client is not None

        # Verify tools are available
        tools = client.tools()
        assert len(tools) == 1
        assert tools[0].name == "echo_test"

        # Verify .gitignore content
        gitignore_content = Path("mci/.gitignore").read_text()
        assert "mcp/" in gitignore_content


def test_install_command_full_workflow_yaml():
    """Test complete install workflow with YAML format."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Run install command with --yaml flag
        result = runner.invoke(main, ["install", "--yaml"])
        assert result.exit_code == 0

        # Verify YAML file created
        assert Path("mci.yaml").exists()
        assert not Path("mci.json").exists()

        # Verify config file can be found
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(".")
        assert found_file is not None
        assert "mci.yaml" in found_file

        # Verify config can be loaded and validated
        config = MCIConfig()
        is_valid, error = config.validate_schema(found_file)
        assert is_valid is True, f"Validation failed: {error}"

        # Verify MCIClient can load the file
        client = config.load(found_file)
        assert client is not None

        # Verify tools are available
        tools = client.tools()
        assert len(tools) == 1
        assert tools[0].name == "echo_test"


def test_install_command_example_toolset_validation():
    """Test that the example toolset file is valid."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Run install command
        result = runner.invoke(main, ["install"])
        assert result.exit_code == 0

        # Verify example toolset file
        example_file = Path("mci/example_toolset.mci.json")
        assert example_file.exists()

        # Verify it can be loaded and validated
        config = MCIConfig()
        is_valid, error = config.validate_schema(str(example_file))
        assert is_valid is True, f"Example toolset validation failed: {error}"

        # Load the client
        client = config.load(str(example_file))
        assert client is not None

        # Verify tools
        tools = client.tools()
        assert len(tools) == 1
        assert tools[0].name == "list_files"
        assert tools[0].description == "List files in a directory"


def test_install_command_example_toolset_yaml_validation():
    """Test that the YAML example toolset file is valid."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Run install command with --yaml
        result = runner.invoke(main, ["install", "--yaml"])
        assert result.exit_code == 0

        # Verify YAML example toolset file
        example_file = Path("mci/example_toolset.mci.yaml")
        assert example_file.exists()

        # Verify it can be loaded and validated
        config = MCIConfig()
        is_valid, error = config.validate_schema(str(example_file))
        assert is_valid is True, f"Example toolset validation failed: {error}"

        # Load the client
        client = config.load(str(example_file))
        assert client is not None

        # Verify tools
        tools = client.tools()
        assert len(tools) == 1
        assert tools[0].name == "list_files"
        assert tools[0].description == "List files in a directory"


def test_install_command_rerun_idempotent():
    """Test that running install twice doesn't cause errors."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Run install first time
        result1 = runner.invoke(main, ["install"])
        assert result1.exit_code == 0
        assert "Created mci.json" in result1.output

        # Run install second time
        result2 = runner.invoke(main, ["install"])
        assert result2.exit_code == 0
        assert "already exists" in result2.output

        # Verify files still valid
        config = MCIConfig()
        finder = MCIFileFinder()
        found_file = finder.find_mci_file(".")
        assert found_file is not None
        is_valid, _ = config.validate_schema(found_file)
        assert is_valid is True


def test_install_command_directory_structure():
    """Test that install creates the correct directory structure."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(main, ["install"])
        assert result.exit_code == 0

        # Verify directory structure
        cwd = Path.cwd()

        # Root level
        assert (cwd / "mci.json").is_file()

        # mci directory
        mci_dir = cwd / "mci"
        assert mci_dir.is_dir()
        assert (mci_dir / ".gitignore").is_file()
        assert (mci_dir / "example_toolset.mci.json").is_file()

        # Count files to ensure no extra files created
        root_files = list(cwd.glob("*"))
        assert len(root_files) == 2  # mci.json and mci directory

        mci_files = list(mci_dir.glob("*"))
        assert len(mci_files) == 2  # .gitignore and example_toolset.mci.json


def test_install_from_main_cli():
    """Test that install command is properly registered in main CLI."""
    runner = CliRunner()

    # Test help shows install command
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "install" in result.output

    # Test install help works
    result = runner.invoke(main, ["install", "--help"])
    assert result.exit_code == 0
    assert "Initialize an MCI project structure" in result.output
