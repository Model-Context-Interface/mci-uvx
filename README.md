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

* * *

## List Available Tools with `mci list`

The `mci list` command displays all available tools from your MCI configuration. It provides a preview of the tool context that would be available when running MCP servers, with support for filtering, multiple output formats, and verbose mode.

### Basic Usage

```bash
# List all tools in table format (default)
uv run mci list

# List tools from a specific configuration file
uv run mci list --file custom.mci.json

# List with verbose output showing tags and parameters
uv run mci list --verbose
```

### Output Formats

The `list` command supports three output formats:

#### Table Format (Default)

Displays tools in a beautiful Rich terminal table:

```bash
uv run mci list
```

Output:
```
🧩 Available Tools (3)
┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name        ┃ Source ┃ Description              ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ get_weather │ main   │ Get current weather      │
│ analyze     │ main   │ Analyze data             │
│ send_email  │ custom │ Send email notifications │
└─────────────┴────────┴──────────────────────────┘
```

#### JSON Format

Export tools to a timestamped JSON file:

```bash
uv run mci list --format json
```

Creates a file like `tools_20241029_143022.json` with structure:

```json
{
  "timestamp": "2024-10-29T14:30:22Z",
  "mci_file": "/path/to/mci.json",
  "filters_applied": [],
  "total": 3,
  "tools": [
    {
      "name": "get_weather",
      "source": "main",
      "description": "Get current weather"
    }
  ]
}
```

#### YAML Format

Export tools to a timestamped YAML file:

```bash
uv run mci list --format yaml
```

Creates a file like `tools_20241029_143022.yaml`.

### Filtering Tools

The `list` command uses the same filtering logic as the `run` command, ensuring consistency between what is listed and what will be available when running MCP servers.

#### Filter by Tags

Include tools with specific tags (OR logic):

```bash
# Show only tools tagged with 'api' OR 'database'
uv run mci list --filter tags:api,database
```

#### Filter by Tool Names

Include or exclude specific tools by name:

```bash
# Include only specific tools
uv run mci list --filter only:get_weather,analyze

# Exclude specific tools
uv run mci list --filter except:deprecated_tool
```

#### Filter by Toolsets

Include tools from specific toolsets:

```bash
uv run mci list --filter toolsets:custom,external
```

### Verbose Mode

Verbose mode shows additional tool metadata including tags, parameters, and execution type:

```bash
uv run mci list --verbose
```

Output:
```
🧩 Available Tools (2):

get_weather (main)
├── Description: Get current weather for a location
├── Tags: [api, data, weather]
├── Execution: text
└── Parameters: location (string), units (string) (optional)

analyze (main)
├── Description: Analyze data
├── Tags: [data, ml]
├── Execution: cli
└── Parameters: dataset (string), model (string) (optional)
```

### Combining Options

You can combine filtering, output format, and verbose mode:

```bash
# Export filtered tools to JSON with verbose metadata
uv run mci list --filter tags:api --format json --verbose

# List only production tools in verbose table format
uv run mci list --filter tags:production --verbose
```

### Use Cases

- **Preview Tools**: See what tools are available before running an MCP server
- **Debugging**: Verify tool loading and filtering logic
- **Documentation**: Export tool lists for documentation or sharing
- **Validation**: Check that toolsets are loaded correctly
- **Filtering**: Test filter specifications before using them with `mci run`

* * *

## Add Toolset References with `mci add`

The `mci add` command adds toolset references to your MCI schema files. It supports optional filtering and automatically preserves the original file format (JSON stays JSON, YAML stays YAML).

### Basic Usage

```bash
# Add a toolset without filter
uv run mci add weather-tools

# Add a toolset with "only" filter
uv run mci add analytics --filter=only:Tool1,Tool2

# Add a toolset with "tags" filter
uv run mci add api-tools --filter=tags:api,database

# Add to a custom file
uv run mci add weather-tools --path=custom.mci.json
```

### Filter Types

The `add` command supports the same filter types as the MCI schema:

#### Only Filter

Include only specific tools from the toolset:

```bash
uv run mci add analytics --filter=only:SummarizeData,AnalyzeSentiment
```

This adds to your schema:

```json
{
  "toolsets": [
    {
      "name": "analytics",
      "filter": "only",
      "filterValue": "SummarizeData,AnalyzeSentiment"
    }
  ]
}
```

#### Except Filter

Exclude specific tools from the toolset:

```bash
uv run mci add weather-tools --filter=except:DeprecatedTool
```

#### Tags Filter

Include tools with specific tags:

```bash
uv run mci add api-tools --filter=tags:api,database
```

#### WithoutTags Filter

Exclude tools with specific tags:

```bash
uv run mci add internal-tools --filter=withoutTags:deprecated,experimental
```

### Format Preservation

The `add` command automatically detects and preserves your file format:

**JSON files** stay JSON:
```bash
# Before (mci.json)
{
  "toolsets": []
}

# Run: mci add weather-tools
# After (still JSON)
{
  "toolsets": ["weather-tools"]
}
```

**YAML files** stay YAML:
```bash
# Before (mci.yaml)
toolsets: []

# Run: mci add weather-tools
# After (still YAML)
toolsets:
  - weather-tools
```

### Duplicate Handling

The `add` command handles duplicates gracefully:

- **Adding an existing toolset**: Updates it with the new filter (if provided)
- **No duplicates created**: Each toolset appears only once in the array

Example:

```bash
# Initial state: toolsets: ["weather-tools"]
uv run mci add weather-tools --filter=tags:api

# Result: toolsets updated, not duplicated
# toolsets: [{"name": "weather-tools", "filter": "tags", "filterValue": "api"}]
```

### Auto-discovery

The `add` command automatically finds your MCI file:

1. Looks for `mci.json` in the current directory
2. Falls back to `mci.yaml` if JSON not found
3. Falls back to `mci.yml` if YAML not found

To use a custom path:

```bash
uv run mci add weather-tools --path=./config/custom.mci.json
```

### Use Cases

- **Add toolsets from library**: Quickly add pre-built toolsets from your `./mci` directory
- **Configure filtering**: Add toolsets with specific tool subsets
- **Organize tools**: Group related tools into toolsets for better organization
- **Update existing references**: Modify filters on existing toolset references

* * *

## Validate MCI Schemas with `mci validate`

The `mci validate` command checks MCI schema files for correctness using mci-py's built-in validation engine. It provides comprehensive validation of schema structure, types, and references, plus additional checks for toolset files and MCP command availability.

### Basic Usage

```bash
# Validate default mci.json/mci.yaml in current directory
uv run mci validate

# Validate a specific file
uv run mci validate --file custom.mci.json

# Validate with environment variables
uv run mci validate -e API_KEY=test123 -e BASE_URL=https://api.example.com
```

### What Gets Validated

The validate command performs two levels of checks:

#### 1. Schema Validation (Errors)

These are critical issues that prevent the schema from being used. Validation uses MCIClient from mci-py, which checks:

- **Schema structure**: Correct JSON/YAML syntax
- **Required fields**: Presence of `schemaVersion` and `metadata`
- **Data types**: Field values match expected types
- **Tool definitions**: Valid execution types and input schemas
- **Toolset references**: Referenced toolsets must exist in the `mci/` directory (validated by MCIClient)
- **MCP server definitions**: Valid server configurations

If any errors are found, validation fails and the schema cannot be used.

#### 2. Additional Checks (Warnings)

These are non-critical issues that don't prevent the schema from being used:

- **Missing MCP commands**: Checks if MCP server commands are available in PATH
- Commands not in PATH generate warnings but don't fail validation

### Validation Output

#### Valid Schema

```bash
uv run mci validate
```

Output:
```
╭───────────── Validation Successful ──────────────╮
│ ✅ Schema is valid!                              │
│                                                  │
│ File: /path/to/mci.json                          │
╰──────────────────────────────────────────────────╯
```

#### Schema with Errors

```bash
uv run mci validate --file invalid.mci.json
```

Output:
```
╭────────── Schema Validation Failed ──────────╮
│ ❌ Validation Errors                          │
│                                               │
│ 1. Failed to load schema: Missing required   │
│    field 'schemaVersion'                      │
│                                               │
╰───────────────────────────────────────────────╯

💡 Fix the errors above and run 'mci validate' again
```

#### Schema with Warnings

```bash
uv run mci validate
```

Output:
```
╭──────────────────── Warnings ─────────────────────╮
│ ⚠️  Validation Warnings                            │
│                                                   │
│ 1. MCP server command not found in PATH:         │
│    weather-mcp (server: weather_server)           │
│    💡 Install the command or ensure it's in PATH  │
│                                                   │
╰───────────────────────────────────────────────────╯

╭───────────── Validation Successful ──────────────╮
│ ✅ Schema is valid!                              │
│                                                  │
│ File: /path/to/mci.json                          │
╰──────────────────────────────────────────────────╯
```

### Environment Variables

Use the `-e` or `--env` flag to provide environment variables needed for template substitution:

```bash
# Single environment variable
uv run mci validate -e API_KEY=your-api-key

# Multiple environment variables
uv run mci validate \
  -e API_KEY=your-api-key \
  -e BASE_URL=https://api.example.com \
  -e PROJECT_ROOT=/path/to/project
```

Environment variables are merged with `os.environ`, so you can also set them in your shell:

```bash
export API_KEY=your-api-key
uv run mci validate
```

### Auto-Discovery

When `--file` is not specified, the validate command searches for:
1. `mci.json` (first priority)
2. `mci.yaml` or `mci.yml` (if JSON not found)

in the current directory.

### Common Validation Errors

#### Missing Required Fields

```json
{
  "tools": []  // Missing schemaVersion!
}
```

Error:
```
Failed to load schema: Missing required field 'schemaVersion'
```

#### Invalid Toolset Reference

```json
{
  "schemaVersion": "1.0",
  "metadata": { "name": "Test" },
  "tools": [],
  "toolsets": ["nonexistent"]  // No file at mci/nonexistent.mci.json
}
```

Error:
```
Toolset not found: nonexistent. Looked for directory or file with .mci.json/.mci.yaml/.mci.yml extension in ./mci
```

#### Invalid JSON/YAML Syntax

```json
{
  "schemaVersion": "1.0"
  "metadata": {}  // Missing comma!
}
```

Error:
```
Failed to load schema: Invalid JSON syntax
```

### Use Cases

- **Pre-deployment validation**: Verify schemas before deploying
- **CI/CD integration**: Add validation to your build pipeline
- **Development workflow**: Check schemas after making changes
- **Troubleshooting**: Get detailed error messages when schemas don't load
- **Team collaboration**: Ensure all team members use valid schemas

### Exit Codes

- `0`: Schema is valid (warnings are OK)
- `1`: Validation failed with errors or file not found

### Integration with mci-py

The validate command leverages mci-py's built-in validation:

```python
from mci.core.config import MCIConfig

# Programmatic validation (same as CLI)
config = MCIConfig()
is_valid, error = config.validate_schema("mci.json")

if not is_valid:
    print(f"Validation error: {error}")
```

All validation logic is provided by `MCIClient` from mci-py, ensuring consistency between the CLI and programmatic usage.

* * *

All further development stages build on this foundational structure:
- **Stage 1**: ✅ Project Setup & Core Dependencies
- **Stage 2**: ✅ Configuration & File Discovery
- **Stage 3**: ✅ CLI Command: `mci install`
- **Stage 4**: ✅ MCI-PY Integration & Tool Loading
- **Stage 5**: ✅ CLI Command: `mci list`
- **Stage 6**: ✅ CLI Command: `mci validate`
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

## MCP Server Creation Infrastructure

The MCI CLI provides infrastructure for creating MCP (Model Context Protocol) servers that dynamically serve tools from MCI schemas. This allows you to expose MCI tools via the MCP protocol, making them available to MCP-compatible clients.

### Overview

The MCP server creation system consists of three main components:

1. **MCIToolConverter**: Converts MCI tool definitions to MCP tool format
2. **MCPServerBuilder**: Creates and configures MCP servers with MCI tools
3. **ServerInstance**: Manages server lifecycle and delegates execution to MCIClient

### Key Features

- **Dynamic Tool Loading**: Tools are loaded from MCI schemas using MCIClient and kept in memory
- **Automatic Conversion**: MCI tools are automatically converted to MCP-compatible tool definitions
- **Execution Delegation**: Tool execution is delegated back to MCIClient, ensuring consistency
- **Flexible Filtering**: Use MCIClient's filtering capabilities to selectively expose tools
- **MCP Protocol Compliance**: Full support for MCP tool listing and execution protocols

### Architecture

```
MCI Schema → MCIClient → MCPServerBuilder → MCP Server → STDIO
                ↓              ↓                ↓
            Tools loaded   Converted      Tool execution
            from schema    to MCP format  via MCIClient
```

### Usage Example

```python
from mcipy import MCIClient
from mci.core.mcp_server import MCPServerBuilder, ServerInstance

# Step 1: Load MCI schema
mci_client = MCIClient(schema_file_path="mci.json")
tools = mci_client.tools()

# Step 2: Create MCP server
builder = MCPServerBuilder(mci_client)
server = await builder.create_server("my-mci-server", "1.0.0")

# Step 3: Register tools
await builder.register_all_tools(server, tools)

# Step 4: Create and start server instance
instance = ServerInstance(server, mci_client)
await instance.start(stdio=True)  # Runs server on STDIO
```

### Tool Conversion

MCI tools are automatically converted to MCP tool format:

**MCI Tool:**
```json
{
  "name": "greet",
  "description": "Greet a person by name",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"}
    }
  },
  "execution": {
    "type": "text",
    "text": "Hello, {{props.name}}!"
  }
}
```

**MCP Tool (after conversion):**
```python
types.Tool(
    name="greet",
    description="Greet a person by name",
    inputSchema={
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
)
```

### Filtering Tools

You can use MCIClient's filtering methods to selectively expose tools:

```python
# Expose only API-related tools
api_tools = mci_client.tags(["api"])
await builder.register_all_tools(server, api_tools)

# Expose specific tools by name
specific_tools = mci_client.only(["get_weather", "get_forecast"])
await builder.register_all_tools(server, specific_tools)

# Exclude certain tools
safe_tools = mci_client.without(["dangerous_operation"])
await builder.register_all_tools(server, safe_tools)
```

### Tool Execution

When an MCP client calls a tool, the server:

1. Receives the tool call via MCP protocol
2. Delegates execution to `MCIClient.execute()`
3. Converts the result to MCP TextContent format
4. Returns the response to the client

This ensures that all execution logic remains in MCIClient, avoiding duplication.

### Server Lifecycle

The `ServerInstance` class manages the server lifecycle:

- **Startup**: Initialize MCP protocol handlers and prepare for requests
- **Runtime**: Handle tool listing and execution requests
- **Shutdown**: Clean up resources (handled by async context manager)

### Advanced Features

For advanced MCP server features, including:

- Lifespan management with resource initialization/cleanup
- Structured output support
- Direct `CallToolResult` returns with `_meta` field
- Low-level server API usage

See [mcp-server-docs.md](mcp-server-docs.md) for comprehensive documentation.

### Integration with CLI

The MCP server infrastructure is designed to be used by the `mci run` command (Stage 9), which will:

1. Load tools from an MCI schema file
2. Create an MCP server with those tools
3. Start the server on STDIO
4. Handle incoming MCP protocol requests

This allows users to instantly turn any MCI schema into a running MCP server.

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For the full implementation plan, see [PLAN.md](PLAN.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
