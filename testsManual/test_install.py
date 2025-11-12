#!/usr/bin/env python3
"""
Manual test for the install command.

This test runs the install command in a real directory and verifies
all files are created correctly.

Usage:
    uv run python testsManual/test_install.py

Requirements:
    - Run from the repository root
    - Will create a temporary directory for testing
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"✗ {message}")


def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result


def test_install_json():
    """Test install command with JSON format."""
    print_section("Test 1: Install with JSON format (default)")

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in: {tmpdir}")

        # Run install command
        result = run_command("uv run mcix install", cwd=tmpdir)

        if result.returncode != 0:
            print_error(f"Install command failed: {result.stderr}")
            return False

        print(result.stdout)

        # Verify files
        tmppath = Path(tmpdir)

        if not (tmppath / "mci.json").exists():
            print_error("mci.json not created")
            return False
        print_success("mci.json created")

        if not (tmppath / "mci").is_dir():
            print_error("./mci directory not created")
            return False
        print_success("./mci directory created")

        if not (tmppath / "mci" / ".gitignore").exists():
            print_error("./mci/.gitignore not created")
            return False
        print_success("./mci/.gitignore created")

        if not (tmppath / "mci" / "example_toolset.mci.json").exists():
            print_error("./mci/example_toolset.mci.json not created")
            return False
        print_success("./mci/example_toolset.mci.json created")

        # Show file contents
        print("\n--- mci.json content (first 10 lines) ---")
        content = (tmppath / "mci.json").read_text().split('\n')[:10]
        print('\n'.join(content))

        print("\n--- ./mci/.gitignore content ---")
        print((tmppath / "mci" / ".gitignore").read_text())

        return True


def test_install_yaml():
    """Test install command with YAML format."""
    print_section("Test 2: Install with YAML format (--yaml)")

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in: {tmpdir}")

        # Run install command with --yaml flag
        result = run_command("uv run mcix install --yaml", cwd=tmpdir)

        if result.returncode != 0:
            print_error(f"Install command failed: {result.stderr}")
            return False

        print(result.stdout)

        # Verify files
        tmppath = Path(tmpdir)

        if not (tmppath / "mci.yaml").exists():
            print_error("mci.yaml not created")
            return False
        print_success("mci.yaml created")

        if (tmppath / "mci.json").exists():
            print_error("mci.json should not exist with --yaml flag")
            return False
        print_success("mci.json correctly not created")

        # Show file contents
        print("\n--- mci.yaml content (first 10 lines) ---")
        content = (tmppath / "mci.yaml").read_text().split('\n')[:10]
        print('\n'.join(content))

        return True


def test_install_existing_files():
    """Test install command with existing files."""
    print_section("Test 3: Install with existing files (idempotency)")

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in: {tmpdir}")

        # Run install first time
        print("Running install first time...")
        result1 = run_command("uv run mcix install", cwd=tmpdir)
        if result1.returncode != 0:
            print_error(f"First install failed: {result1.stderr}")
            return False
        print_success("First install succeeded")

        # Run install second time
        print("\nRunning install second time...")
        result2 = run_command("uv run mcix install", cwd=tmpdir)
        if result2.returncode != 0:
            print_error(f"Second install failed: {result2.stderr}")
            return False

        print(result2.stdout)

        if "already exists" not in result2.stdout:
            print_error("Expected 'already exists' message not found")
            return False
        print_success("Correctly detected existing files")

        return True


def test_install_help():
    """Test install command help."""
    print_section("Test 4: Install command help")

    result = run_command("uv run mcix install --help")

    if result.returncode != 0:
        print_error(f"Help command failed: {result.stderr}")
        return False

    print(result.stdout)

    if "Initialize an MCI project structure" not in result.stdout:
        print_error("Expected help text not found")
        return False
    print_success("Help text correct")

    if "--yaml" not in result.stdout:
        print_error("--yaml flag not documented in help")
        return False
    print_success("--yaml flag documented")

    return True


def main():
    """Run all manual tests."""
    print_section("MCI Install Command - Manual Tests")
    print("Running manual tests for the install command...")

    tests = [
        test_install_json,
        test_install_yaml,
        test_install_existing_files,
        test_install_help,
    ]

    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            results.append(False)

    # Summary
    print_section("Test Summary")
    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print_success("All tests passed!")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
