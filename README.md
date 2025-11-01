# MCI CLI Tool

A command-line interface for managing Model Context Interface (MCI) schemas and dynamically running MCP (Model Context Protocol) servers using defined MCI toolsets.

## Quick Start

### Installation

Install using uv (recommended):

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install mci-cli
uv tool install mci-cli
```

Or install from source:

```bash
git clone https://github.com/Model-Context-Interface/mci-uvx.git
cd mci-uvx
uv sync --all-extras
uv tool install --editable .
```

### Your First MCI Project

1. **Initialize a new project**:
   ```bash
   uv run mci install
   ```
   This creates `mci.json` with example tools and `mci/` directory with example toolsets.

2. **List your tools**:
   ```bash
   uv run mci list
   ```

3. **Validate your configuration**:
   ```bash
   uv run mci validate
   ```

4. **Run an MCP server**:
   ```bash
   uv run mci run
   ```

That's it! Your MCI tools are now available via the MCP protocol.

## Core Concepts

### MCI Tools

MCI tools are reusable, declarative tool definitions that can execute different types of operations:

- **Text tools**: Return templated text responses
- **File tools**: Read and return file contents
- **CLI tools**: Execute command-line programs
- **HTTP tools**: Make API requests
- **MCP tools**: Invoke other MCP servers

### Toolsets

Toolsets are collections of related tools stored in the `mci/` directory. They can be:

- Shared across projects
- Filtered by tags or names
- Referenced from your main configuration

### MCP Server Integration

The `mci run` command creates an MCP server that:

- Dynamically loads tools from your MCI schema
- Serves them via the Model Context Protocol
- Can be used with MCP-compatible clients (like Claude Desktop)
- Supports filtering to expose only specific tools

## Available Commands

### `mci install`

Bootstrap a new MCI project with starter configuration.

```bash
# Create JSON configuration (default)
uv run mci install

# Create YAML configuration
uv run mci install --yaml
```

Creates:
- `mci.json` (or `mci.yaml`) - Main configuration file
- `mci/` directory - Library of toolsets
- `mci/.gitignore` - Excludes generated files

### `mci list`

Display all available tools from your configuration.

```bash
# List all tools (table format)
uv run mci list

# List with verbose details
uv run mci list --verbose

# Filter by tags
uv run mci list --filter tags:api,database

# Export to JSON
uv run mci list --format json

# Export to YAML
uv run mci list --format yaml
```

**Filter types**:
- `tags:tag1,tag2` - Include tools with any of these tags
- `only:tool1,tool2` - Include only specific tools
- `except:tool1,tool2` - Exclude specific tools
- `toolsets:ts1,ts2` - Include tools from specific toolsets
- `without-tags:tag1,tag2` - Exclude tools with these tags

### `mci validate`

Validate your MCI schema for correctness.

```bash
# Validate default configuration
uv run mci validate

# Validate specific file
uv run mci validate --file custom.mci.json
```

Checks for:
- Schema structure and syntax
- Required fields
- Data types
- Tool definitions
- Toolset references
- MCP command availability (warnings)

### `mci add`

Add toolset references to your schema.

```bash
# Add a toolset
uv run mci add weather-tools

# Add with filter
uv run mci add analytics --filter=only:Tool1,Tool2

# Add with tag filter
uv run mci add api-tools --filter=tags:api,database

# Add to custom file
uv run mci add weather-tools --path=custom.mci.json
```

Automatically preserves your file format (JSON stays JSON, YAML stays YAML).

### `mci run`

Launch an MCP server that dynamically serves your tools.

```bash
# Run with default configuration
uv run mci run

# Run with specific file
uv run mci run --file custom.mci.json

# Run with filtered tools
uv run mci run --filter tags:production

# Run excluding tools
uv run mci run --filter except:deprecated_tool
```

The server:
- Loads tools from your MCI schema
- Converts them to MCP format
- Listens on STDIO for MCP requests
- Delegates execution back to MCIClient

**Stop the server**: Press `Ctrl+C`

## Example Workflows

### Development Workflow

```bash
# 1. Create a new project
uv run mci install

# 2. Add toolsets
uv run mci add weather-tools
uv run mci add api-tools --filter=tags:production

# 3. Preview your tools
uv run mci list --verbose

# 4. Validate everything
uv run mci validate

# 5. Test with MCP server
uv run mci run --filter tags:development
```

### Production Deployment

```bash
# Validate before deployment
uv run mci validate

# Run server with only production tools
uv run mci run --filter tags:production

# Or exclude experimental features
uv run mci run --filter without-tags:experimental,beta
```

### Tool Development

```bash
# Create your schema
uv run mci install

# Edit mci.json to add your tool
# (see examples in the generated file)

# Validate your changes
uv run mci validate

# Test your tool
uv run mci list --verbose
uv run mci run
```

## Supported Execution Types

MCI tools support multiple execution types. Below are examples for each type:

### Text Execution

Returns templated text using `{{props.field}}` and `{{env.VAR}}` syntax.

**Example:**
```json
{
  "name": "greet_user",
  "description": "Greet a user by name",
  "inputSchema": {
    "type": "object",
    "properties": {
      "username": {
        "type": "string",
        "description": "Name of the user to greet"
      }
    },
    "required": ["username"]
  },
  "execution": {
    "type": "text",
    "text": "Hello {{props.username}}! Welcome to MCI."
  }
}
```

This tool takes a username as input and returns a personalized greeting message.

### File Execution

Reads and returns file contents, with optional templating support.

**Example:**
```json
{
  "name": "read_config",
  "description": "Read application configuration file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "config_path": {
        "type": "string",
        "description": "Path to configuration file"
      }
    },
    "required": ["config_path"]
  },
  "execution": {
    "type": "file",
    "path": "{{props.config_path}}",
    "enableTemplating": false
  },
  "directoryAllowList": ["./configs", "/etc/myapp"]
}
```

This tool reads a configuration file from an allowed directory. The `directoryAllowList` ensures files can only be read from safe locations.

### CLI Execution

Executes command-line programs with arguments and flags.

**Example:**
```json
{
  "name": "search_files",
  "description": "Search for text in files using grep",
  "inputSchema": {
    "type": "object",
    "properties": {
      "pattern": {
        "type": "string",
        "description": "Search pattern"
      },
      "directory": {
        "type": "string",
        "description": "Directory to search in"
      },
      "ignore_case": {
        "type": "boolean",
        "description": "Ignore case in search"
      }
    },
    "required": ["pattern", "directory"]
  },
  "execution": {
    "type": "cli",
    "command": "grep",
    "args": ["-r", "-n", "{{props.pattern}}"],
    "flags": {
      "-i": {
        "from": "props.ignore_case",
        "type": "boolean"
      }
    },
    "cwd": "{{props.directory}}",
    "timeout_ms": 8000
  }
}
```

This tool executes `grep` to search for text in files. The `-i` flag is conditionally added based on the `ignore_case` property.

### HTTP Execution

Makes HTTP requests to external APIs with full header and authentication support.

**Example:**
```json
{
  "name": "get_weather",
  "description": "Get current weather for a location",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City name or coordinates"
      }
    },
    "required": ["location"]
  },
  "execution": {
    "type": "http",
    "method": "GET",
    "url": "https://api.example.com/weather",
    "params": {
      "location": "{{props.location}}",
      "units": "metric"
    },
    "headers": {
      "Accept": "application/json",
      "Authorization": "Bearer {{env.WEATHER_API_KEY}}"
    },
    "timeout_ms": 5000
  }
}
```

This tool makes a GET request to a weather API, using an API key from the environment and the location from the input properties.

### MCP Execution

Invokes tools from other MCP servers (for tool composition and chaining).

**Example:**
```json
{
  "name": "analyze_with_ai",
  "description": "Analyze data using AI MCP server",
  "inputSchema": {
    "type": "object",
    "properties": {
      "data": {
        "type": "string",
        "description": "Data to analyze"
      }
    },
    "required": ["data"]
  },
  "execution": {
    "type": "mcp",
    "server": "ai_analysis_server",
    "tool": "analyze_text",
    "arguments": {
      "text": "{{props.data}}",
      "model": "gpt-4"
    }
  }
}
```

This tool delegates execution to another MCP server's tool, enabling composition of complex workflows.

### Common Features

All execution types support:
- **Environment variable templating**: Use `{{env.VAR}}` to access environment variables
- **Property templating**: Use `{{props.field}}` to access input properties
- **Input validation**: Define schemas with JSON Schema for type safety

## Configuration Files

### Main Configuration (`mci.json` or `mci.yaml`)

```json
{
  "schemaVersion": "1.0",
  "metadata": {
    "name": "My Project",
    "description": "My MCI configuration"
  },
  "tools": [
    {
      "name": "example_tool",
      "description": "Example tool",
      "inputSchema": {
        "type": "object",
        "properties": {
          "message": {"type": "string"}
        }
      },
      "execution": {
        "type": "text",
        "text": "Echo: {{props.message}}"
      }
    }
  ],
  "toolsets": ["my-toolset"],
  "mcp_servers": {}
}
```

### Toolset Files (`mci/*.mci.json`)

Toolset files follow the same schema but typically contain focused collections of related tools.

## Environment Variables

MCI supports environment variable templating in tool definitions:

```json
{
  "execution": {
    "type": "http",
    "url": "{{env.BASE_URL}}/api/endpoint",
    "headers": {
      "Authorization": "Bearer {{env.API_KEY}}"
    }
  }
}
```

### Setting Environment Variables for MCP Clients

When running MCI as an MCP server from clients like Claude Desktop or VS Code, configure environment variables in the client's settings:

**Claude Desktop Example** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mci-tools": {
      "command": "uv",
      "args": ["run", "mci", "run"],
      "cwd": "/path/to/your/project",
      "env": {
        "API_KEY": "your-api-key",
        "BASE_URL": "https://api.example.com",
        "PROJECT_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

**VS Code Example** (`.vscode/settings.json`):
```json
{
  "mcp.servers": {
    "mci-tools": {
      "command": "uv",
      "args": ["run", "mci", "run"],
      "cwd": "${workspaceFolder}",
      "env": {
        "API_KEY": "your-api-key",
        "BASE_URL": "https://api.example.com",
        "PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

**Running Standalone** (without MCP client):

If you're running the MCP server directly in a terminal, set environment variables first:

```bash
export API_KEY=your-api-key
export BASE_URL=https://api.example.com
uv run mci run
```

## Integration with MCP Clients

The `mci run` command creates an MCP-compliant server that can be used with:

- **Claude Desktop**: Configure as an MCP server in settings
- **MCP CLI tools**: Connect via STDIO transport
- **Custom integrations**: Use the MCP Python SDK

Example Claude Desktop configuration:

```json
{
  "mcpServers": {
    "mci-tools": {
      "command": "uv",
      "args": ["run", "mci", "run"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

## Documentation

- **[Development Guide](development.md)** - Setup, testing, and contribution workflow
- **[Technical Architecture](docs/architecture.md)** - Project structure and design decisions
- **[Implementation Plan](PLAN.md)** - Full development roadmap
- **[Product Requirements](PRD.md)** - Project goals and specifications
- **[Installation Guide](installation.md)** - Detailed installation instructions
- **[Publishing Guide](publishing.md)** - How to publish to PyPI

## Key Features

✨ **Declarative Tool Definitions** - Define tools once, use everywhere

🔌 **Multiple Execution Types** - Text, file, CLI, HTTP, and MCP support

🎯 **Flexible Filtering** - Filter by tags, names, or toolsets

📦 **Toolset Management** - Organize and reuse tool collections

🔄 **Dynamic MCP Servers** - Instantly turn MCI schemas into MCP servers

🌍 **Environment Templating** - Use environment variables in tool definitions

✅ **Built-in Validation** - Comprehensive schema validation

📊 **Multiple Output Formats** - JSON, YAML, and table displays

## Contributing

Contributions are welcome! Please see [development.md](development.md) for:

- Setting up your development environment
- Running tests and linters
- Building the project
- Submitting pull requests

## License

MIT License - see LICENSE file for details

---

*This project was built from [simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
