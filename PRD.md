# 🧩 MCI CLI Tool — Product Requirements Document (PRD)

## 1. Overview
The **MCI CLI Tool** is a **uvx-based command-line interface** designed to manage **MCI (Model Context Interface)** schemas and dynamically run **MCP servers** using defined MCI toolsets.

It serves as the main interface for developers to:
- Create, modify, and validate `.mci.json` or `.mci.yaml` files.
- Dynamically run MCP-compatible servers based on MCI definitions.
- Generate example configurations and toolsets.

The CLI integrates **`mci-py`** for schema parsing, validation, and execution logic, and **`mcp`** for server management and protocol-level operations.

---

## 2. Goals
- Provide a simple CLI to **instantiate dynamic MCP servers** from static JSON/YAML definitions.
- Automate the creation and management of **MCI schemas**.
- Support **JSON** and **YAML** configurations equally.
- Maintain compatibility with **uvx** runtime and **mci-py** APIs.

---

## 3. Dependencies
- **mci-py** → for schema parsing, validation, and tool execution
- **mcp** → for server creation and protocol communication
- **uvx** → as the Python-based CLI launcher/runtime environment
- Any other credible packages to simplify CLI and JSON/YAML operations

---

## 4. Core Commands

### 🏃‍♂️ `uvx mcix run`
**Purpose:** Launch a dynamic MCP server using the defined MCI configuration.

#### Usage Examples
```bash
uvx mcix run
uvx mcix run --file=./tools.mci.json
uvx mcix run --filter=tags:Tag1,Tag2
uvx mcix run --file=./tools.mci.json --filter=tags:Tag1,Tag2
```

#### Behavior
- By default, searches for `mci.json` or `mci.yaml` in the current directory.
- Uses **mci-py** to parse and validate the MCI schema.
- Dynamically creates an **MCP server** with the provided toolsets.
- When execution requests arrive, **mci-py** handles tool execution based on schema definitions.
- Supports `--filter` to select only specific tools or tags.

#### Parameters
| Flag | Description |
|------|--------------|
| `--file` | Specify which MCI schema file to load (optional) |
| `--filter` | Comma-separated list of tags or tool names to load (optional) |

#### Filter Types

| Filter Type   | Description                           | Example                       |
| ------------- | ------------------------------------- | ----------------------------- |
| `only`        | Include only specified tool names     | `"get_weather, get_forecast"` |
| `except`      | Exclude specified tool names          | `"delete_user, drop_table"`   |
| `tags`        | Include only tools with matching tags | `"read, search"`              |
| `withoutTags` | Exclude tools with matching tags      | `"write, delete"`             |

#### Output
- Starts MCP server instance on a STDIO.
- In case of port, it should return the URL of MCP server (`http://localhost:3000/mcp`)

---

### ⚙️ `uvx mcix install`
**Purpose:** Initialize a new MCI implementation structure in project root.

#### Usage Examples
```bash
uvx mcix install
uvx mcix install --yaml
```

#### Behavior
- Creates `mci.json` or `mci.yaml` (depending on flag) with template content:
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
          "required": [
            "message"
          ]
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
- Generates `./mci` directory with:
  - `example.mci.json` → example toolset file
  - `mcp/` → empty directory for future MCP toolsets
  - `.gitignore` → with "./mcp" added

---

### ➕ `uvx mcix add <toolsetName>`
**Purpose:** Add a toolset reference to the main MCI file.

#### Usage Examples
```bash
uvx mcix add weather-tools
uvx mcix add analytics --filter=only:SummarizeData,AnalyzeSentiment
```

#### Behavior
- Adds the specified toolset reference to `mci.json` or `mci.yaml`.
- Optionally applies filters to include only specific tools.
- If `--path` is provided, modifies a custom file instead of the default.

#### Parameters
| Flag | Description |
|------|--------------|
| `<toolsetName>` | Name of the toolset file (without extension) |
| `--filter` | Filter tools to include (optional) |
| `--path` | Path to alternative MCI file (optional) |

#### JSON Example
from:
```json
"toolsets": [
    "weather"
  ]
```
to:
```json
"toolsets": [
    "weather",
    {
      "name": "analytics",
      "filter": "only",
      "filterValue": "SummarizeData,AnalyzeSentiment"
    }
  ]
```

---

### 📋 `uvx mcix list`
**Purpose:** Display all available tools with applied filters from the current MCI configuration. It tests the `run` method to check what context will be returned on MCP run.

#### Usage Examples
```bash
uvx mcix list
uvx mcix list --file=./tools.mci.json
uvx mcix list --filter=tags:Tag1,Tag2
uvx mcix list --format=json
uvx mcix list --format=yaml --verbose
```

#### Behavior
- By default, searches for `mci.json` or `mci.yaml` in the current directory.
- Uses **mci-py**'s `list_tools()` method to get all available tools with applied filters.
- Shows tools in a table format with name, source toolset, and description.
- Applies the same filtering logic as the `run` command would use.
- When using `--format=json` or `--format=yaml`, creates a timestamped file (e.g., `tools_20241029_143022.json`) instead of printing to console.

#### Parameters
| Flag | Description |
|------|--------------|
| `--file` | Specify which MCI schema file to read (optional) |
| `--filter` | Apply filters to narrow down tools (same as `run` command) |
| `--format` | Output format: `table` (default), `json`, or `yaml` |
| `--verbose` | Show additional tool metadata (tags, parameters, etc.) |

#### Filter Types
Same filter types as the `run` command: `only`, `except`, `tags`, `withoutTags`.

#### Output Examples

**Table Format (Default):**
```
� Available Tools (5):
┌──────────────────┬─────────────────┬─────────────────────────────────────┐
│ Name             │ Source          │ Description                         │
├──────────────────┼─────────────────┼─────────────────────────────────────┤
│ n8n_workflow     │ main            │ Add post to Drive                   │
│ get_weather      │ weather-tools   │ Get current weather for a location  │
│ get_forecast     │ weather-tools   │ Get weather forecast                │
│ weather_alerts   │ weather-tools   │ Get weather alerts                  │
│ analyze_sentiment│ analytics       │ Analyze text sentiment              │
│ summarize_data   │ analytics       │ Summarize dataset                   │
└──────────────────┴─────────────────┴─────────────────────────────────────┘
```

**Verbose Format:**
```
� Available Tools (5):

get_weather (weather-tools)
├── Description: Get current weather for a location
├── Tags: [api, data, weather]
└── Parameters: location (string), units (optional)

get_forecast (weather-tools)
├── Description: Get weather forecast
├── Tags: [api, data, weather]
└── Parameters: location (string), days (optional)

analyze_sentiment (analytics)
├── Description: Analyze text sentiment
├── Tags: [data, ml, text]
└── Parameters: text (string), model (optional)
```

**JSON/YAML File Output:**
When using `--format=json` or `--format=yaml`, the command creates a timestamped file instead of printing to console:

```bash
# Creates tools_20241029_143022.json
uvx mcix list --format=json

# Creates tools_20241029_143022.yaml  
uvx mcix list --format=yaml --verbose
```

**File Content Example (JSON):**
```json
{
  "timestamp": "2024-10-29T14:30:22Z",
  "mci_file": "./mci.json",
  "filters_applied": ["tags:api,data"],
  "tools": [
    {
      "name": "get_weather",
      "source": "weather-tools", 
      "description": "Get current weather for a location",
      "tags": ["api", "data", "weather"],
      "parameters": {...}
    }
  ],
  "total": 5
}
```

The generated filename format is: `tools_YYYYMMDD_HHMMSS.{json|yaml}`

---

### ✅ `uvx mcix validate`
**Purpose:** Validate MCI schema files for syntax, structure, and semantic correctness.

#### Usage Examples
```bash
uvx mcix validate
uvx mcix validate --file=./tools.mci.json
```

#### Behavior
- By default, searches for `mci.json` or `mci.yaml` in the current directory.
- Uses **mci-py**'s validation engine to check schema compliance.
- Validates JSON/YAML syntax, required fields, data types, and references.
- Checks that referenced toolset files exist and are valid.
- Verifies MCP server configurations and commands.
- Reports errors and warnings in a simple, readable format.

#### Parameters
| Flag | Description |
|------|--------------|
| `--file` | Specify which MCI schema file to validate (optional) |

#### Output Example
```
✅ Validating: ./mci.json

⚠️  Warnings:
├── Line 15: Toolset 'analytics.mci.json' not found in ./mci/ directory
└── Line 23: MCP server 'filesystem' command 'npx' not found in PATH

✅ Schema is valid - 0 errors found
```

**With Errors:**
```
✅ Validating: ./mci.json

❌ Errors:
├── Line 8: Missing required field 'version' in metadata
└── Line 12: Invalid toolset reference format

⚠️  Warnings:
└── Line 20: Consider using absolute paths for MCP server commands

❌ Validation failed - 2 errors found
```

---

## 5. Internal Workflow

1. **Parse Schema** — `mci-py` reads and validates `.mci.json` or `.mci.yaml`.
2. **Apply Filters** — Filters (if provided) narrow down the loaded tools.
3. **Bootstrap MCP Server** — `mcp` initializes a local web or stdio-based server.
4. **Register Tools** — All tools defined in the schema are registered dynamically.
5. **Handle Execution** — Incoming MCP requests are delegated to `mci-py` executors.
6. **Graceful Shutdown** — Server terminates when stopped or invalidated.

---

## 6. Configuration Structure

### Example `mci.json`
```json
{
  "schemaVersion": "1.0",
  "metadata": {
    "name": "MCI Example",
    "description": "Simple MCI demo"
  },
  "toolsets": [
    { "name": "toolset.mci.json", "tags": ["demo"] }
  ],
  "mcp_servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    }
  }
}
```

---

## 7. Error Handling
| Error | Description |
|--------|-------------|
| InvalidSchemaError | The file does not conform to MCI spec |
| ToolNotFoundError | Filter references a missing tool |
| MCPStartupError | Failed to initialize MCP server |
| FileMissingError | `mci.json` or `mci.yaml` not found |

---

## 8. Future Enhancements
- `--port` to `run` command for dynamic web based MCP servers.
- `mci test` command to simulate tool execution locally.

---

## 9. References
- [MCI Schema Reference](https://usemci.dev/documentation/schema-reference)
- [MCI Python API](https://usemci.dev/python/api-reference)
- [MCI Structure Docs](https://usemci.dev/documentation/structure)
- [MCP Servers Reference](https://usemci.dev/documentation/mcp_servers)

