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
- **Stage 2**: Configuration & File Discovery
- **Stage 3**: CLI Command: `mci install`
- **Stage 4**: MCI-PY Integration & Tool Loading
- **Stage 5**: CLI Command: `mci list`
- **Stage 6**: CLI Command: `mci validate`
- **Stage 7**: CLI Command: `mci add`
- **Stage 8**: MCP Server Creation Infrastructure
- **Stage 9**: CLI Command: `mci run`
- **Stage 10**: Error Handling, Documentation & Final Polish

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For the full implementation plan, see [PLAN.md](PLAN.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
