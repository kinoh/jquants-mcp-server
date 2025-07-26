# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides access to the free J-Quants API for Japanese stock market data. The server exposes three main tools:
- `search_company`: Search for listed stocks by company name (Japanese text search)
- `get_daily_quotes`: Retrieve daily stock price data for a specific stock code
- `get_financial_statements`: Retrieve financial statements for a specific stock code

## Architecture

The project follows a simple structure:
- `src/jquants_free_mcp_server/server.py`: Main server implementation using FastMCP
- `src/jquants_free_mcp_server/__init__.py`: Package entry point
- Single MCP tools are implemented as async functions decorated with `@mcp_server.tool()`

## Technology Stack

- **Python**: >=3.13 required
- **MCP Framework**: Uses FastMCP from the `mcp` library
- **HTTP Client**: Uses `httpx` for async HTTP requests to J-Quants API
- **Authentication**: Bearer token authentication using `JQUANTS_ID_TOKEN` environment variable
- **Build System**: Uses `hatchling` as the build backend
- **Package Manager**: Project is designed to work with `uv`

## Development Commands

This project uses [Task](https://taskfile.dev/) for command management. Install Task and then use these commands:

### Quick Start
```bash
# Setup development environment
task setup:env

# Run tests
task test

# Run the server
task run
```

### Available Commands
```bash
# Development
task install          # Install dependencies
task run              # Run MCP server locally
task run:package      # Run as installed package
task dev              # Run in development mode

# Testing and Quality
task test             # Run unit tests (verbose)
task test:quick       # Run tests (minimal output)
task lint             # Run code formatting/linting
task check            # Run all checks (tests + lint)

# Building and Release
task build            # Build the package
task clean            # Clean build artifacts
task release          # Full release build

# Utilities
task help             # Show all available tasks
```

### Environment Setup
1. Create a `.env` file with your J-Quants API token:
   ```
   JQUANTS_ID_TOKEN=your_token_here
   ```
2. Run `task setup:env` to install dependencies

### Manual Commands (if Task is not available)
```bash
# Install dependencies
uv sync --extra dev

# Run tests
JQUANTS_ID_TOKEN=your_token_here uv run python -m pytest tests/ -v

# Run server
uv run python src/jquants_free_mcp_server/server.py

# Build package
uv build
```

## Key Implementation Details

### Error Handling
The `make_requests` function implements comprehensive error handling for:
- Missing ID token
- HTTP request failures
- Non-JSON responses
- Timeout errors
- Connection errors
- HTTP status errors

### API Integration
- Base URL: `https://api.jquants.com/v1/`
- Authentication: Bearer token in Authorization header
- Data limitation: 2 years prior to today up until 12 weeks ago
- Response format: JSON with proper Japanese character encoding (`ensure_ascii=False`)

### Tool Parameters
All tools support pagination through `limit` and `start_position` parameters. The search functionality includes case-insensitive matching for both Japanese and English company names.

## Testing and Quality

No test framework is currently configured in the project. Consider adding pytest for future development:
```bash
uv add --dev pytest
uv run pytest
```

No linting tools are configured. Consider adding ruff for code quality:
```bash
uv add --dev ruff
uv run ruff check
uv run ruff format
```