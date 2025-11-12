# Development Guide

This guide covers the technical aspects of developing the MCI CLI tool, including architecture, internal components, and contribution workflows.

## Table of Contents

- [Setting Up Development Environment](#setting-up-development-environment)
- [Project Architecture](#project-architecture)
- [Core Components](#core-components)
- [Development Workflows](#development-workflows)
- [Testing](#testing)
- [Documentation](#documentation)

## Setting Up Development Environment

### Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) to manage Python and dependencies.

1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Fork and clone the repository**:
   - [Fork the repo](https://github.com/Model-Context-Interface/mci-uvx/fork)
   - [Clone your fork](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

3. **Install dependencies**:
   ```bash
   make install
   # or
   uv sync --all-extras
   ```

## Project Architecture

### Directory Structure

```
src/mci/
├── __init__.py          # Package initialization, exports main CLI entry point
├── mci.py               # Main CLI entry point with Click group
├── cli/                 # CLI command modules
│   ├── __init__.py
│   ├── install.py       # mcix install command
│   ├── list.py          # mcix list command
│   ├── validate.py      # mcix validate command
│   ├── add.py           # mcix add command
│   ├── run.py           # mcix run command
│   └── formatters/      # Output formatters (JSON, YAML, table)
├── core/                # Core business logic
│   ├── __init__.py
│   ├── config.py        # Configuration loading and management
│   ├── file_finder.py   # MCI file discovery utilities
│   ├── mci_client.py    # MCIClient wrapper for CLI integration
│   ├── mcp_server.py    # MCP server creation infrastructure
│   ├── dynamic_server.py # Dynamic MCP server from MCI schemas
│   ├── tool_converter.py # MCI to MCP tool conversion
│   ├── tool_manager.py  # Tool filtering and management
│   ├── schema_editor.py # Schema editing utilities
│   └── validator.py     # Schema validation
└── utils/               # Utility functions
    ├── __init__.py
    ├── error_handler.py  # Error formatting for CLI
    ├── error_formatter.py # Rich-based error display
    ├── validation.py     # File and path validation
    └── timestamp.py      # Timestamp utilities
```

### Main Entry Point

The main entry point is the `main()` function in `src/mci/mci.py`, which is exported from the package root. This function is a Click command group that serves as the foundation for all CLI commands.

## Core Components

### Configuration & File Discovery

#### MCIFileFinder

The `MCIFileFinder` class provides methods to locate MCI configuration files:

```python
from mci.core.file_finder import MCIFileFinder

finder = MCIFileFinder()
config_file = finder.find_mci_file("./my_project")
```

**File Priority**: When both `mci.json` and `mci.yaml` exist, JSON format is prioritized.

**Supported Formats**: `mci.json`, `mci.yaml`, `mci.yml`

#### MCIConfig

The `MCIConfig` class uses `MCIClient` from mci-py to load and validate MCI configuration files:

```python
from mci.core.config import MCIConfig

config = MCIConfig()
client = config.load("mci.json")
tools = client.tools()
```

**Environment Variables**: Support for environment variable substitution in MCI schemas:

```python
env_vars = {
    "API_KEY": "your-api-key",
    "BASE_URL": "https://api.example.com"
}
client = config.load("mci.json", env_vars)
```

### MCI-PY Integration

All tool loading, filtering, and schema operations are delegated to `MCIClient` from mci-py, ensuring consistency with the upstream adapter.

#### MCIClientWrapper

The `MCIClientWrapper` class provides a CLI-friendly interface to `MCIClient`:

```python
from mci.core.mci_client import MCIClientWrapper

wrapper = MCIClientWrapper("mci.json")
tools = wrapper.get_tools()

# Filter tools
api_tools = wrapper.filter_tags(["api"])
safe_tools = wrapper.filter_except(["deprecated_tool"])
specific_tools = wrapper.filter_only(["tool1", "tool2"])
```

#### Tool Filtering

The `ToolManager` class parses CLI filter specifications and applies filters:

```python
from mci.core.tool_manager import ToolManager

api_tools = ToolManager.apply_filter_spec(wrapper, "tags:api,database")
non_deprecated = ToolManager.apply_filter_spec(wrapper, "without-tags:deprecated")
selected_tools = ToolManager.apply_filter_spec(wrapper, "only:tool1,tool2")
```

**Supported Filter Types**:
- `only:tool1,tool2,...` - Include only specified tools by name
- `except:tool1,tool2,...` - Exclude specified tools by name
- `tags:tag1,tag2,...` - Include tools with any of these tags (OR logic)
- `without-tags:tag1,tag2,...` - Exclude tools with any of these tags
- `toolsets:toolset1,toolset2,...` - Include tools from specified toolsets

### MCP Server Infrastructure

The MCI CLI provides infrastructure for creating MCP servers that dynamically serve tools from MCI schemas.

#### Components

1. **MCIToolConverter**: Converts MCI tool definitions to MCP tool format
2. **MCPServerBuilder**: Creates and configures MCP servers with MCI tools
3. **ServerInstance**: Manages server lifecycle and delegates execution to MCIClient
4. **DynamicMCPServer**: High-level interface for creating and running servers

#### Usage Example

```python
from mci.core.dynamic_server import DynamicMCPServer

# Create and run server
server = DynamicMCPServer("mci.json", filter_spec="tags:api")
await server.create_from_mci_schema()
await server.start_stdio()
```

#### Architecture Flow

```
MCI Schema → MCIClient → MCPServerBuilder → MCP Server → STDIO
                ↓              ↓                ↓
            Tools loaded   Converted      Tool execution
            from schema    to MCP format  via MCIClient
```

### Error Handling

#### ErrorHandler

Formats `MCIClientError` exceptions for CLI display:

```python
from mci.utils.error_handler import ErrorHandler
from mcipy import MCIClientError

try:
    wrapper = MCIClientWrapper("nonexistent.mci.json")
except MCIClientError as e:
    formatted = ErrorHandler.format_mci_client_error(e)
    print(formatted)
```

#### ErrorFormatter

Provides Rich-based formatting for validation errors and warnings:

```python
from mci.utils.error_formatter import ErrorFormatter, ValidationError

formatter = ErrorFormatter()
errors = [ValidationError(message="Missing required field: name")]
formatter.format_validation_errors(errors)
```

## Development Workflows

The `Makefile` provides shortcuts to `uv` commands for developer convenience.

```bash
# Install all dependencies
make install

# Run sync, lint, and test
make

# Build wheel
make build

# Run linters
make lint

# Run tests
make test

# Run tests with coverage
make coverage

# Clean build artifacts
make clean

# Upgrade dependencies
make upgrade
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file with output
uv run pytest -s tests/test_file.py

# With coverage
uv run pytest --cov=src/mci --cov-report=term-missing

# Single test
uv run pytest tests/test_file.py::test_function_name
```

### Linting

```bash
# Run all linters
make lint

# Individual linters
uv run ruff check --fix src/
uv run ruff format src/
uv run basedpyright --stats src/
```

### Dependency Management

```bash
# Add dependency
uv add package_name

# Add dev dependency
uv add --dev package_name

# Update to latest compatible versions
uv sync --upgrade

# Update specific package
uv lock --upgrade-package package_name
```

### Installing Development Version

```bash
# Install as editable tool
uv tool install --editable .

# Now you can use `mci` command globally with your dev changes
mci --help
```

## Testing

### Test Organization

```
tests/
├── test_*.py              # Feature tests
├── unit/                  # Unit tests
│   ├── cli/              # CLI command tests
│   ├── core/             # Core logic tests
│   └── utils/            # Utility tests
└── testsManual/          # Manual integration tests
```

### Test Coverage Goals

- **Target**: 90%+ test coverage across all modules
- **Current**: 90% (Stage 10 achievement)

### Writing Tests

#### Unit Tests

Test individual functions in isolation:

```python
def test_is_valid_path_with_valid_path():
    """Test is_valid_path with a valid path."""
    assert is_valid_path("./mci.json") is True
```

#### Feature Tests

Test complete features end-to-end:

```python
def test_list_command_basic(runner):
    """Test basic list command."""
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Available Tools" in result.output
```

#### Manual Tests

Large integration tests run individually:

```bash
uv run python testsManual/test_mcp_server.py
```

## Documentation

### Code Documentation Standards

#### File-Level Comments

Every file should have a docstring explaining:
- Purpose of the file
- What functionality it provides
- How it fits into the project

Example:
```python
"""
mci_client.py - MCIClient wrapper for CLI integration

This module provides a CLI-friendly wrapper around MCIClient from mci-py,
handling tool loading, filtering, and error formatting for command-line usage.
"""
```

#### Function/Class Documentation

Every function and class should have a docstring with:
- What it does
- Why it exists
- Important implementation details
- Parameters and return values

Example:
```python
def apply_filter_spec(wrapper: MCIClientWrapper, filter_spec: str) -> list:
    """
    Apply a filter specification to tools from MCIClient wrapper.
    
    Parses filter specifications like "tags:api,database" and applies
    the appropriate filtering method from MCIClient. Supports all MCI
    filter types: only, except, tags, without-tags, toolsets.
    
    Args:
        wrapper: MCIClientWrapper instance with loaded tools
        filter_spec: Filter specification string
        
    Returns:
        List of filtered tools
        
    Raises:
        ValueError: If filter specification is invalid
    """
```

### Documentation Files

- **README.md** - User-focused quickstart and usage guide
- **development.md** - This file - technical development guide
- **PLAN.md** - Full implementation plan and roadmap
- **PRD.md** - Product requirements and specifications
- **installation.md** - Detailed installation instructions
- **publishing.md** - PyPI publishing guide
- **mcp-server-docs.md** - Advanced MCP server features

## IDE Setup

For VSCode, Cursor, or similar editors:

### Recommended Extensions

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Based Pyright](https://marketplace.visualstudio.com/items?itemName=detachhead.basedpyright)

### Agent Rules

See [.cursor/rules](.cursor/rules) for agent rules. Generate aggregated rules:

```bash
make agent-rules
```

This creates `CLAUDE.md` and `AGENTS.md` from the cursor rules.

## Contributing

### Contribution Workflow

1. **Fork and clone** the repository
2. **Create a branch** for your feature/fix
3. **Make changes** following the code style
4. **Write tests** for your changes
5. **Run linters and tests**:
   ```bash
   make lint
   make test
   make coverage
   ```
6. **Commit** with clear messages
7. **Push** to your fork
8. **Open a pull request**

### Code Style

- Use modern Python 3.11+ features
- Type annotations for all functions
- Docstrings for all public APIs
- Follow existing code patterns
- Keep comments concise and explanatory

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for YAML output in list command

- Implement YAMLFormatter class
- Add --format yaml option
- Update tests for new format
- Document in README
```

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [basedpyright Documentation](https://docs.basedpyright.com/latest/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [mci-py Library](https://github.com/Model-Context-Interface/mci-py)

---

*This file was built with [simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
