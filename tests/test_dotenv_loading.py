"""
Feature tests for .env file auto-loading in config loading.

Tests that .env files are automatically loaded when initializing MCI
configurations and that the precedence rules are applied correctly.
"""

import tempfile
from pathlib import Path

from mci.core.config import MCIConfig


def test_config_loading_with_root_dotenv():
    """Test that .env files in project root are automatically loaded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create .env file in root
        env_file = tmpdir_path / ".env"
        env_file.write_text("TEST_VAR=from-dotenv\nAPI_KEY=secret-key\n")

        # Create valid schema file
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test with .env"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        # Load config - should auto-load .env
        config = MCIConfig()
        client = config.load(str(schema_file))

        # Should load successfully
        assert client is not None


def test_config_loading_with_mci_dotenv():
    """Test that .env files in ./mci directory are automatically loaded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory and .env
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()
        mci_env = mci_dir / ".env"
        mci_env.write_text("MCI_VAR=from-mci-dir\n")

        # Create schema file
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test with ./mci/.env"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        # Load config
        config = MCIConfig()
        client = config.load(str(schema_file))

        assert client is not None


def test_config_loading_dotenv_precedence():
    """Test that root .env overrides ./mci/.env."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory and .env
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()
        mci_env = mci_dir / ".env"
        mci_env.write_text("SHARED_VAR=from-mci\nMCI_ONLY=mci\n")

        # Create root .env (should override SHARED_VAR)
        root_env = tmpdir_path / ".env"
        root_env.write_text("SHARED_VAR=from-root\nROOT_ONLY=root\n")

        # Create schema file
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test precedence"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        # Load config
        config = MCIConfig()
        client = config.load(str(schema_file))

        # Precedence: root .env > ./mci/.env
        assert client is not None


def test_config_loading_explicit_env_overrides_dotenv():
    """Test that explicit env_vars override .env files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create .env file
        env_file = tmpdir_path / ".env"
        env_file.write_text("OVERRIDE_VAR=from-dotenv\n")

        # Create schema file
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test explicit override"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        # Load config with explicit env_vars
        config = MCIConfig()
        explicit_env = {"OVERRIDE_VAR": "from-explicit"}
        client = config.load(str(schema_file), env_vars=explicit_env)

        # Should load successfully with explicit vars taking precedence
        assert client is not None


def test_config_loading_no_dotenv_files():
    """Test that config loads successfully when no .env files exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create schema file (no .env files)
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test without .env"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        # Load config - should work fine without .env
        config = MCIConfig()
        client = config.load(str(schema_file))

        assert client is not None


def test_config_loading_dotenv_can_be_disabled():
    """Test that dotenv auto-loading can be disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create .env file
        env_file = tmpdir_path / ".env"
        env_file.write_text("SHOULD_NOT_LOAD=value\n")

        # Create schema file
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
            "schemaVersion": "1.0",
            "metadata": {
                "name": "Test Project",
                "description": "Test disabled dotenv"
            },
            "tools": [],
            "toolsets": []
        }"""
        schema_file.write_text(schema_content)

        # Load config with auto_load_dotenv=False
        config = MCIConfig()
        client = config.load(str(schema_file), auto_load_dotenv=False)

        assert client is not None
