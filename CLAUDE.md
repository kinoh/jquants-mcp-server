# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides access to the J-Quants API for Japanese stock market data (supports both free and paid plans). The server exposes 22 tools covering all major J-Quants API endpoints:

### Company & Price Data
- `search_company`: Search for listed stocks by company name (Japanese text search)
- `get_daily_quotes`: Retrieve daily stock price data for a specific stock code
- `get_prices_prices_am`: Retrieve morning session prices

### Market Indices
- `get_topix_prices`: Retrieve daily TOPIX (Tokyo Stock Price Index) price data
- `get_indices`: Retrieve index OHLC data

### Financial Statements & Dividends
- `get_financial_statements`: Retrieve financial statements for a specific stock code
- `get_fins_announcement`: Retrieve earnings announcement schedule
- `get_fins_dividend`: Retrieve dividend information
- `get_fins_fs_details`: Retrieve detailed financial statements

### Trading & Market Data
- `get_trades_spec`: Retrieve trading by type of investors data
- `get_markets_breakdown`: Retrieve trading breakdown data
- `get_markets_daily_margin_interest`: Retrieve daily margin trading balance
- `get_markets_weekly_margin_interest`: Retrieve weekly margin trading balance
- `get_markets_short_selling`: Retrieve sector-wise short selling ratio
- `get_markets_short_selling_positions`: Retrieve short selling positions report

### Derivatives
- `get_derivatives_futures`: Retrieve futures OHLC data
- `get_derivatives_options`: Retrieve options OHLC data
- `get_option_index_option`: Retrieve Nikkei 225 options OHLC data

## Architecture

The project follows a simple structure:
- `src/jquants_mcp_server/server.py`: Main server implementation using FastMCP
- `src/jquants_mcp_server/__init__.py`: Package entry point
- Single MCP tools are implemented as async functions decorated with `@mcp_server.tool()`

## Technology Stack

- **Python**: >=3.13 required
- **MCP Framework**: Uses FastMCP from the `mcp` library
- **HTTP Client**: Uses `httpx` for async HTTP requests to J-Quants API
- **Authentication**: Uses `jquantsapi` library client with either `JQUANTS_REFRESH_TOKEN` or `JQUANTS_MAIL_ADDRESS`/`JQUANTS_PASSWORD`
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
1. Create a `.env` file with your J-Quants API credentials (choose one method):
   ```
   # Method 1: Using refresh token (recommended)
   JQUANTS_REFRESH_TOKEN=your_refresh_token_here

   # Method 2: Using email and password
   JQUANTS_MAIL_ADDRESS=your_email@example.com
   JQUANTS_PASSWORD=your_password_here
   ```
2. Run `task setup:env` to install dependencies

### Manual Commands (if Task is not available)
```bash
# Install dependencies
uv sync --extra dev

# Run tests (set authentication env vars as needed)
uv run python -m pytest tests/ -v

# Run server
uv run python src/jquants_mcp_server/server.py

# Build package
uv build
```

## Key Implementation Details

### Error Handling
The `get_client` function implements comprehensive error handling for:
- Missing authentication credentials
- Invalid refresh token
- Authentication failures

### API Integration
- Uses official `jquantsapi` Python library for API access
- Authentication: Either refresh token or email/password credentials
- Data availability varies by plan:
  - Free plan: Past 2 years
  - Light plan: Past 5 years
  - Standard plan: Past 10 years  
  - Premium plan: All available historical data
- Response format: JSON converted from pandas DataFrame with proper Japanese character encoding (`ensure_ascii=False`)

### Tool Parameters
All tools support pagination through `limit` and `start_position` parameters. The search functionality includes case-insensitive matching for both Japanese and English company names.

## Testing and Quality

The project uses pytest for testing and ruff for code quality:

```bash
# Run tests
task test              # Run with verbose output
task test:quick        # Run with minimal output

# Run linting and formatting
task lint              # Format code with ruff

# Run all checks
task check             # Run tests + linting
```