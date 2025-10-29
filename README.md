# MCI CLI Tool

A command-line interface for managing Model Context Interface (MCI) schemas and dynamically running MCP (Model Context Protocol) servers using defined MCI toolsets.

## Project Structure — Initial Setup

The MCI CLI tool is organized into the following directory structure:

```
src/mci/
├── __init__.py          # Package initialization, exports main CLI entry point
├── mci.py               # Main CLI entry point with Click group
├── cli/                 # CLI command modules
│   └── __init__.py      # CLI package initialization
├── core/                # Core business logic
│   └── __init__.py      # Core package initialization
└── utils/               # Utility functions
    └── __init__.py      # Utils package initialization
```

### Directory Purpose

- **`src/mci/`**: Main package directory containing all MCI CLI code
- **`src/mci/mci.py`**: Main entry point with `main()` function that implements the CLI using Click
- **`src/mci/cli/`**: Contains all CLI command implementations (install, list, validate, add, run)
- **`src/mci/core/`**: Core business logic including MCI schema management, tool loading, and MCP server creation
- **`src/mci/utils/`**: Utility functions for error handling, validation, formatting, and other helpers

### Main Entry Point

The main entry point is the `main()` function in `src/mci/mci.py`, which is exported from the package root. This function is a Click command group that serves as the foundation for all CLI commands.

### CLI Usage

To use the CLI tool:

```bash
# Show help and available commands
uv run mci --help

# Show version
uv run mci --version
```

### Development Foundation

All further development stages build on this foundational structure:
- **Stage 1**: ✅ Project Setup & Core Dependencies
- **Stage 2**: ✅ Configuration & File Discovery
- **Stage 3**: CLI Command: `mci install`
- **Stage 4**: MCI-PY Integration & Tool Loading
- **Stage 5**: CLI Command: `mci list`
- **Stage 6**: CLI Command: `mci validate`
- **Stage 7**: CLI Command: `mci add`
- **Stage 8**: MCP Server Creation Infrastructure
- **Stage 9**: CLI Command: `mci run`
- **Stage 10**: Error Handling, Documentation & Final Polish

* * *

## Configuration & File Discovery

The MCI CLI tool includes robust configuration file discovery and validation functionality.

### File Discovery

The `MCIFileFinder` class provides methods to locate MCI configuration files in a directory:

```python
from mci.core.file_finder import MCIFileFinder

# Find MCI configuration file (mci.json or mci.yaml)
finder = MCIFileFinder()
config_file = finder.find_mci_file("./my_project")

if config_file:
    print(f"Found: {config_file}")
else:
    print("No MCI configuration file found")
```

**File Priority**: When both `mci.json` and `mci.yaml` exist in the same directory, JSON format is prioritized.

**Supported Formats**:
- `mci.json` (preferred)
- `mci.yaml`
- `mci.yml`

### File Format Detection

```python
from mci.core.file_finder import MCIFileFinder

finder = MCIFileFinder()
file_format = finder.get_file_format("./mci.json")
print(file_format)  # Output: "json"

file_format = finder.get_file_format("./mci.yaml")
print(file_format)  # Output: "yaml"
```

### Configuration Loading

The `MCIConfig` class uses `MCIClient` from mci-py to load and validate MCI configuration files:

```python
from mci.core.config import MCIConfig
from mcipy import MCIClientError

# Load and validate configuration
config = MCIConfig()
try:
    client = config.load("mci.json")
    tools = client.tools()
    print(f"Loaded {len(tools)} tools")
except MCIClientError as e:
    print(f"Schema invalid: {e}")
```

### Schema Validation

```python
from mci.core.config import MCIConfig

# Validate schema without loading
config = MCIConfig()
is_valid, error = config.validate_schema("mci.json")

if is_valid:
    print("Schema is valid")
else:
    print(f"Validation failed: {error}")
```

### Environment Variables

Support for environment variable substitution in MCI schemas:

```python
from mci.core.config import MCIConfig

# Load with environment variables
config = MCIConfig()
env_vars = {
    "API_KEY": "your-api-key",
    "BASE_URL": "https://api.example.com"
}
client = config.load("mci.json", env_vars)
```

### Error Handling Strategy

The configuration system provides user-friendly error messages by leveraging mci-py's built-in validation:

1. **MCIClient Validation**: Schema validation is performed by `MCIClient` during initialization
2. **Error Extraction**: Error messages from `MCIClientError` are extracted and presented to users
3. **File Not Found**: Specific handling for missing configuration files
4. **Malformed Files**: Detection of JSON/YAML parsing errors

Example error handling:

```python
from mci.core.config import MCIConfig
from mcipy import MCIClientError

config = MCIConfig()
is_valid, error = config.validate_schema("path/to/mci.json")

if not is_valid:
    # Error message contains details from MCIClient validation
    print(f"Configuration error: {error}")
    # Take corrective action
```

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For the full implementation plan, see [PLAN.md](PLAN.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
