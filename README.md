# MCI CLI Tool

A command-line interface for managing Model Context Interface (MCI) schemas and dynamically running MCP (Model Context Protocol) servers using defined MCI toolsets.

## Features
- Connect existing **MCP servers** with automatic **caching** and easy **filtering** options to make your unique set of tools
- Define your custom tools in JSON or YAML using clear, reviewable MCI schema
  - API:
    - Connect your n8n, Make and other workflow builders as tools
    - Convert any REST API Docs to AI tools in minute with LLM
    - Run remote code with AWS Lambda, judge0, etc.
    - Authentication, headers, body... Full set of API features are supported
  - CLI:
    - Run server based CLI commands as tool from simple "ls" to anything else you can install with apt-get!
    - Write separated python script and convert in tool in 30 seconds!
    - Build super fast GoLang binary and run as AI tool
  - File:
    - Manage your prompts, generate reports, and provide context with ease
    - Any file becomes a template: From printing simple variables (`{{ props.message }}`) to blocks like if, for & foreach
    - Everything you need to create real, dynamic and usable templates
  - Text:
    - Simplest way to return dynamic or static text from tool
    - Supports full templating as File type, but defined inside .mci.json
    - Ideal for serving dynamic assets (image URLs per user, PDFs, etc)
    - As well as for generating simple messages
- Make **toolset** from your custom tools: easiest way to organize, manage and share your tools!
- Everything mentioned above you can use programmatically via [MCI-Adapter](https://github.com/Model-Context-Interface/mci-py) for your language
- Or.. Instantly serve them as a unified **STDIO MCP server** via `uvx mcix run` command.
- And... Create separate .mci.json files to serve them as different MCP servers for different agents! Reducing token and runtime overhead by providing small, specific context files tailored per agent.

Everything simple, super flexible and still, high performant!

> Check out the [documentation](https://usemci.dev/) for general understanding of MCI (We are working hard to update docs with `uvx mcix` tool usage)

## Quick Start

No installation needed! Run MCI directly using `uvx`:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Your First MCI Project

1. **Initialize a new project**:
   ```bash
   uvx mcix install
   ```
   This creates `mci.json` with example tools and `mci/` directory with example toolsets.

2. **List your tools**:
   ```bash
   uvx mcix list
   ```

3. **Validate your configuration**:
   ```bash
   uvx mcix validate
   ```

4. **Run an MCP server**:
   ```bash
   uvx mcix run
   ```

That's it! Your MCI tools are now available via the MCP protocol.

### Optional: Install MCI Globally

If you prefer to install MCI permanently:

```bash
# Install globally with uv
uv tool install mcix

# Then use without uvx prefix
mcix install
mcix list
mcix run
```

Or install from source:

```bash
git clone https://github.com/Model-Context-Interface/mci-uvx.git
cd mci-uvx
uv sync --all-extras
uv tool install --editable .
```

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
uvx mcix install

# Create YAML configuration
uvx mcix install --yaml
```

Creates:
- `mci.json` (or `mci.yaml`) - Main configuration file
- `mci/` directory - Library of toolsets
- `mci/.gitignore` - Excludes generated files

### `mci list`

Display all available tools from your configuration.

```bash
# List all tools (table format)
uvx mcix list

# List with verbose details
uvx mcix list --verbose

# Filter by tags
uvx mcix list --filter tags:api,database

# Export to JSON
uvx mcix list --format json

# Export to YAML
uvx mcix list --format yaml
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
uvx mcix validate

# Validate specific file
uvx mcix validate --file custom.mci.json
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
uvx mcix add weather-tools

# Add with filter
uvx mcix add analytics --filter=only:Tool1,Tool2

# Add with tag filter
uvx mcix add api-tools --filter=tags:api,database

# Add to custom file
uvx mcix add weather-tools --path=custom.mci.json
```

Automatically preserves your file format (JSON stays JSON, YAML stays YAML).

### `mci run`

Launch an MCP server that dynamically serves your tools.

```bash
# Run with default configuration
uvx mcix run

# Run with specific file
uvx mcix run --file custom.mci.json

# Run with filtered tools
uvx mcix run --filter tags:production

# Run excluding tools
uvx mcix run --filter except:deprecated_tool
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
uvx mcix install

# 2. Add toolsets
uvx mcix add weather-tools
uvx mcix add api-tools --filter=tags:production

# 3. Preview your tools
uvx mcix list --verbose

# 4. Validate everything
uvx mcix validate

# 5. Test with MCP server
uvx mcix run --filter tags:development
```

### Production Deployment

```bash
# Validate before deployment
uvx mcix validate

# Run server with only production tools
uvx mcix run --filter tags:production

# Or exclude experimental features
uvx mcix run --filter without-tags:experimental,beta
```

### Tool Development

```bash
# Create your schema
uvx mcix install

# Edit mci.json to add your tool
# (see examples in the generated file)

# Validate your changes
uvx mcix validate

# Test your tool
uvx mcix list --verbose
uvx mcix run
```

## Supported Execution Types

MCI tools support multiple execution types. Below are examples for each type:

## Tool Annotations

MCI tools support optional annotations that provide metadata and behavioral hints about the tool. These annotations are preserved when serving tools via MCP servers and help MCP clients make better decisions about tool usage and display.

### Supported Annotation Fields

All annotation fields are optional:

- **`title`**: Human-readable title for the tool (alternative to the machine name)
- **`readOnlyHint`**: `true` if the tool only reads data without modification, `false` if it modifies state
- **`destructiveHint`**: `true` if the tool may perform destructive updates (delete, overwrite), `false` if only additive
- **`idempotentHint`**: `true` if calling the tool repeatedly with the same arguments has no additional effect
- **`openWorldHint`**: `true` if the tool interacts with external entities (web APIs, databases), `false` for internal tools

**Example with annotations:**
```json
{
  "name": "delete_resource",
  "description": "Delete a resource from the remote server",
  "annotations": {
    "title": "Delete Resource",
    "readOnlyHint": false,
    "destructiveHint": true,
    "idempotentHint": false,
    "openWorldHint": true
  },
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {"type": "string", "description": "Resource ID"}
    },
    "required": ["id"]
  },
  "execution": {
    "type": "http",
    "method": "DELETE",
    "url": "{{env.API_URL}}/resources/{{props.id}}"
  }
}
```

**Example with partial annotations:**
```json
{
  "name": "read_data",
  "description": "Read data from the database",
  "annotations": {
    "title": "Read Data",
    "readOnlyHint": true
  },
  "execution": {
    "type": "http",
    "method": "GET",
    "url": "{{env.API_URL}}/data"
  }
}
```

> **Note**: Annotations are automatically included when serving tools via `uvx mcix run`. MCP clients can use these annotations for filtering, validation, and user interface enhancements.

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

### Automatic .env File Loading

MCI automatically loads environment variables from `.env` files when loading your MCI schema. This provides a convenient way to manage environment-specific configuration without manually setting variables.

**Automatic Detection:**
- When you run any MCI command (`run`, `list`, `validate`, etc.), MCI looks for `.env` files in:
  1. The project root directory (same location as your `mci.json` or `mci.yaml`)
  2. The `./mci` directory

**Precedence Order (lowest to highest):**
1. `./mci/.env` - Library-level defaults (lowest priority)
2. Project root `.env` - Project-specific overrides
3. System environment variables (set via `export` or shell config)
4. Environment variables passed via CLI (highest priority)

If the same variable is defined in multiple locations, the higher-priority source wins.

**Example .env file:**
```bash
# .env file in project root
API_KEY=your-api-key-here
BASE_URL=https://api.example.com
DEBUG=false

# Comments are supported
# Blank lines are ignored

# Export keyword is optional (automatically stripped)
export OPTIONAL_VAR=value
```

**Example directory structure:**
```
my-project/
├── .env                    # Project-specific variables (overrides ./mci/.env)
├── mci.json               # Your MCI schema
└── mci/
    ├── .env               # Library defaults (lowest priority)
    └── weather.mci.json   # Your toolsets
```

**Example precedence:**
```bash
# ./mci/.env
API_KEY=default-key
LIBRARY_VAR=lib-value

# .env (project root)
API_KEY=project-key        # This overrides ./mci/.env
PROJECT_VAR=proj-value

# Result: MCI will use:
# API_KEY=project-key (from root .env)
# LIBRARY_VAR=lib-value (from ./mci/.env)
# PROJECT_VAR=proj-value (from root .env)
```

**Notes:**
- .env files are completely optional - MCI works fine without them
- No error if .env files are missing
- You can disable auto-loading by setting `auto_load_dotenv=False` when using the MCI library programmatically
- .env files should NOT be committed to version control if they contain secrets

### Setting Environment Variables for MCP Clients

When running MCI as an MCP server from clients like Claude Desktop or VS Code, you have two options for environment variables:

1. **Use .env files** (recommended): Create a `.env` file in your project root, and MCI will automatically load it
2. **Configure in client settings**: Explicitly set environment variables in the MCP client configuration

**Option 1: Using .env files (Recommended)**

Create a `.env` file in your project root:
```bash
# .env
API_KEY=your-api-key
BASE_URL=https://api.example.com
```

Then configure your MCP client with minimal settings:
```json
{
  "mcpServers": {
    "mci-tools": {
      "command": "uvx",
      "args": ["mcix", "run"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

MCI will automatically load the `.env` file when it starts.

**Option 2: Configure in Client Settings**

**Claude Desktop Example** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mci-tools": {
      "command": "uvx",
      "args": ["mcix", "run"],
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
      "command": "uvx",
      "args": ["mcix", "run"],
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

MCI automatically loads `.env` files from your project root and `./mci` directory:

```bash
# Create .env file
echo "API_KEY=your-api-key" > .env
echo "BASE_URL=https://api.example.com" >> .env

# Run MCI - it will automatically load .env
uvx mcix run
```

You can also set environment variables manually if needed:
```bash
export API_KEY=your-api-key
export BASE_URL=https://api.example.com
uvx mcix run
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
      "command": "uvx",
      "args": ["mcix", "run"],
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
