"""
Unit tests for env_scanner.py - Environment variable scanning utilities
"""

from mci.utils.env_scanner import EnvScanner


def test_scan_simple_string():
    """Test scanning a simple string with one env variable."""
    result = EnvScanner.scan_value("{{env.API_KEY}}")
    assert result == {"API_KEY"}


def test_scan_string_multiple_vars():
    """Test scanning a string with multiple env variables."""
    result = EnvScanner.scan_value("{{env.USER}} uses {{env.API_KEY}}")
    assert result == {"USER", "API_KEY"}


def test_scan_string_no_vars():
    """Test scanning a string with no env variables."""
    result = EnvScanner.scan_value("Hello world")
    assert result == set()


def test_scan_string_duplicate_vars():
    """Test scanning a string with duplicate env variable references."""
    result = EnvScanner.scan_value("{{env.KEY}} and {{env.KEY}} again")
    assert result == {"KEY"}


def test_scan_dict_simple():
    """Test scanning a simple dictionary."""
    data = {
        "url": "{{env.BASE_URL}}/api",
        "key": "{{env.API_KEY}}",
    }
    result = EnvScanner.scan_dict(data)
    assert result == {"BASE_URL", "API_KEY"}


def test_scan_dict_nested():
    """Test scanning a nested dictionary."""
    data = {
        "execution": {
            "type": "http",
            "url": "{{env.BASE_URL}}/api",
            "headers": {
                "Authorization": "Bearer {{env.API_KEY}}",
                "X-Custom": "{{env.CUSTOM_HEADER}}",
            },
        }
    }
    result = EnvScanner.scan_dict(data)
    assert result == {"BASE_URL", "API_KEY", "CUSTOM_HEADER"}


def test_scan_list():
    """Test scanning a list."""
    data = [
        "{{env.VAR1}}",
        "{{env.VAR2}}",
        "plain text",
    ]
    result = EnvScanner.scan_value(data)
    assert result == {"VAR1", "VAR2"}


def test_scan_mixed_structure():
    """Test scanning a complex mixed structure."""
    data = {
        "tools": [
            {
                "name": "tool1",
                "execution": {
                    "url": "{{env.URL1}}",
                    "args": ["--key", "{{env.KEY1}}"],
                },
            },
            {
                "name": "tool2",
                "execution": {
                    "url": "{{env.URL2}}",
                    "cwd": "{{env.PROJECT_ROOT}}",
                },
            },
        ],
        "directoryAllowList": ["{{env.ALLOWED_DIR}}"],
    }
    result = EnvScanner.scan_dict(data)
    assert result == {"URL1", "KEY1", "URL2", "PROJECT_ROOT", "ALLOWED_DIR"}


def test_scan_non_string_values():
    """Test scanning dictionary with non-string values."""
    data = {
        "string": "{{env.VAR1}}",
        "number": 123,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
    }
    result = EnvScanner.scan_dict(data)
    assert result == {"VAR1"}


def test_scan_empty_dict():
    """Test scanning an empty dictionary."""
    result = EnvScanner.scan_dict({})
    assert result == set()


def test_scan_empty_list():
    """Test scanning an empty list."""
    result = EnvScanner.scan_value([])
    assert result == set()


def test_scan_variable_name_patterns():
    """Test scanning with various valid variable name patterns."""
    # Valid variable names: start with letter or underscore, contain letters, digits, underscores
    test_cases = [
        ("{{env.API_KEY}}", {"API_KEY"}),
        ("{{env.api_key}}", {"api_key"}),
        ("{{env._private}}", {"_private"}),
        ("{{env.VAR123}}", {"VAR123"}),
        ("{{env.MY_VAR_2}}", {"MY_VAR_2"}),
    ]

    for text, expected in test_cases:
        result = EnvScanner.scan_value(text)
        assert result == expected, f"Failed for: {text}"


def test_scan_invalid_patterns_ignored():
    """Test that invalid patterns are ignored."""
    # These should not be matched
    test_cases = [
        "{{env.}}",  # Empty variable name
        "{{env.123VAR}}",  # Starts with number
        "{{ env.VAR }}",  # Extra spaces
        "{env.VAR}",  # Single braces
        "env.VAR",  # No braces
    ]

    for text in test_cases:
        result = EnvScanner.scan_value(text)
        assert result == set(), f"Should not match: {text}"


def test_scan_partial_match():
    """Test scanning with partial/incomplete patterns."""
    result = EnvScanner.scan_value("Start {{env.VAR1}} middle {{env. broken")
    assert result == {"VAR1"}
