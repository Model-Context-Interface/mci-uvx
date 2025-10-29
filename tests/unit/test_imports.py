"""
Unit tests for package imports.

Tests that all package modules can be imported correctly.
"""


def test_import_mci_package():
    """Test that the mci package can be imported."""
    import mci

    assert hasattr(mci, "main")


def test_import_main_function():
    """Test that the main function can be imported directly."""
    from mci import main

    assert callable(main)


def test_import_mci_module():
    """Test that the mci.mci module can be imported."""
    from mci import mci

    assert hasattr(mci, "main")


def test_import_cli_package():
    """Test that the cli package can be imported."""
    from mci import cli

    assert cli is not None


def test_import_core_package():
    """Test that the core package can be imported."""
    from mci import core

    assert core is not None


def test_import_utils_package():
    """Test that the utils package can be imported."""
    from mci import utils

    assert utils is not None


def test_package_exports():
    """Test that the package exports the expected symbols."""
    import mci

    assert "__all__" in dir(mci)
    assert "main" in mci.__all__
