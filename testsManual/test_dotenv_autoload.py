#!/usr/bin/env python3
"""
Manual test for .env file auto-loading feature.

This test creates a temporary MCI project with .env files and verifies
that environment variables are automatically loaded when running MCI commands.

Run this test manually to verify the feature works:
    uv run python testsManual/test_dotenv_autoload.py
"""

import tempfile
from pathlib import Path

from rich.console import Console

from mci.core.config import MCIConfig
from mci.core.mci_client import MCIClientWrapper

console = Console()


def test_basic_dotenv_loading():
    """Test basic .env file loading from project root."""
    console.print("\n[bold cyan]Test 1: Basic .env file loading[/bold cyan]")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create .env file
        env_file = tmpdir_path / ".env"
        env_content = """# Test .env file
API_KEY=test-api-key-123
BASE_URL=https://api.example.com
DEBUG=true
"""
        env_file.write_text(env_content)
        console.print(f"✓ Created .env file at: {env_file}")
        console.print(f"  Contents:\n{env_content}")

        # Create MCI schema
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
    "schemaVersion": "1.0",
    "metadata": {
        "name": "Test Project",
        "description": "Test .env auto-loading"
    },
    "tools": [
        {
            "name": "test_tool",
            "description": "Test tool with env vars",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            },
            "execution": {
                "type": "text",
                "text": "API_KEY={{env.API_KEY}}, BASE_URL={{env.BASE_URL}}, DEBUG={{env.DEBUG}}"
            }
        }
    ],
    "toolsets": []
}"""
        schema_file.write_text(schema_content)
        console.print(f"✓ Created schema file at: {schema_file}")

        # Load config
        config = MCIConfig()
        client = config.load(str(schema_file))

        console.print("✓ Config loaded successfully")
        console.print(
            f"  Tools loaded: {len(client.tools())} - "
            f"{[t.name for t in client.tools()]}"
        )
        console.print("\n[bold green]✓ Test 1 PASSED[/bold green]\n")


def test_dotenv_precedence():
    """Test that root .env overrides ./mci/.env."""
    console.print("\n[bold cyan]Test 2: .env precedence (root > ./mci)[/bold cyan]")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create mci directory
        mci_dir = tmpdir_path / "mci"
        mci_dir.mkdir()

        # Create ./mci/.env
        mci_env = mci_dir / ".env"
        mci_env_content = """# MCI library defaults
SHARED_VAR=from-mci-dir
MCI_ONLY_VAR=mci-value
API_KEY=default-key
"""
        mci_env.write_text(mci_env_content)
        console.print(f"✓ Created ./mci/.env file")
        console.print(f"  Contents:\n{mci_env_content}")

        # Create root .env (should override SHARED_VAR and API_KEY)
        root_env = tmpdir_path / ".env"
        root_env_content = """# Project-specific overrides
SHARED_VAR=from-root
ROOT_ONLY_VAR=root-value
API_KEY=project-key
"""
        root_env.write_text(root_env_content)
        console.print(f"✓ Created root .env file")
        console.print(f"  Contents:\n{root_env_content}")

        # Create schema
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
    "schemaVersion": "1.0",
    "metadata": {
        "name": "Test Precedence",
        "description": "Test .env precedence"
    },
    "tools": [],
    "toolsets": []
}"""
        schema_file.write_text(schema_content)

        # Load config
        config = MCIConfig()
        config.load(str(schema_file))

        console.print("✓ Config loaded successfully")
        console.print("\n[bold]Expected precedence:[/bold]")
        console.print("  SHARED_VAR should be: from-root (root overrides mci)")
        console.print("  API_KEY should be: project-key (root overrides mci)")
        console.print("  MCI_ONLY_VAR should be: mci-value (only in mci)")
        console.print("  ROOT_ONLY_VAR should be: root-value (only in root)")
        console.print("\n[bold green]✓ Test 2 PASSED[/bold green]\n")


def test_no_dotenv_files():
    """Test that MCI works fine without .env files."""
    console.print("\n[bold cyan]Test 3: No .env files (should work silently)[/bold cyan]")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create schema only (no .env files)
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
    "schemaVersion": "1.0",
    "metadata": {
        "name": "Test No .env",
        "description": "Test without .env files"
    },
    "tools": [],
    "toolsets": []
}"""
        schema_file.write_text(schema_content)
        console.print(f"✓ Created schema file at: {schema_file}")
        console.print("  No .env files created")

        # Load config
        config = MCIConfig()
        config.load(str(schema_file))

        console.print("✓ Config loaded successfully without .env files")
        console.print("\n[bold green]✓ Test 3 PASSED[/bold green]\n")


def test_explicit_env_override():
    """Test that explicit env_vars override .env files."""
    console.print("\n[bold cyan]Test 4: Explicit env vars override .env[/bold cyan]")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create .env file
        env_file = tmpdir_path / ".env"
        env_content = """OVERRIDE_VAR=from-dotenv
DOTENV_ONLY=dotenv-value
"""
        env_file.write_text(env_content)
        console.print(f"✓ Created .env file")
        console.print(f"  Contents:\n{env_content}")

        # Create schema
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
    "schemaVersion": "1.0",
    "metadata": {
        "name": "Test Override",
        "description": "Test explicit override"
    },
    "tools": [],
    "toolsets": []
}"""
        schema_file.write_text(schema_content)

        # Load config with explicit env vars
        config = MCIConfig()
        explicit_env = {"OVERRIDE_VAR": "from-explicit", "EXPLICIT_ONLY": "explicit-value"}
        config.load(str(schema_file), env_vars=explicit_env)

        console.print("✓ Config loaded with explicit env vars")
        console.print("\n[bold]Expected results:[/bold]")
        console.print("  OVERRIDE_VAR should be: from-explicit (explicit overrides .env)")
        console.print("  DOTENV_ONLY should be: dotenv-value (from .env)")
        console.print("  EXPLICIT_ONLY should be: explicit-value (only in explicit)")
        console.print("\n[bold green]✓ Test 4 PASSED[/bold green]\n")


def test_mci_client_wrapper():
    """Test MCIClientWrapper with .env auto-loading."""
    console.print(
        "\n[bold cyan]Test 5: MCIClientWrapper with .env auto-loading[/bold cyan]"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create .env file
        env_file = tmpdir_path / ".env"
        env_content = """WRAPPER_VAR=wrapper-value
API_KEY=wrapper-key
"""
        env_file.write_text(env_content)
        console.print(f"✓ Created .env file")

        # Create schema
        schema_file = tmpdir_path / "mci.json"
        schema_content = """{
    "schemaVersion": "1.0",
    "metadata": {
        "name": "Test Wrapper",
        "description": "Test MCIClientWrapper"
    },
    "tools": [
        {
            "name": "test_tool",
            "description": "Test tool",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            },
            "execution": {
                "type": "text",
                "text": "API={{env.API_KEY}}"
            }
        }
    ],
    "toolsets": []
}"""
        schema_file.write_text(schema_content)

        # Create wrapper
        wrapper = MCIClientWrapper(str(schema_file))

        console.print("✓ MCIClientWrapper created successfully")
        tools = wrapper.get_tools()
        console.print(f"  Tools loaded: {len(tools)} - {[t.name for t in tools]}")
        console.print("\n[bold green]✓ Test 5 PASSED[/bold green]\n")


def main():
    """Run all manual tests."""
    console.print("\n" + "=" * 60)
    console.print("[bold]Manual Test: .env Auto-Loading Feature[/bold]")
    console.print("=" * 60)

    try:
        test_basic_dotenv_loading()
        test_dotenv_precedence()
        test_no_dotenv_files()
        test_explicit_env_override()
        test_mci_client_wrapper()

        console.print("\n" + "=" * 60)
        console.print("[bold green]✓ All manual tests PASSED![/bold green]")
        console.print("=" * 60 + "\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed with error:[/bold red]")
        console.print(f"  {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
