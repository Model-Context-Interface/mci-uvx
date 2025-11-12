# MCI CLI Tool - Implementation Plan

## Overview

This document outlines the implementation plan for the **MCI CLI Tool** (`mci-uvx`), a uvx-based command-line interface for managing MCI (Model Context Interface) schemas and dynamically running MCP servers. The implementation is divided into 10 logical stages, building from core dependencies to full CLI functionality.

## Recommended Packages

### Core Dependencies
- **[click](https://github.com/pallets/click)** (15.5k+ stars) - Modern Python CLI framework with excellent developer experience
- **[rich](https://github.com/Textualize/rich)** (48k+ stars) - Beautiful terminal formatting, tables, and progress bars
- **[pyyaml](https://github.com/yaml/pyyaml)** (2.5k+ stars) - YAML parsing and serialization
- **[mci-py](https://github.com/Model-Context-Interface/mci-py)** - MCI Python adapter for schema parsing and tool execution (includes Pydantic models)
- **[mcp](https://github.com/modelcontextprotocol/python-sdk)** - Official Python SDK for Model Context Protocol

### Development & Testing
- **pytest** - Testing framework (already in dependencies)
- **pytest-asyncio** - Async test support for MCP integration
- **pytest-mock** - Mocking utilities for tests
- **pytest-cov** - Coverage reporting

### Notes on Dependencies

- **Pydantic is NOT needed as a separate dependency** - it's already included in `mci-py` which provides all necessary Pydantic models for tool definitions, schemas, and validation
- The CLI tool should use mci-py's models directly rather than creating new ones

---

## Stage 1: Project Setup & Core Dependencies

### Goal
Set up project structure, install dependencies, and configure build system.

### Directories to Create
```
src/mci/
├── __init__.py          # Package initialization
├── mci.py               # Main CLI entry point
├── cli/                 # CLI command modules
│   └── __init__.py
├── core/                # Core business logic
│   └── __init__.py
└── utils/               # Utility functions
    └── __init__.py
```

### Files to Create/Modify
- **pyproject.toml** - Add core dependencies (click, rich, pyyaml, mci-py, mcp) - Note: Pydantic not needed separately as it's in mci-py
- **src/mci/__init__.py** - Export main CLI entry point
- **src/mci/mci.py** - Basic Click application structure
- **src/mci/cli/__init__.py** - CLI command group initialization
- **src/mci/core/__init__.py** - Core module initialization
- **src/mci/utils/__init__.py** - Utilities initialization

### Classes/Functions
- `main()` in `mci.py` - Main CLI entry point with Click group

### Tests

#### Unit Tests
- `tests/unit/test_cli_init.py` - Test CLI initialization
- `tests/unit/test_imports.py` - Test package imports

#### Feature Tests
- `tests/test_cli_help.py` - Test CLI help output and command discovery

#### Manual Tests
None for this stage.

### Success Criteria
- [ ] All dependencies installed via `uv sync`
- [ ] `uv run mci --help` displays help text
- [ ] All tests pass with `make test`
- [ ] Code passes linting with `make lint`

---

## Stage 2: Configuration & File Discovery

### Goal
Implement logic to find and load MCI configuration files (JSON/YAML) using mci-py's MCIClient for validation.

### Directories to Create
```
src/mci/core/
├── config.py            # Configuration loading and validation
└── file_finder.py       # File discovery logic
```

### Files to Create/Modify
- **src/mci/core/config.py** - Config class for managing MCI file paths, validation using MCIClient
- **src/mci/core/file_finder.py** - Logic to find mci.json/mci.yaml in directory
- **src/mci/utils/validation.py** - File validation utilities

### Classes/Functions
- `MCIFileFinder` class with methods:
  - `find_mci_file(directory: str = ".") -> str | None` - Find mci.json or mci.yaml
  - `validate_file_exists(path: str) -> bool` - Check if file exists
  - `get_file_format(path: str) -> str` - Determine if JSON or YAML
- `MCIConfig` class with methods:
  - `load(file_path: str) -> MCIClient` - Load and parse MCI file using MCIClient in try block
  - `validate_schema(file_path: str) -> tuple[bool, str]` - Validate using MCIClient, return (is_valid, error_message)

### Implementation Notes
- **MCI schema validation is already built into `mci-py`**, so use MCIClient in a try block to parse the file
- If MCIClient initialization fails, catch the exception and extract error details for user-friendly messages
- This approach leverages mci-py's built-in validation instead of duplicating validation logic

### Tests

#### Unit Tests
- `tests/unit/core/test_file_finder.py`
  - `test_find_json_file()` - Find mci.json in directory
  - `test_find_yaml_file()` - Find mci.yaml in directory
  - `test_find_priority_json_over_yaml()` - JSON takes priority
  - `test_no_file_found()` - Return None when no file exists
- `tests/unit/core/test_config.py`
  - `test_load_valid_schema_with_mciclient()` - Load valid schema using MCIClient
  - `test_invalid_schema_caught_by_mciclient()` - MCIClient catches invalid schema
  - `test_missing_file_error()` - Handle missing file errors
  - `test_error_message_extraction()` - Extract user-friendly error messages from MCIClient exceptions

#### Feature Tests
- `tests/test_config_loading.py` - Test end-to-end config loading with sample files using MCIClient

#### Manual Tests
None for this stage.

### Success Criteria
- [ ] Can find mci.json and mci.yaml files
- [ ] Can load and validate files using MCIClient
- [ ] Proper error handling using MCIClient's validation
- [ ] User-friendly error messages extracted from MCIClient exceptions
- [ ] All tests pass

---

## Stage 3: CLI Command: `mcix install`

### Goal
Implement the `install` command to initialize MCI project structure.

### Directories to Create
```
src/mci/cli/
├── install.py           # Install command implementation
└── templates/           # Template files for initialization
    ├── mci_json_template.py
    ├── mci_yaml_template.py
    └── example_template.py
```

### Files to Create/Modify
- **src/mci/cli/install.py** - Install command implementation
- **src/mci/cli/templates/mci_json_template.py** - Template for mci.json
- **src/mci/cli/templates/mci_yaml_template.py** - Template for mci.yaml
- **src/mci/cli/templates/example_template.py** - Template for example.mci.json
- **src/mci/mci.py** - Register install command

### Classes/Functions
- `install_command(yaml: bool = False)` - Click command for `mcix install`
- `create_mci_file(format: str) -> None` - Create main MCI file
- `create_mci_directory() -> None` - Create ./mci directory structure
- `create_example_toolset() -> None` - Create example.mci.json

### Initial MCI File Structure

The `mci.json` template should create this starting structure:

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

The `mci.yaml` template should have the equivalent YAML structure.

### Tests

#### Unit Tests
- `tests/unit/cli/test_install.py`
  - `test_create_json_file()` - Create mci.json file
  - `test_create_yaml_file()` - Create mci.yaml file with --yaml flag
  - `test_file_already_exists()` - Handle existing file gracefully
  - `test_create_mci_directory()` - Create ./mci directory
  - `test_create_gitignore()` - Create .gitignore with ./mcp entry

#### Feature Tests
- `tests/test_install_command.py` - Test full install workflow in temp directory

#### Manual Tests
- `testsManual/test_install.py` - Run install in real directory, verify all files

### Success Criteria
- [ ] `uvx mcix install` creates mci.json with proper structure
- [ ] `uvx mcix install --yaml` creates mci.yaml
- [ ] Creates ./mci directory with example.mci.json
- [ ] Creates ./mci/.gitignore with ./mcp entry
- [ ] Handles existing files gracefully
- [ ] All tests pass

---

## Stage 4: MCI-PY Integration & Tool Loading

### Goal
Integrate mci-py library for loading and managing MCI tools using MCIClient.

### Directories to Create
```
src/mci/core/
├── mci_client.py        # Wrapper around mci-py MCIClient
└── tool_manager.py      # Tool management and filtering logic
```

### Files to Create/Modify
- **src/mci/core/mci_client.py** - Wrapper for MCIClient with error handling
- **src/mci/core/tool_manager.py** - Tool filtering and listing logic
- **src/mci/utils/error_handler.py** - Error handling utilities

### Implementation Notes

**IMPORTANT: Use MCIClient from mci-py for all tool loading and filtering operations.**

- The `MCIClient` class from mci-py already provides all necessary functionality:
  - Loading tools from schema files (JSON/YAML)
  - Built-in filtering methods: `only()`, `except_()`, `tags()`, `withoutTags()`
  - Environment variable templating
  - Pydantic models for tool definitions
- **Check mci-docs** for full MCIClient API reference and usage examples
- Do NOT reimplement filtering logic - use MCIClient's built-in methods
- The wrapper should primarily handle CLI-specific error handling and formatting
- MCIClient already includes all needed Pydantic models for validation

### Classes/Functions
- `MCIClientWrapper` class with methods:
  - `__init__(file_path: str, env_vars: dict = None)` - Initialize MCIClient
  - `get_tools() -> list[Tool]` - Get all tools using MCIClient.tools()
  - `filter_only(tool_names: list[str]) -> list[Tool]` - Use MCIClient.only()
  - `filter_except(tool_names: list[str]) -> list[Tool]` - Use MCIClient.except_()
  - `filter_tags(tags: list[str]) -> list[Tool]` - Use MCIClient.tags()
  - `filter_without_tags(tags: list[str]) -> list[Tool]` - Use MCIClient.withoutTags()
- `ToolManager` class with methods:
  - `apply_filter_spec(client: MCIClient, filter_spec: str) -> list[Tool]`
  - `parse_filter_spec(filter_spec: str) -> tuple[str, list[str]]` - Parse CLI filter string

### Tests

#### Unit Tests
- `tests/unit/core/test_mci_client.py`
  - `test_load_valid_schema()` - Load schema successfully using MCIClient
  - `test_invalid_schema_error()` - Handle invalid schema from MCIClient
  - `test_missing_file_error()` - Handle missing file
  - `test_env_var_substitution()` - Test environment variable templating
  - `test_use_mciclient_filtering()` - Verify MCIClient filter methods are used
- `tests/unit/core/test_tool_manager.py`
  - `test_parse_filter_spec()` - Parse CLI filter specification
  - `test_apply_filter_only()` - Apply "only" filter via MCIClient
  - `test_apply_filter_except()` - Apply "except" filter via MCIClient
  - `test_apply_filter_tags()` - Apply "tags" filter via MCIClient

#### Feature Tests
- `tests/test_mci_integration.py` - Test mci-py integration with sample schemas

#### Manual Tests
- `testsManual/test_tool_loading.py` - Load real MCI files and display tools

### Success Criteria
- [ ] Uses MCIClient from mci-py for all operations
- [ ] Leverages MCIClient's built-in filtering methods
- [ ] Environment variable templating works via MCIClient
- [ ] Proper error messages for invalid schemas
- [ ] No reimplementation of mci-py functionality
- [ ] All tests pass

---

## Stage 5: CLI Command: `mcix list`

### Goal
Implement the `list` command to display available tools.

### Implementation Notes

**IMPORTANT: The list command should use the same modules that will be used in the run command.**

- The `list` command is designed to test and preview what tools the `run` command will return
- Both commands should share the same tool loading and filtering logic
- This ensures consistency between what `list` shows and what `run` actually provides
- Use the same MCIClient wrapper and filtering logic that `run` will use

### Directories to Create
```
src/mci/cli/
├── list.py              # List command implementation
└── formatters/          # Output formatters
    ├── __init__.py
    ├── table_formatter.py
    ├── json_formatter.py
    └── yaml_formatter.py
```

### Files to Create/Modify
- **src/mci/cli/list.py** - List command implementation (reuse tool loading from Stage 4)
- **src/mci/cli/formatters/table_formatter.py** - Rich table formatter
- **src/mci/cli/formatters/json_formatter.py** - JSON output formatter
- **src/mci/cli/formatters/yaml_formatter.py** - YAML output formatter
- **src/mci/utils/timestamp.py** - Timestamp generation utilities
- **src/mci/mci.py** - Register list command

### Classes/Functions
- `list_command(file: str, filter: str, format: str, verbose: bool)` - Click command
- `TableFormatter` class with methods:
  - `format(tools: list[Tool], verbose: bool) -> str`
  - `format_verbose(tools: list[Tool]) -> str`
- `JSONFormatter` class with methods:
  - `format_to_file(tools: list[Tool], verbose: bool) -> str` - Returns filename
- `YAMLFormatter` class with methods:
  - `format_to_file(tools: list[Tool], verbose: bool) -> str` - Returns filename
- `generate_timestamp_filename(format: str) -> str` - Generate tools_YYYYMMDD_HHMMSS.{format}

### Tests

#### Unit Tests
- `tests/unit/cli/test_list.py`
  - `test_list_default_format()` - Default table format
  - `test_list_json_format()` - JSON file output
  - `test_list_yaml_format()` - YAML file output
  - `test_list_with_filter()` - Apply filters
  - `test_list_verbose()` - Verbose output
  - `test_list_uses_same_loading_as_run()` - Verify shared logic with run command
- `tests/unit/cli/formatters/test_table_formatter.py`
  - `test_basic_table()` - Basic table output
  - `test_verbose_table()` - Verbose table with parameters
- `tests/unit/cli/formatters/test_json_formatter.py`
  - `test_json_output_structure()` - Verify JSON structure
  - `test_timestamp_in_json()` - Verify timestamp field
- `tests/unit/cli/formatters/test_yaml_formatter.py`
  - `test_yaml_output_structure()` - Verify YAML structure

#### Feature Tests
- `tests/test_list_command.py` - Test full list command with various options

#### Manual Tests
- `testsManual/test_list_output.py` - Run list command, verify table output visually

### Success Criteria
- [ ] `uvx mcix list` displays table of tools
- [ ] `uvx mcix list --format=json` creates timestamped JSON file
- [ ] `uvx mcix list --format=yaml` creates timestamped YAML file
- [ ] `uvx mcix list --verbose` shows detailed tool info
- [ ] `uvx mcix list --filter=tags:Tag1,Tag2` filters correctly
- [ ] Uses same tool loading/filtering logic as run command
- [ ] Beautiful output with Rich tables
- [ ] All tests pass

---

## Stage 6: CLI Command: `mcix validate`

### Goal
Implement the `validate` command to check MCI schema correctness using mci-py's built-in validation.

### Implementation Notes

**IMPORTANT: Use mci-py's built-in validation since it already validates the schema.**

- mci-py's `MCIClient` performs comprehensive schema validation during initialization
- Leverage this built-in validation instead of reimplementing validation logic
- Additional checks (toolset file existence, MCP command availability) can be added as warnings
- Use try/except with MCIClient to catch validation errors

### Directories to Create
```
src/mci/core/
└── validator.py         # Schema validation logic using mci-py
```

### Files to Create/Modify
- **src/mci/core/validator.py** - Schema validation using MCIClient
- **src/mci/cli/validate.py** - Validate command implementation
- **src/mci/utils/error_formatter.py** - Format validation errors nicely
- **src/mci/mci.py** - Register validate command

### Classes/Functions
- `validate_command(file: str)` - Click command for `mcix validate`
- `MCIValidator` class with methods:
  - `validate_schema(file_path: str) -> ValidationResult` - Validate using MCIClient
  - `check_toolset_files() -> list[ValidationWarning]` - Check toolset file existence
  - `check_mcp_commands() -> list[ValidationWarning]` - Check MCP commands in PATH
- `ValidationResult` dataclass with fields:
  - `errors: list[ValidationError]` - From MCIClient exceptions
  - `warnings: list[ValidationWarning]` - Additional checks
  - `is_valid: bool`

### Tests

#### Unit Tests
- `tests/unit/core/test_validator.py`
  - `test_valid_schema_via_mciclient()` - Validate correct schema using MCIClient
  - `test_invalid_schema_caught_by_mciclient()` - MCIClient catches invalid schema
  - `test_missing_required_field()` - Detect missing fields via MCIClient
  - `test_invalid_toolset_reference()` - Detect missing toolsets (warning)
  - `test_missing_mcp_command()` - Detect missing MCP commands (warning)
  - `test_warning_collection()` - Collect warnings without failing
- `tests/unit/cli/test_validate.py`
  - `test_validate_valid_file()` - Validate successful schema
  - `test_validate_invalid_file()` - Report validation errors from MCIClient

#### Feature Tests
- `tests/test_validate_command.py` - Test validation with various schema files

#### Manual Tests
- `testsManual/test_validate.py` - Run validate on real schemas, check output

### Success Criteria
- [ ] `uvx mcix validate` checks default mci.json/mci.yaml using MCIClient
- [ ] `uvx mcix validate --file=custom.mci.json` checks custom file
- [ ] Uses MCIClient for schema validation (no reimplementation)
- [ ] Shows warnings for missing toolsets and MCP commands
- [ ] Beautiful, color-coded output using Rich
- [ ] All tests pass

---

## Stage 7: CLI Command: `mcix add`

### Goal
Implement the `add` command to add toolset references to MCI files.

### Directories to Create
```
src/mci/core/
└── schema_editor.py     # Schema file editing logic
```

### Files to Create/Modify
- **src/mci/core/schema_editor.py** - Edit MCI schema files programmatically
- **src/mci/cli/add.py** - Add command implementation
- **src/mci/mci.py** - Register add command

### Classes/Functions
- `add_command(toolset_name: str, filter: str, path: str)` - Click command
- `SchemaEditor` class with methods:
  - `load_schema(file_path: str) -> dict`
  - `add_toolset(toolset_name: str, filter_type: str = None, filter_value: str = None) -> None`
  - `save_schema(file_path: str) -> None`
  - `preserve_format() -> str` - Remember if JSON or YAML
- `parse_add_filter(filter_spec: str) -> tuple[str, str]` - Parse filter specification

### Tests

#### Unit Tests
- `tests/unit/core/test_schema_editor.py`
  - `test_add_simple_toolset()` - Add toolset without filter
  - `test_add_toolset_with_filter()` - Add toolset with filter
  - `test_add_duplicate_toolset()` - Handle duplicate gracefully
  - `test_preserve_json_format()` - Save back as JSON
  - `test_preserve_yaml_format()` - Save back as YAML
- `tests/unit/cli/test_add.py`
  - `test_add_toolset_command()` - Test add command
  - `test_add_with_filter()` - Test add with filter option
  - `test_add_to_custom_path()` - Test --path option

#### Feature Tests
- `tests/test_add_command.py` - Test full add workflow

#### Manual Tests
- `testsManual/test_add.py` - Add toolsets to real files, verify changes

### Success Criteria
- [ ] `uvx mcix add weather-tools` adds toolset to mci.json
- [ ] `uvx mcix add analytics --filter=only:Tool1,Tool2` adds with filter
- [ ] `uvx mcix add toolset --path=custom.mci.json` modifies custom file
- [ ] Preserves file format (JSON stays JSON, YAML stays YAML)
- [ ] Handles duplicates gracefully
- [ ] All tests pass

---

## Stage 8: MCP Server Creation Infrastructure

### Goal
Set up infrastructure for creating MCP servers (not connecting to them) that can serve MCI tools.

### Implementation Notes

**IMPORTANT: This stage is about CREATING MCP servers.**

- We create an MCP server that will serve tools from MCI schemas
- The server will expose MCI tools as MCP tools to MCP clients
- Check **mcp-server-docs.md** for examples of how to create MCP servers (to be added later)
- Use the official `mcp` Python SDK to create the server
- The server should handle tool listing and tool execution requests via MCP protocol

### Directories to Create
```
src/mci/core/
├── mcp_server.py        # MCP server creation and management
└── tool_converter.py    # Convert MCI tools to MCP tool format
```

### Files to Create/Modify
- **src/mci/core/mcp_server.py** - Create and configure MCP server instances
- **src/mci/core/tool_converter.py** - Convert MCI Tool objects to MCP tool definitions
- **pyproject.toml** - Add pytest-asyncio for async tests

### Classes/Functions
- `MCPServerBuilder` class with async methods:
  - `async create_server(name: str, version: str) -> Server` - Create MCP server instance
  - `async register_tool(server: Server, mci_tool: Tool) -> None` - Register MCI tool as MCP tool
  - `async register_all_tools(server: Server, tools: list[Tool]) -> None` - Register multiple tools
- `MCIToolConverter` class with methods:
  - `convert_to_mcp_tool(mci_tool: Tool) -> MCPTool` - Convert MCI Tool to MCP format
  - `convert_input_schema(mci_schema: dict) -> dict` - Convert inputSchema to MCP format
- `ServerInstance` class:
  - `start() -> None` - Start the MCP server
  - `stop() -> None` - Stop the MCP server
  - `handle_tool_call(name: str, arguments: dict) -> Any` - Delegate to MCI execution

### Tests

#### Unit Tests
- `tests/unit/core/test_mcp_server.py`
  - `test_create_server()` - Create MCP server instance
  - `test_register_single_tool()` - Register one MCI tool
  - `test_register_multiple_tools()` - Register multiple tools
  - `test_server_metadata()` - Verify server name and version
- `tests/unit/core/test_tool_converter.py`
  - `test_convert_mci_to_mcp_tool()` - Convert tool definition
  - `test_convert_input_schema()` - Convert inputSchema format
  - `test_preserve_tool_description()` - Ensure description is preserved

#### Feature Tests
- `tests/test_mcp_server_creation.py` - Test full MCP server creation workflow

#### Manual Tests
- `testsManual/test_mcp_server.py` - Create server, verify it can be queried

### Success Criteria
- [ ] Can create MCP server instances using `mcp` SDK
- [ ] Can register MCI tools as MCP tools
- [ ] Tool definitions properly converted to MCP format
- [ ] Server can handle tool listing requests
- [ ] Proper async handling
- [ ] All tests pass

---

## Stage 9: CLI Command: `mcix run` (STDIO Only)

### Goal
Implement the `run` command to launch MCP servers via STDIO that serve MCI tools.

### Implementation Notes

**IMPORTANT: Integration flow for the run command:**

1. **Fetch tools from MCI**: Use MCIClient (from Stage 4) to load tools from MCI schema
2. **Build MCP tools**: Convert MCI tools to MCP tool format (from Stage 8)
3. **Create MCP server**: Use the MCP server infrastructure (from Stage 8)
4. **Handle execution**: When a tool execution is requested via MCP, use MCI's execution logic

The `run` command creates a dynamic MCP server that:
- Loads MCI tools using MCIClient
- Converts them to MCP format
- Serves them via MCP protocol over STDIO
- Delegates execution back to MCI when tools are called

### Directories to Create
```
src/mci/core/
└── dynamic_server.py    # Dynamic MCP server creation from MCI schema
```

### Files to Create/Modify
- **src/mci/core/dynamic_server.py** - Create MCP server from MCI schema
- **src/mci/cli/run.py** - Run command implementation
- **src/mci/mci.py** - Register run command

### Classes/Functions
- `run_command(file: str, filter: str)` - Click command for `mcix run`
- `DynamicMCPServer` class with async methods:
  - `async create_from_mci_schema(schema_path: str, filter_spec: str = None) -> Server`
    - Load tools using MCIClient from Stage 4
    - Convert MCI tools to MCP format using Stage 8 converter
    - Register tools with MCP server from Stage 8
  - `async handle_tool_execution(name: str, arguments: dict) -> ToolResult`
    - Use MCIClient.execute() to run the tool
    - Return result in MCP format
  - `async start_stdio() -> None` - Start server on STDIO
- `run_server(schema_path: str, filter_spec: str) -> None` - Main run function

### Tests

#### Unit Tests
- `tests/unit/core/test_dynamic_server.py`
  - `test_create_server_from_schema()` - Create server from MCI schema
  - `test_load_tools_via_mciclient()` - Verify MCIClient is used to load tools
  - `test_convert_tools_to_mcp()` - Verify tools are converted to MCP format
  - `test_handle_execution_uses_mci()` - Verify MCI's execute() is used
- `tests/unit/cli/test_run.py`
  - `test_run_default_file()` - Run with default mci.json
  - `test_run_custom_file()` - Run with --file option
  - `test_run_with_filter()` - Run with --filter option

#### Feature Tests
- `tests/test_run_command.py` - Test full run command with mock MCP client

#### Manual Tests
- `testsManual/test_run_stdio.py` - Run actual MCP server, connect with MCP client

### Success Criteria
- [ ] `uvx mcix run` starts MCP server on STDIO
- [ ] Uses MCIClient to fetch tools from MCI schema
- [ ] Converts MCI tools to MCP tool format
- [ ] Server responds to MCP protocol requests (list_tools)
- [ ] Tool execution requests delegate to MCI's execute()
- [ ] `uvx mcix run --file=custom.mci.json` uses custom file
- [ ] `uvx mcix run --filter=tags:Tag1,Tag2` filters tools correctly
- [ ] Graceful shutdown on Ctrl+C
- [ ] All tests pass
- `testsManual/test_run_stdio.py` - Run actual MCP server, connect with MCP client

### Success Criteria
- [ ] `uvx mcix run` starts MCP server on STDIO
- [ ] `uvx mcix run --file=custom.mci.json` uses custom file
- [ ] `uvx mcix run --filter=tags:Tag1,Tag2` filters tools
- [ ] Server responds to MCP protocol requests
- [ ] Tools execute correctly via mci-py
- [ ] Graceful shutdown on Ctrl+C
- [ ] All tests pass

---

## Stage 10: Error Handling, Documentation & Final Polish

### Goal
Comprehensive error handling, user documentation, and final polish.

### Directories to Create
```
docs/
├── commands/            # Command documentation
│   ├── install.md
│   ├── list.md
│   ├── validate.md
│   ├── add.md
│   └── run.md
└── examples/            # Example MCI files
    ├── basic.mci.json
    ├── with-toolsets.mci.json
    └── with-mcp-servers.mci.json
```

### Files to Create/Modify
- **README.md** - Update with full usage documentation
- **docs/commands/*.md** - Detailed command documentation
- **docs/examples/*.mci.json** - Example configurations
- **src/mci/utils/error_handler.py** - Enhanced error handling
- **src/mci/utils/logging.py** - Logging utilities
- **All CLI commands** - Add comprehensive error handling

### Classes/Functions
- `ErrorHandler` class with methods:
  - `handle_mci_error(error: Exception) -> None` - Handle MCI-specific errors
  - `handle_file_error(error: Exception) -> None` - Handle file errors
  - `handle_validation_error(error: Exception) -> None` - Handle validation errors
  - `display_user_friendly_error(error: Exception) -> None` - Display errors nicely
- `setup_logging(verbose: bool) -> None` - Configure logging

### Tests

#### Unit Tests
- `tests/unit/utils/test_error_handler.py`
  - `test_handle_mci_client_error()` - Test MCI client error handling
  - `test_handle_file_not_found()` - Test file error handling
  - `test_handle_validation_error()` - Test validation error handling
  - `test_user_friendly_display()` - Test error display formatting
- `tests/unit/test_all_commands.py`
  - Integration tests for all commands with error scenarios

#### Feature Tests
- `tests/test_error_scenarios.py` - Test error handling end-to-end
- `tests/test_user_experience.py` - Test complete user workflows

#### Manual Tests
- `testsManual/test_all_features.py` - Complete manual test of all features
- `testsManual/test_error_messages.py` - Verify error messages are helpful

### Additional Tasks
- [ ] Update README.md with installation and usage instructions
- [ ] Create comprehensive command documentation
- [ ] Add example MCI files with comments
- [ ] Implement --verbose flag for debugging
- [ ] Add --version flag to show version
- [ ] Create helpful error messages for common mistakes
- [ ] Add progress indicators for long operations
- [ ] Create CONTRIBUTING.md for contributors
- [ ] Update .gitignore to exclude common temporary files

### Success Criteria
- [ ] All commands have comprehensive error handling
- [ ] User-friendly error messages guide users to solutions
- [ ] Complete documentation for all commands
- [ ] Example files demonstrate all features
- [ ] All tests pass with >90% coverage
- [ ] README is clear and comprehensive
- [ ] Code is well-documented with docstrings

---

## Testing Strategy Summary

### Test Distribution by Stage

Each stage includes three types of tests:

1. **Unit Tests** (tests/unit/) - Test individual functions and classes in isolation
2. **Feature Tests** (tests/) - Test complete features end-to-end
3. **Manual Tests** (testsManual/) - Manual verification for visual/interactive features

### Overall Testing Goals

- **Code Coverage**: Target 90%+ coverage across all modules
- **Test Count**: Approximately 150-200 total automated tests
- **Manual Tests**: 10-15 manual verification scripts
- **Test Organization**: Mimic src/ directory structure in tests/unit/

### Test Execution

```bash
# Run all automated tests
make test

# Run with coverage
make coverage

# Run specific test file
uv run pytest -s tests/test_list_command.py

# Run manual test
uv run python testsManual/test_run_stdio.py
```

---

## Implementation Order Rationale

The 10 stages are ordered to build incrementally:

1. **Stage 1-2**: Foundation - Set up infrastructure and configuration loading
2. **Stage 3**: First user-facing feature - Initialize projects
3. **Stage 4-5**: Core functionality - Load and display tools
4. **Stage 6-7**: Schema management - Validate and modify schemas
5. **Stage 8-9**: MCP integration - Connect and run MCP servers
6. **Stage 10**: Polish - Error handling and documentation

Each stage builds on previous stages, ensuring:
- Early feedback on core functionality
- Incremental complexity
- Testable milestones
- Working software at each stage

---

## Dependencies Between Stages

```
Stage 1 (Setup)
    ↓
Stage 2 (Config Loading)
    ↓
    ├─→ Stage 3 (Install Command)
    ├─→ Stage 4 (MCI-PY Integration)
    │       ↓
    │   Stage 5 (List Command)
    │       ↓
    │   Stage 6 (Validate Command)
    │       ↓
    │   Stage 7 (Add Command)
    │
    └─→ Stage 8 (MCP Setup)
            ↓
        Stage 9 (Run Command)
            ↓
        Stage 10 (Polish & Docs)
```

---

## Future Enhancements (Beyond 10 Stages)

These features are documented in PRD.md but not included in the initial 10 stages:

1. **Stage 11** (Future): `mcix run --port` for HTTP-based MCP servers
2. **Stage 12** (Future): `mci test` command to simulate tool execution
3. **Stage 13** (Future): Plugin system for custom commands
4. **Stage 14** (Future): Interactive mode with prompts
5. **Stage 15** (Future): Tool marketplace integration

---

## Success Metrics

The implementation is considered complete when:

- ✅ All 10 stages are implemented
- ✅ All commands from PRD.md work correctly
- ✅ Test coverage > 90%
- ✅ Documentation is comprehensive
- ✅ Code passes all linting checks
- ✅ Manual testing validates user experience
- ✅ Can be installed via `uvx mci` and used immediately

---

## Notes

- This plan focuses on **STDIO-based MCP servers** for the initial implementation
- HTTP-based MCP servers (--port option) are deferred to future enhancements
- Each stage should take 1-3 days for an experienced developer
- Total estimated time: 2-3 weeks for full implementation
- Emphasis on test-driven development throughout
- Use Rich library for beautiful terminal output
- Follow the project's existing code style and documentation standards
