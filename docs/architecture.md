# Technical Architecture

This document describes the technical architecture and design decisions for the MCI CLI tool.

## Overview

The MCI CLI tool is built on a modular architecture that separates concerns into distinct layers:

1. **CLI Layer** - Command-line interface using Click
2. **Core Layer** - Business logic and MCI/MCP integration
3. **Utils Layer** - Shared utilities and helpers

## Design Principles

### Delegation to mci-py

All tool loading, filtering, and schema operations are delegated to `MCIClient` from mci-py. The CLI tool acts as a thin wrapper that:

- Provides command-line interface to mci-py functionality
- Formats output for terminal display
- Handles file discovery and user interaction
- Manages MCP server lifecycle

This ensures consistency with the upstream mci-py adapter and avoids reimplementing core logic.

### Modular Design

Each command is implemented as a separate module in `src/mci/cli/`, making it easy to:

- Add new commands
- Test commands in isolation
- Maintain consistent command structure
- Share common utilities

### Error Handling Strategy

The CLI provides user-friendly error messages by:

1. Catching `MCIClientError` exceptions from mci-py
2. Extracting error details and context
3. Formatting with Rich library for visual clarity
4. Providing actionable suggestions for resolution

## Component Architecture

### CLI Layer (`src/mci/cli/`)

#### Command Structure

All commands follow a consistent pattern:

```python
import click
from mci.core.config import MCIConfig
from mci.utils.error_handler import ErrorHandler

@click.command()
@click.option("--file", "-f", help="Path to MCI file")
def command_name(file: str | None):
    """Command description."""
    try:
        # Load configuration
        config = MCIConfig()
        client = config.load(file or "mci.json")
        
        # Execute command logic
        result = do_something(client)
        
        # Display results
        print(result)
        
    except MCIClientError as e:
        # Handle errors
        click.echo(ErrorHandler.format_mci_client_error(e))
        raise click.Abort()
```

#### Output Formatters

Output formatters (`src/mci/cli/formatters/`) handle different output formats:

- **TableFormatter**: Rich-based terminal tables
- **JSONFormatter**: JSON output with timestamps
- **YAMLFormatter**: YAML output with timestamps

All formatters implement a common interface for consistency.

### Core Layer (`src/mci/core/`)

#### Configuration Management

**MCIConfig** handles configuration loading:

```python
class MCIConfig:
    def load(self, file_path: str, env_vars: dict = None) -> MCIClient:
        """Load and validate MCI configuration."""
        # Uses MCIClient from mci-py
        
    def validate_schema(self, file_path: str) -> tuple[bool, str]:
        """Validate schema without loading."""
```

**MCIFileFinder** discovers MCI files:

```python
class MCIFileFinder:
    def find_mci_file(self, directory: str) -> str | None:
        """Find mci.json or mci.yaml in directory."""
        
    def get_file_format(self, file_path: str) -> str:
        """Detect file format (json/yaml)."""
```

#### MCI-PY Integration

**MCIClientWrapper** wraps MCIClient for CLI use:

```python
class MCIClientWrapper:
    def __init__(self, schema_path: str, env_vars: dict = None):
        self.client = MCIClient(schema_file_path=schema_path, env_vars=env_vars)
        
    def get_tools(self) -> list:
        """Get all tools from schema."""
        
    def filter_tags(self, tags: list[str]) -> list:
        """Filter tools by tags."""
```

**ToolManager** parses and applies filter specifications:

```python
class ToolManager:
    @staticmethod
    def apply_filter_spec(wrapper: MCIClientWrapper, spec: str) -> list:
        """Parse and apply filter specification."""
        # Supports: tags:, only:, except:, without-tags:, toolsets:
```

#### MCP Server Infrastructure

**MCIToolConverter** converts MCI tools to MCP format:

```python
class MCIToolConverter:
    @staticmethod
    def to_mcp_tool(mci_tool) -> types.Tool:
        """Convert MCI tool to MCP Tool."""
```

**MCPServerBuilder** creates MCP servers:

```python
class MCPServerBuilder:
    async def create_server(self, name: str, version: str) -> Server:
        """Create MCP server instance."""
        
    async def register_all_tools(self, server: Server, tools: list):
        """Register tools with server."""
```

**ServerInstance** manages server lifecycle:

```python
class ServerInstance:
    async def start(self, stdio: bool = True):
        """Start server on STDIO or other transport."""
        
    def stop(self):
        """Stop server gracefully."""
```

**DynamicMCPServer** provides high-level server creation:

```python
class DynamicMCPServer:
    async def create_from_mci_schema(self, server_name: str) -> ServerInstance:
        """Create server from MCI schema with filtering."""
        
    async def start_stdio(self):
        """Start server on STDIO."""
```

#### Schema Editing

**SchemaEditor** modifies MCI schema files:

```python
class SchemaEditor:
    def add_toolset(self, toolset_name: str, filter_spec: str = None):
        """Add toolset reference to schema."""
        
    def save(self):
        """Save changes preserving format."""
```

### Utils Layer (`src/mci/utils/`)

#### Error Handling

**ErrorHandler** formats MCIClient errors:

```python
class ErrorHandler:
    @staticmethod
    def format_mci_client_error(error: MCIClientError) -> str:
        """Format error with suggestions."""
```

**ErrorFormatter** provides Rich-based display:

```python
class ErrorFormatter:
    def format_validation_errors(self, errors: list[ValidationError]):
        """Display validation errors in panel."""
        
    def format_validation_success(self, file_path: str):
        """Display success message."""
```

#### Validation

**Validation utilities** for file operations:

```python
def is_valid_path(path: str) -> bool:
    """Check if path is valid."""
    
def file_exists(path: str) -> bool:
    """Check if file exists."""
    
def is_readable(path: str) -> bool:
    """Check if file is readable."""
```

## Data Flow

### Tool Loading Flow

```
User Command
    ↓
MCIConfig.load()
    ↓
MCIClient (mci-py)
    ↓
Parse schema → Load toolsets → Apply environment variables
    ↓
Return MCIClient instance
    ↓
MCIClientWrapper
    ↓
Apply filters (if specified)
    ↓
Return filtered tools
```

### MCP Server Creation Flow

```
User runs `mcix run`
    ↓
Load MCI schema via MCIConfig
    ↓
Create MCIClientWrapper
    ↓
Apply filter_spec if provided
    ↓
Create DynamicMCPServer
    ↓
MCPServerBuilder.create_server()
    ↓
Convert tools: MCI → MCP (MCIToolConverter)
    ↓
Register tools with server
    ↓
Create ServerInstance
    ↓
Start STDIO transport
    ↓
Handle MCP protocol requests:
  - tools/list → Return registered tools
  - tools/call → Delegate to MCIClient.execute()
```

### Tool Execution Flow (within MCP server)

```
MCP client sends tools/call request
    ↓
ServerInstance receives request
    ↓
Extract tool name and arguments
    ↓
MCIClient.execute(tool_name, properties)
    ↓
MCIClient handles execution:
  - Load tool definition
  - Apply templating
  - Execute based on type (text/file/cli/http/mcp)
  - Return result
    ↓
ServerInstance formats result as MCP response
    ↓
Return to client
```

## Key Design Decisions

### Why Delegate to mci-py?

1. **Consistency**: Ensures CLI and programmatic usage behave identically
2. **Maintainability**: Core logic maintained in one place
3. **Reliability**: mci-py is well-tested and handles edge cases
4. **Future-proof**: New mci-py features automatically available

### Why Rich for Output?

1. **User Experience**: Beautiful terminal output with colors and formatting
2. **Accessibility**: Fallback to plain text when colors not supported
3. **Consistency**: Professional look across all commands
4. **Maintainability**: Simple API for complex output

### Why Click for CLI?

1. **Pythonic**: Natural Python API for commands and options
2. **Powerful**: Supports complex argument parsing and validation
3. **Extensible**: Easy to add new commands
4. **Well-documented**: Extensive documentation and examples

### Why Separate Formatters?

1. **Flexibility**: Users choose output format (table/json/yaml)
2. **Testability**: Easy to test formatting logic
3. **Reusability**: Formatters can be used across commands
4. **Maintainability**: Changes to one format don't affect others

## Performance Considerations

### Schema Loading

- Schemas are loaded once per command execution
- MCIClient caches parsed tools
- Toolset files loaded lazily by MCIClient

### Tool Filtering

- Filtering done in-memory on already-loaded tools
- O(n) complexity where n = number of tools
- Acceptable for typical tool counts (< 1000)

### MCP Server

- Tools converted to MCP format once at startup
- Kept in memory for fast access
- Tool execution delegates to MCIClient (no caching)

## Security Considerations

### File Access

- Path validation prevents directory traversal
- Toolset files must be in `./mci/` directory
- File operations use Path library for safety

### Command Execution

- CLI execution delegated to MCIClient
- MCIClient handles sandboxing and validation
- No shell injection possible in MCI CLI layer

### Environment Variables

- Environment variables explicitly passed to MCIClient
- No automatic injection of sensitive variables
- User controls which variables are available

## Extensibility

### Adding New Commands

1. Create new file in `src/mci/cli/`
2. Implement Click command
3. Import in `src/mci/mci.py`
4. Add command to CLI group
5. Write tests in `tests/unit/cli/`

### Adding New Output Formats

1. Create formatter in `src/mci/cli/formatters/`
2. Implement common interface
3. Register in commands that support formats
4. Write tests in `tests/unit/cli/formatters/`

### Adding New Validators

1. Add validation logic to `src/mci/core/validator.py`
2. Update `validate` command to use new validators
3. Add error/warning formatting
4. Write tests in `tests/unit/core/`

## Testing Strategy

### Unit Tests

- Test individual functions/classes in isolation
- Mock external dependencies (file system, MCIClient)
- Cover edge cases and error conditions
- Fast execution (< 1s per test)

### Feature Tests

- Test complete command workflows
- Use real files and configurations
- Verify output format and content
- Slower but more comprehensive

### Manual Tests

- Test complex integration scenarios
- Verify MCP server behavior
- Test with real MCP clients
- Human-verified output

## Future Enhancements

### Potential Improvements

1. **Caching**: Cache parsed schemas for faster repeated commands
2. **Parallel Loading**: Load toolset files in parallel
3. **Streaming**: Support streaming output for large tool lists
4. **Plugins**: Plugin system for custom commands/formatters
5. **Config Profiles**: Support multiple configuration profiles

### Known Limitations

1. **Large Schemas**: May be slow with 1000+ tools (not optimized)
2. **Binary Output**: No support for binary tool outputs
3. **Concurrent Execution**: One tool execution at a time per server
4. **Error Recovery**: Limited error recovery in MCP server

---

*For more information, see [development.md](../development.md) and [PLAN.md](../PLAN.md).*
