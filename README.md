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

## Bootstrap a Project with `mci install`

The `mci install` command initializes a new MCI project with starter configuration files and directory structure.

### Basic Usage

```bash
# Initialize a new MCI project with JSON configuration (default)
uv run mci install

# Initialize with YAML configuration
uv run mci install --yaml
```

### What Gets Created

Running `mci install` creates the following files and directories:

```
project-root/
├── mci.json (or mci.yaml)         # Main MCI configuration file
└── mci/                           # MCI library directory
    ├── .gitignore                 # Git ignore file (includes mcp/)
    └── example_toolset.mci.json   # Example toolset with CLI tool
```

#### Main Configuration File (`mci.json`)

The default configuration includes an example echo tool:

```json
{
  "schemaVersion": "1.0",
  "metadata": {
    "name": "Example Project",
    "description": "Example MCI configuration"
  },
  "tools": [
    {
      "name": "echo_test",
      "description": "Simple echo test tool",
      "inputSchema": {
        "type": "object",
        "properties": {
          "message": {
            "type": "string",
            "description": "Message to echo"
          }
        },
        "required": ["message"]
      },
      "execution": {
        "type": "text",
        "text": "Echo: {{props.message}}"
      }
    }
  ],
  "toolsets": [],
  "mcp_servers": {}
}
```

#### Example Toolset (`mci/example_toolset.mci.json`)

The example toolset includes a CLI tool for listing directory contents:

```json
{
  "schemaVersion": "1.0",
  "metadata": {
    "name": "Example Toolset",
    "description": "Example MCI toolset with CLI tool"
  },
  "tools": [
    {
      "name": "list_files",
      "description": "List files in a directory",
      "inputSchema": {
        "type": "object",
        "properties": {
          "directory": {
            "type": "string",
            "description": "Directory to list files from"
          }
        },
        "required": ["directory"]
      },
      "execution": {
        "type": "cli",
        "command": "ls",
        "args": ["-la", "{{props.directory}}"]
      },
      "enableAnyPaths": false,
      "directoryAllowList": ["{{env.PROJECT_ROOT}}"]
    }
  ],
  "toolsets": [],
  "mcp_servers": {}
}
```

### Existing Files Handling

The install command is idempotent and handles existing files gracefully:

- **Existing configuration file**: Skips creation and displays a warning
- **Existing `.gitignore`**: Updates if `mcp/` entry is missing, otherwise skips
- **Existing example toolset**: Skips creation and displays a warning

No files are overwritten by default, ensuring safe re-runs.

### Next Steps After Installation

After running `mci install`, you can:

1. **Review the configuration**: Edit `mci.json` or `mci.yaml` to customize your tools
2. **Validate your setup**: Run `mci validate` (when implemented) to check your configuration
3. **List available tools**: Run `mci list` (when implemented) to see all defined tools
4. **Initialize MCIClient**: Use the configuration programmatically:

```python
from mcipy import MCIClient

# Load the generated configuration
client = MCIClient(schema_file_path="mci.json")

# List available tools
tools = client.tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}")
```

### `.gitignore` Configuration

The `./mci/.gitignore` file is automatically created or updated to include:

```
mcp/
```

This prevents the `./mci/mcp/` directory (used for MCP server storage) from being committed to version control.


### Development Foundation

All further development stages build on this foundational structure:
- **Stage 1**: ✅ Project Setup & Core Dependencies
- **Stage 2**: ✅ Configuration & File Discovery
- **Stage 3**: ✅ CLI Command: `mci install`
- **Stage 4**: ✅ MCI-PY Integration & Tool Loading
- **Stage 5**: CLI Command: `mci list`
- **Stage 6**: CLI Command: `mci validate`
- **Stage 7**: CLI Command: `mci add`
- **Stage 8**: MCP Server Creation Infrastructure
- **Stage 9**: CLI Command: `mci run`
- **Stage 10**: Error Handling, Documentation & Final Polish

* * *

## MCI-PY Integration & Tool Loading

The MCI CLI tool integrates with the **mci-py** library for robust loading and management of MCI tools. All tool loading, filtering, and schema operations are delegated to `MCIClient` from mci-py, ensuring consistency with the upstream adapter and future-proof functionality.

### Key Components

#### MCIClientWrapper

The `MCIClientWrapper` class provides a CLI-friendly interface to `MCIClient` from mci-py:

```python
from mci.core.mci_client import MCIClientWrapper

# Load MCI schema
wrapper = MCIClientWrapper("mci.json")

# Get all tools
tools = wrapper.get_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Filter tools
api_tools = wrapper.filter_tags(["api"])
safe_tools = wrapper.filter_except(["deprecated_tool"])
specific_tools = wrapper.filter_only(["tool1", "tool2"])
```

#### Tool Filtering

The `ToolManager` class parses CLI filter specifications and applies filters using MCIClient methods:

```python
from mci.core.mci_client import MCIClientWrapper
from mci.core.tool_manager import ToolManager

wrapper = MCIClientWrapper("mci.json")

# Apply filter specifications
api_tools = ToolManager.apply_filter_spec(wrapper, "tags:api,database")
non_deprecated = ToolManager.apply_filter_spec(wrapper, "without-tags:deprecated")
selected_tools = ToolManager.apply_filter_spec(wrapper, "only:tool1,tool2,tool3")
```

**Supported Filter Types:**
- `only:tool1,tool2,...` - Include only specified tools by name
- `except:tool1,tool2,...` - Exclude specified tools by name
- `tags:tag1,tag2,...` - Include tools with any of these tags (OR logic)
- `without-tags:tag1,tag2,...` - Exclude tools with any of these tags (OR logic)
- `toolsets:toolset1,toolset2,...` - Include tools from specified toolsets

### MCIClient Delegation

All tool operations delegate to `MCIClient` from mci-py:

- **Schema parsing**: `MCIClient` validates and loads MCI schemas
- **Tool loading**: Uses Pydantic models from mci-py for type-safe tool definitions
- **Filtering**: Leverages built-in methods: `only()`, `without()`, `tags()`, `withoutTags()`, `toolsets()`
- **Environment variables**: Template substitution via `MCIClient`
- **Validation**: Schema validation performed by `MCIClient` during initialization

No filtering or validation logic is reimplemented in the CLI. The wrapper focuses on:
- CLI-specific error handling
- Filter specification parsing
- Output formatting for terminal display

### Error Handling

The `ErrorHandler` class formats `MCIClientError` exceptions for CLI-friendly display:

```python
from mci.core.mci_client import MCIClientWrapper
from mci.utils.error_handler import ErrorHandler
from mcipy import MCIClientError

try:
    wrapper = MCIClientWrapper("nonexistent.mci.json")
except MCIClientError as e:
    # Format error for CLI display
    formatted_error = ErrorHandler.format_mci_client_error(e)
    print(formatted_error)
```

Error messages include:
- Clear error descriptions
- Helpful suggestions for resolution
- Visual indicators (emoji) for better readability

### Environment Variable Support

```python
from mci.core.mci_client import MCIClientWrapper

# Load with environment variables for template substitution
env_vars = {
    "API_KEY": "your-api-key",
    "BASE_URL": "https://api.example.com",
    "PROJECT_ROOT": "/path/to/project"
}

wrapper = MCIClientWrapper("mci.json", env_vars=env_vars)
tools = wrapper.get_tools()
```

Environment variables are used in tool definitions:
```json
{
  "name": "api_tool",
  "execution": {
    "type": "http",
    "url": "{{env.BASE_URL}}/endpoint",
    "headers": {
      "Authorization": "Bearer {{env.API_KEY}}"
    }
  }
}
```

### Using Pydantic Models

All tool objects are Pydantic models from mci-py:

```python
from mci.core.mci_client import MCIClientWrapper

wrapper = MCIClientWrapper("mci.json")
tools = wrapper.get_tools()

for tool in tools:
    # Access Pydantic model properties
    print(f"Name: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Tags: {tool.tags}")
    print(f"Input Schema: {tool.inputSchema}")
    print(f"Execution Type: {tool.execution.type}")
```

### YAML Support

Both JSON and YAML schema files are supported:

```python
from mci.core.mci_client import MCIClientWrapper

# Load JSON schema
json_wrapper = MCIClientWrapper("mci.json")

# Load YAML schema
yaml_wrapper = MCIClientWrapper("mci.yaml")

# Both work identically
tools = json_wrapper.get_tools()
```

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
