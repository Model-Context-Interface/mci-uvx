"""
Unit tests for dotenv parsing utilities.

Tests the .env file parsing, discovery, and merging functionality.
"""

import tempfile
from pathlib import Path

from mci.utils.dotenv import (
    find_and_merge_dotenv_files,
    get_env_with_dotenv,
    parse_dotenv_file,
)


def test_parse_dotenv_file_basic():
    """Test parsing a basic .env file with KEY=VALUE format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("API_KEY=test-key-123\nBASE_URL=https://api.example.com\n")

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {
            "API_KEY": "test-key-123",
            "BASE_URL": "https://api.example.com",
        }


def test_parse_dotenv_file_with_comments():
    """Test parsing .env file with comments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_content = """# This is a comment
API_KEY=test-key-123
# Another comment
BASE_URL=https://api.example.com
"""
        env_file.write_text(env_content)

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {
            "API_KEY": "test-key-123",
            "BASE_URL": "https://api.example.com",
        }


def test_parse_dotenv_file_with_blank_lines():
    """Test parsing .env file with blank lines."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_content = """API_KEY=test-key-123

BASE_URL=https://api.example.com

"""
        env_file.write_text(env_content)

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {
            "API_KEY": "test-key-123",
            "BASE_URL": "https://api.example.com",
        }


def test_parse_dotenv_file_with_export():
    """Test parsing .env file with export keyword."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_content = """export API_KEY=test-key-123
export BASE_URL=https://api.example.com
NORMAL_VAR=value
"""
        env_file.write_text(env_content)

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {
            "API_KEY": "test-key-123",
            "BASE_URL": "https://api.example.com",
            "NORMAL_VAR": "value",
        }


def test_parse_dotenv_file_with_quotes():
    """Test parsing .env file with quoted values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_content = """API_KEY="test-key-123"
BASE_URL='https://api.example.com'
MESSAGE="Hello World"
SINGLE='Single quotes'
"""
        env_file.write_text(env_content)

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {
            "API_KEY": "test-key-123",
            "BASE_URL": "https://api.example.com",
            "MESSAGE": "Hello World",
            "SINGLE": "Single quotes",
        }


def test_parse_dotenv_file_with_spaces():
    """Test parsing .env file with spaces around equals sign."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_content = """API_KEY = test-key-123
BASE_URL=https://api.example.com
SPACED = value with spaces
"""
        env_file.write_text(env_content)

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {
            "API_KEY": "test-key-123",
            "BASE_URL": "https://api.example.com",
            "SPACED": "value with spaces",
        }


def test_parse_dotenv_file_empty():
    """Test parsing empty .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("")

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {}


def test_parse_dotenv_file_nonexistent():
    """Test parsing nonexistent .env file returns empty dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / "nonexistent.env"

        env_vars = parse_dotenv_file(env_file)

        assert env_vars == {}


def test_parse_dotenv_file_with_malformed_lines():
    """Test parsing .env file with malformed lines (should skip them)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_content = """API_KEY=test-key-123
INVALID LINE WITHOUT EQUALS
=VALUE_WITHOUT_KEY
BASE_URL=https://api.example.com
"""
        env_file.write_text(env_content)

        env_vars = parse_dotenv_file(env_file)

        # Should only parse valid lines
        assert env_vars == {
            "API_KEY": "test-key-123",
            "BASE_URL": "https://api.example.com",
        }


def test_find_and_merge_dotenv_files_both_exist():
    """Test merging .env files when both root and mci/.env exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # Create ./mci/.env
        mci_env = mci_dir / ".env"
        mci_env.write_text("API_KEY=mci-key\nMCI_VAR=mci-value\n")

        # Create root .env (should override API_KEY)
        root_env = tmpdir_path / ".env"
        root_env.write_text("API_KEY=root-key\nROOT_VAR=root-value\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        # Root .env should override ./mci/.env for API_KEY
        assert env_vars == {
            "API_KEY": "root-key",  # Overridden by root
            "MCI_VAR": "mci-value",  # From mci/.env
            "ROOT_VAR": "root-value",  # From root .env
        }


def test_find_and_merge_dotenv_files_only_root():
    """Test loading .env when only root .env exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create root .env only
        root_env = tmpdir_path / ".env"
        root_env.write_text("API_KEY=root-key\nROOT_VAR=root-value\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        assert env_vars == {
            "API_KEY": "root-key",
            "ROOT_VAR": "root-value",
        }


def test_find_and_merge_dotenv_files_only_mci():
    """Test loading .env when only mci/.env exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # Create ./mci/.env only
        mci_env = mci_dir / ".env"
        mci_env.write_text("API_KEY=mci-key\nMCI_VAR=mci-value\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        assert env_vars == {
            "API_KEY": "mci-key",
            "MCI_VAR": "mci-value",
        }


def test_find_and_merge_dotenv_files_neither_exist():
    """Test loading .env when neither root nor mci/.env exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        assert env_vars == {}


def test_find_and_merge_dotenv_files_default_cwd():
    """Test finding .env files using current directory by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create root .env
        root_env = tmpdir_path / ".env"
        root_env.write_text("CWD_VAR=cwd-value\n")

        # Change to temp directory and test
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir_path)
            env_vars = find_and_merge_dotenv_files()
            assert "CWD_VAR" in env_vars
            assert env_vars["CWD_VAR"] == "cwd-value"
        finally:
            os.chdir(original_cwd)


def test_get_env_with_dotenv_basic():
    """Test getting environment with .env files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create root .env
        root_env = tmpdir_path / ".env"
        root_env.write_text("DOTENV_VAR=dotenv-value\n")

        env_vars = get_env_with_dotenv(tmpdir_path)

        # Should include .env variable
        assert "DOTENV_VAR" in env_vars
        assert env_vars["DOTENV_VAR"] == "dotenv-value"

        # Should also include system environment variables
        assert "PATH" in env_vars  # System var


def test_get_env_with_dotenv_precedence():
    """Test precedence order: .env < system < additional."""
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci/.env
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()
        mci_env = mci_dir / ".env"
        mci_env.write_text("TEST_VAR=mci-value\nMCI_ONLY=mci\n")

        # Create root .env
        root_env = tmpdir_path / ".env"
        root_env.write_text("TEST_VAR=root-value\nROOT_ONLY=root\n")

        # Set system environment variable
        original_value = os.environ.get("TEST_VAR")
        try:
            os.environ["TEST_VAR"] = "system-value"

            # Get with additional override
            env_vars = get_env_with_dotenv(
                tmpdir_path, additional_env={"TEST_VAR": "additional-value"}
            )

            # Precedence: additional > system > root > mci
            assert env_vars["TEST_VAR"] == "additional-value"
            assert env_vars["MCI_ONLY"] == "mci"
            assert env_vars["ROOT_ONLY"] == "root"

        finally:
            # Restore original value
            if original_value is not None:
                os.environ["TEST_VAR"] = original_value
            else:
                os.environ.pop("TEST_VAR", None)


def test_get_env_with_dotenv_no_additional():
    """Test getting environment without additional vars."""
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create root .env
        root_env = tmpdir_path / ".env"
        root_env.write_text("DOTENV_VAR=dotenv-value\n")

        # Set system environment variable
        original_value = os.environ.get("SYSTEM_VAR")
        try:
            os.environ["SYSTEM_VAR"] = "system-value"

            env_vars = get_env_with_dotenv(tmpdir_path)

            # Should have both .env and system vars
            assert env_vars["DOTENV_VAR"] == "dotenv-value"
            assert env_vars["SYSTEM_VAR"] == "system-value"

        finally:
            if original_value is not None:
                os.environ["SYSTEM_VAR"] = original_value
            else:
                os.environ.pop("SYSTEM_VAR", None)


def test_env_mci_priority_over_env():
    """Test that when .env.mci files exist, .env files are not loaded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create .env file
        env_file = tmpdir_path / ".env"
        env_file.write_text("API_KEY=from-env\nENV_ONLY=env-value\n")

        # Create .env.mci file (should take priority, .env not loaded)
        env_mci_file = tmpdir_path / ".env.mci"
        env_mci_file.write_text("API_KEY=from-env-mci\nMCI_ONLY=mci-value\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        # Only .env.mci should be loaded
        assert env_vars["API_KEY"] == "from-env-mci"
        assert "ENV_ONLY" not in env_vars  # .env is not loaded
        assert env_vars["MCI_ONLY"] == "mci-value"


def test_mci_env_mci_priority():
    """Test that when ./mci/.env.mci exists, ./mci/.env is not loaded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # Create ./mci/.env
        mci_env = mci_dir / ".env"
        mci_env.write_text("SHARED_KEY=from-mci-env\nMCI_ENV_ONLY=mci-env\n")

        # Create ./mci/.env.mci (should take priority, ./mci/.env not loaded)
        mci_env_mci = mci_dir / ".env.mci"
        mci_env_mci.write_text("SHARED_KEY=from-mci-env-mci\nMCI_MCI_ONLY=mci-mci\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        # Only ./mci/.env.mci should be loaded
        assert env_vars["SHARED_KEY"] == "from-mci-env-mci"
        assert "MCI_ENV_ONLY" not in env_vars  # ./mci/.env is not loaded
        assert env_vars["MCI_MCI_ONLY"] == "mci-mci"


def test_full_precedence_with_env_mci():
    """Test precedence order when .env.mci files exist (only .env.mci files loaded)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # These .env files should NOT be loaded when .env.mci files exist
        mci_env = mci_dir / ".env"
        mci_env.write_text("KEY=mci-env\nMCI_ENV=1\n")
        root_env = tmpdir_path / ".env"
        root_env.write_text("KEY=root-env\nROOT_ENV=3\n")

        # These .env.mci files SHOULD be loaded
        mci_env_mci = mci_dir / ".env.mci"
        mci_env_mci.write_text("KEY=mci-env-mci\nMCI_MCI=2\n")
        root_env_mci = tmpdir_path / ".env.mci"
        root_env_mci.write_text("KEY=root-env-mci\nROOT_MCI=4\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        # root .env.mci should win for KEY
        assert env_vars["KEY"] == "root-env-mci"
        # .env files should not be loaded
        assert "MCI_ENV" not in env_vars
        assert "ROOT_ENV" not in env_vars
        # Only .env.mci files loaded
        assert env_vars["MCI_MCI"] == "2"
        assert env_vars["ROOT_MCI"] == "4"


def test_env_mci_only_in_root():
    """Test .env.mci works when only in root directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create only .env.mci in root
        root_env_mci = tmpdir_path / ".env.mci"
        root_env_mci.write_text("MCI_VAR=mci-root\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        assert env_vars["MCI_VAR"] == "mci-root"


def test_env_mci_only_in_mci_dir():
    """Test .env.mci works when only in ./mci directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # Create only .env.mci in ./mci
        mci_env_mci = mci_dir / ".env.mci"
        mci_env_mci.write_text("MCI_VAR=mci-lib\n")

        env_vars = find_and_merge_dotenv_files(tmpdir_path)

        assert env_vars["MCI_VAR"] == "mci-lib"
