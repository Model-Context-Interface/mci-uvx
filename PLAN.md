# MCI CLI Tool - Implementation Plan

## Overview

This document outlines the implementation plan for the **MCI CLI Tool** (`mci-uvx`), a uvx-based command-line interface for managing MCI (Model Context Interface) schemas and dynamically running MCP servers. The implementation is divided into 10 logical stages, building from core dependencies to full CLI functionality.

## Recommended Packages

### Core Dependencies
- **[click](https://github.com/pallets/click)** (15.5k+ stars) - Modern Python CLI framework with excellent developer experience
- **[rich](https://github.com/Textualize/rich)** (48k+ stars) - Beautiful terminal formatting, tables, and progress bars
- **[pyyaml](https://github.com/yaml/pyyaml)** (2.5k+ stars) - YAML parsing and serialization
- **[pydantic](https://github.com/pydantic/pydantic)** (20k+ stars) - Data validation and settings management
- **[mci-py](https://github.com/Model-Context-Interface/mci-py)** - MCI Python adapter for schema parsing and tool execution
- **[mcp](https://github.com/modelcontextprotocol/python-sdk)** - Official Python SDK for Model Context Protocol

### Development & Testing
- **pytest** - Testing framework (already in dependencies)
- **pytest-asyncio** - Async test support for MCP integration
- **pytest-mock** - Mocking utilities for tests
- **pytest-cov** - Coverage reporting

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
- **pyproject.toml** - Add core dependencies (click, rich, pyyaml, pydantic, mci-py, mcp)
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
Implement logic to find and load MCI configuration files (JSON/YAML).

### Directories to Create
```
src/mci/core/
├── config.py            # Configuration loading and validation
└── file_finder.py       # File discovery logic
```

### Files to Create/Modify
- **src/mci/core/config.py** - Config class for managing MCI file paths, validation
- **src/mci/core/file_finder.py** - Logic to find mci.json/mci.yaml in directory
- **src/mci/utils/validation.py** - File validation utilities

### Classes/Functions
- `MCIFileFinder` class with methods:
  - `find_mci_file(directory: str = ".") -> str | None` - Find mci.json or mci.yaml
  - `validate_file_exists(path: str) -> bool` - Check if file exists
  - `get_file_format(path: str) -> str` - Determine if JSON or YAML
- `MCIConfig` class with methods:
  - `load(file_path: str) -> dict` - Load and parse MCI file
  - `validate_schema(data: dict) -> bool` - Basic schema validation

### Tests

#### Unit Tests
- `tests/unit/core/test_file_finder.py`
  - `test_find_json_file()` - Find mci.json in directory
  - `test_find_yaml_file()` - Find mci.yaml in directory
  - `test_find_priority_json_over_yaml()` - JSON takes priority
  - `test_no_file_found()` - Return None when no file exists
- `tests/unit/core/test_config.py`
  - `test_load_json_config()` - Load valid JSON config
  - `test_load_yaml_config()` - Load valid YAML config
  - `test_invalid_json_syntax()` - Handle malformed JSON
  - `test_invalid_yaml_syntax()` - Handle malformed YAML

#### Feature Tests
- `tests/test_config_loading.py` - Test end-to-end config loading with sample files

#### Manual Tests
None for this stage.

### Success Criteria
- [ ] Can find mci.json and mci.yaml files
- [ ] Can load and parse both JSON and YAML formats
- [ ] Proper error handling for missing/invalid files
- [ ] All tests pass

---

## Stage 3: CLI Command: `mci install`

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
- `install_command(yaml: bool = False)` - Click command for `mci install`
- `create_mci_file(format: str) -> None` - Create main MCI file
- `create_mci_directory() -> None` - Create ./mci directory structure
- `create_example_toolset() -> None` - Create example.mci.json

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
- [ ] `uvx mci install` creates mci.json with proper structure
- [ ] `uvx mci install --yaml` creates mci.yaml
- [ ] Creates ./mci directory with example.mci.json
- [ ] Creates ./mci/.gitignore with ./mcp entry
- [ ] Handles existing files gracefully
- [ ] All tests pass

---

## Stage 4: MCI-PY Integration & Tool Loading

### Goal
Integrate mci-py library for loading and managing MCI tools.

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

### Classes/Functions
- `MCIClientWrapper` class with methods:
  - `__init__(file_path: str, env_vars: dict = None)`
  - `load_tools() -> list[Tool]` - Load all tools from schema
  - `apply_filters(filter_type: str, filter_value: str) -> list[Tool]`
- `ToolManager` class with methods:
  - `list_tools(client: MCIClientWrapper) -> list[ToolInfo]`
  - `filter_tools(tools: list[Tool], filter_spec: str) -> list[Tool]`
  - `parse_filter_spec(filter_spec: str) -> tuple[str, list[str]]`

### Tests

#### Unit Tests
- `tests/unit/core/test_mci_client.py`
  - `test_load_valid_schema()` - Load schema successfully
  - `test_invalid_schema_error()` - Handle invalid schema
  - `test_missing_file_error()` - Handle missing file
  - `test_env_var_substitution()` - Test environment variable templating
- `tests/unit/core/test_tool_manager.py`
  - `test_list_all_tools()` - List all available tools
  - `test_filter_by_tags()` - Filter tools by tags
  - `test_filter_only()` - Filter with "only" type
  - `test_filter_except()` - Filter with "except" type
  - `test_parse_filter_spec()` - Parse filter specification

#### Feature Tests
- `tests/test_mci_integration.py` - Test mci-py integration with sample schemas

#### Manual Tests
- `testsManual/test_tool_loading.py` - Load real MCI files and display tools

### Success Criteria
- [ ] Can load tools from MCI JSON/YAML files
- [ ] Environment variable templating works
- [ ] Filtering logic works correctly
- [ ] Proper error messages for invalid schemas
- [ ] All tests pass

---

## Stage 5: CLI Command: `mci list`

### Goal
Implement the `list` command to display available tools.

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
- **src/mci/cli/list.py** - List command implementation
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
- [ ] `uvx mci list` displays table of tools
- [ ] `uvx mci list --format=json` creates timestamped JSON file
- [ ] `uvx mci list --format=yaml` creates timestamped YAML file
- [ ] `uvx mci list --verbose` shows detailed tool info
- [ ] `uvx mci list --filter=tags:Tag1,Tag2` filters correctly
- [ ] Beautiful output with Rich tables
- [ ] All tests pass

---

## Stage 6: CLI Command: `mci validate`

### Goal
Implement the `validate` command to check MCI schema correctness.

### Directories to Create
```
src/mci/core/
└── validator.py         # Schema validation logic
```

### Files to Create/Modify
- **src/mci/core/validator.py** - Schema validation implementation
- **src/mci/cli/validate.py** - Validate command implementation
- **src/mci/utils/error_formatter.py** - Format validation errors nicely
- **src/mci/mci.py** - Register validate command

### Classes/Functions
- `validate_command(file: str)` - Click command for `mci validate`
- `MCIValidator` class with methods:
  - `validate_schema(file_path: str) -> ValidationResult`
  - `check_syntax() -> list[ValidationError]` - Check JSON/YAML syntax
  - `check_required_fields() -> list[ValidationError]` - Check required fields
  - `check_toolset_files() -> list[ValidationWarning]` - Check toolset file existence
  - `check_mcp_commands() -> list[ValidationWarning]` - Check MCP commands in PATH
- `ValidationResult` dataclass with fields:
  - `errors: list[ValidationError]`
  - `warnings: list[ValidationWarning]`
  - `is_valid: bool`

### Tests

#### Unit Tests
- `tests/unit/core/test_validator.py`
  - `test_valid_schema()` - Validate correct schema
  - `test_missing_required_field()` - Detect missing fields
  - `test_invalid_json_syntax()` - Detect syntax errors
  - `test_invalid_toolset_reference()` - Detect missing toolsets
  - `test_missing_mcp_command()` - Detect missing MCP commands
  - `test_warning_collection()` - Collect warnings without failing
- `tests/unit/cli/test_validate.py`
  - `test_validate_valid_file()` - Validate successful schema
  - `test_validate_invalid_file()` - Report validation errors

#### Feature Tests
- `tests/test_validate_command.py` - Test validation with various schema files

#### Manual Tests
- `testsManual/test_validate.py` - Run validate on real schemas, check output

### Success Criteria
- [ ] `uvx mci validate` checks default mci.json/mci.yaml
- [ ] `uvx mci validate --file=custom.mci.json` checks custom file
- [ ] Detects syntax errors, missing fields, invalid references
- [ ] Shows warnings for missing toolsets and MCP commands
- [ ] Beautiful, color-coded output using Rich
- [ ] All tests pass

---

## Stage 7: CLI Command: `mci add`

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
- [ ] `uvx mci add weather-tools` adds toolset to mci.json
- [ ] `uvx mci add analytics --filter=only:Tool1,Tool2` adds with filter
- [ ] `uvx mci add toolset --path=custom.mci.json` modifies custom file
- [ ] Preserves file format (JSON stays JSON, YAML stays YAML)
- [ ] Handles duplicates gracefully
- [ ] All tests pass

---

## Stage 8: MCP Server Integration Setup

### Goal
Set up infrastructure for running MCP servers via mci-py and mcp SDK.

### Directories to Create
```
src/mci/core/
├── mcp_manager.py       # MCP server management
└── server_runner.py     # Server execution logic
```

### Files to Create/Modify
- **src/mci/core/mcp_manager.py** - MCP server connection and management
- **src/mci/core/server_runner.py** - Logic to run MCP servers (STDIO/HTTP)
- **pyproject.toml** - Add pytest-asyncio for async tests

### Classes/Functions
- `MCPManager` class with async methods:
  - `async connect_stdio(command: str, args: list[str], env: dict) -> MCPClient`
  - `async connect_http(url: str, headers: dict) -> MCPClient`
  - `async list_tools(client: MCPClient) -> list[str]`
  - `async call_tool(client: MCPClient, name: str, **args) -> Any`
- `ServerRunner` class with async methods:
  - `async start_server(config: dict) -> MCPServerInstance`
  - `async stop_server(instance: MCPServerInstance) -> None`

### Tests

#### Unit Tests
- `tests/unit/core/test_mcp_manager.py`
  - `test_connect_stdio()` - Test STDIO connection (mocked)
  - `test_connect_http()` - Test HTTP connection (mocked)
  - `test_list_tools()` - Test tool listing
  - `test_call_tool()` - Test tool execution
- `tests/unit/core/test_server_runner.py`
  - `test_start_stdio_server()` - Start server with STDIO
  - `test_start_http_server()` - Start server with HTTP
  - `test_stop_server()` - Stop running server

#### Feature Tests
- `tests/test_mcp_integration.py` - Test MCP integration with mock server

#### Manual Tests
- `testsManual/test_mcp_server.py` - Connect to real MCP server, list tools

### Success Criteria
- [ ] Can connect to STDIO MCP servers
- [ ] Can connect to HTTP MCP servers
- [ ] Can list tools from MCP servers
- [ ] Can execute tools on MCP servers
- [ ] Proper async handling
- [ ] All tests pass

---

## Stage 9: CLI Command: `mci run` (STDIO Only)

### Goal
Implement the `run` command to launch MCP servers via STDIO.

### Directories to Create
```
src/mci/core/
└── dynamic_server.py    # Dynamic MCP server creation
```

### Files to Create/Modify
- **src/mci/core/dynamic_server.py** - Create MCP server from MCI schema
- **src/mci/cli/run.py** - Run command implementation
- **src/mci/mci.py** - Register run command

### Classes/Functions
- `run_command(file: str, filter: str)` - Click command for `mci run`
- `DynamicMCPServer` class with async methods:
  - `async create_from_schema(schema_path: str, filter_spec: str = None) -> Server`
  - `async register_tools(tools: list[Tool]) -> None`
  - `async handle_tool_execution(name: str, args: dict) -> ToolResult`
  - `async start_stdio() -> None` - Start server on STDIO
- `run_server(schema_path: str, filter_spec: str) -> None` - Main run function

### Tests

#### Unit Tests
- `tests/unit/core/test_dynamic_server.py`
  - `test_create_server()` - Create server from schema
  - `test_register_tools()` - Register MCI tools
  - `test_handle_execution()` - Handle tool execution requests
- `tests/unit/cli/test_run.py`
  - `test_run_default_file()` - Run with default mci.json
  - `test_run_custom_file()` - Run with --file option
  - `test_run_with_filter()` - Run with --filter option

#### Feature Tests
- `tests/test_run_command.py` - Test full run command with mock MCP client

#### Manual Tests
- `testsManual/test_run_stdio.py` - Run actual MCP server, connect with MCP client

### Success Criteria
- [ ] `uvx mci run` starts MCP server on STDIO
- [ ] `uvx mci run --file=custom.mci.json` uses custom file
- [ ] `uvx mci run --filter=tags:Tag1,Tag2` filters tools
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

1. **Stage 11** (Future): `mci run --port` for HTTP-based MCP servers
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
