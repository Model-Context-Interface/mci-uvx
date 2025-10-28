# Copilot Instructions for mci-py

## Project Context

- **Check `PRD.md`** for overall project context, goals, and requirements
- **Check `PLAN.md`** for full implementation plan and design decisions
- **Check `development.md`** for testing and linting commands
- **Check `installation.md`** for setup and installation instructions

## Code Documentation Standards

### File-Level Comments

Write explanation comments at the start of each file that describe:

- The purpose of the file
- What functionality it provides
- How it fits into the overall project

Example:

```python
"""
mcipy.py - Main entry point for the MCI Python adapter

This module provides the core functionality for loading and executing
MCI tool definitions from JSON schema files.
"""
```

### Function/Class Documentation

Write explanation comments for each function, class, and method that explain:

- What the function/class does
- Why it exists (not just what it does)
- Any important implementation details or gotchas
- Parameters and return values (if not obvious from type hints)

Example:

```python
def execute_tool(tool_def: dict, properties: dict) -> dict:
    """
    Execute an MCI tool definition with the provided properties.

    Handles templating of environment variables and property values,
    then dispatches to the appropriate executor (HTTP, CLI, or file).
    Returns a structured result with error handling.
    """
    # Implementation
```

## Testing Strategy

### Coverage Goal

**Target: 90%+ test coverage** across all modules

### Test Types

#### 1. Unit Tests

Test every function involved in processing:

- **JSON Schema Validation**: Test schema loading, validation, and error handling
- **Templating Engine**: Test placeholder replacement for `{{env.VAR}}`, `{{props.name}}`, `{{input.field}}`
- **Execution Dispatchers**: Test each executor (HTTP, CLI, file) in isolation
- **Authentication Handlers**: Test API key, OAuth2, basic auth parsing and application
- **Error Handling**: Test error detection, formatting, and propagation
- **Utility Functions**: Test all helper functions for parsing, formatting, and validation
- **Others**

Example unit test structure:

```python
def test_template_replacement():
    """Test that environment variables are correctly replaced in templates."""
    template = "Hello {{env.USER}}"
    env = {"USER": "TestUser"}
    result = replace_template(template, env=env)
    assert result == "Hello TestUser"

def test_template_missing_variable():
    """Test error handling when template variable is missing."""
    template = "Hello {{env.MISSING}}"
    with pytest.raises(TemplateError):
        replace_template(template, env={})
```

#### 2. Feature Tests

Test full features end-to-end:

- **Tool Loading**: Load JSON context file and parse all tools
- **HTTP Execution**: Make real HTTP requests to test endpoints (use mocking where appropriate)
- **CLI Execution**: Execute command-line tools and capture output
- **File Reading**: Read and parse files with template replacement
- **Error Scenarios**: Test network failures, timeouts, invalid inputs

Example feature test:

```python
def test_execute_http_tool_with_api_key():
    """Test executing an HTTP tool with API key authentication."""
    tool_def = {
        "name": "get_weather",
        "execution": {
            "type": "http",
            "method": "GET",
            "url": "https://api.example.com/weather",
            "auth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "value": "{{env.API_KEY}}"
            }
        }
    }
    env = {"API_KEY": "test-key-123"}
    result = execute_tool(tool_def, env=env, props={})
    assert result["success"] is True
```

#### 3. Manual Tests

Create manual test files for large features that should be run individually via terminal with clear output.

**Location**: `testsManual/`

**Requirements**:

- Each test file should be standalone and executable
- Provide clear, human-readable output showing what is being tested
- Include setup instructions in comments at the top of each file
- Use only the implemented modules directly, not mocks or any other deps
- Show both success and failure cases
- Avoid using private properties or methods in feature tests

### Test Organization

Organize tests in the `tests/` directory: Unit tests in `tests/unit/` mimicking `src/` directory structure; place feature tests directly under `tests/` directory.

Example:

```
tests/
├── test_schema.py              # Feature tests for JSON schema validation
├── test_templating.py          # Feature tests for template engine
└── unit/
    ├── test_mcipy.py
    ├── test_init.py
    └── tools/
        ├── test_http_executor.py
        └── test_file_executor.py
```

## Development Workflow

### Testing Commands

```bash
# Run all automated tests
make test

# Run specific test file with output
uv run pytest -s tests/test_schema.py

# Run tests with coverage report
make coverage

# Run a manual test
uv run python testsManual/test_parsing_tools.py
```

### Linting Commands

```bash
# Run all linters and formatters
make lint

# Run individual linters
uv run ruff check --fix src/
uv run ruff format src/
uv run basedpyright --stats src/
```

### Installation

```bash
# Install all dependencies
make install

# Run sync, lint, and test in one command
make
```

## Code Style Guidelines

- Use modern Python 3.11+ features and type annotations
- Keep comments concise and explanatory (focus on WHY, not WHAT)
- Avoid obvious or redundant comments
- Use `uv` for all Python operations, not `pip` or `python` directly
