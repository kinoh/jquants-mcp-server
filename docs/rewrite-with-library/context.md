# Rewrite with Official Python Client Library

Completely rewrite API access using https://github.com/J-Quants/jquants-api-client-python

- API Documentation: https://jpx.gitbook.io/j-quants-ja/api-reference

## Current Implementation

### Architecture
- Uses raw `httpx` for API requests
- 5 MCP tools: `search_company`, `get_daily_quotes`, `get_financial_statements`, `get_topix_prices`, `get_trades_spec`
- Authentication: Bearer token via `JQUANTS_ID_TOKEN` environment variable
- Custom error handling implementation
- Returns JSON strings

### Tool Parameters
- All tools have `limit` and `start_position` for pagination
- Date parameters as strings (YYYY-MM-DD format)

## Official Library (jquants-api-client)

### Features
- Returns pandas DataFrames
- Multiple authentication methods:
  - Email/password
  - Config file (`jquants-api.toml`)
  - Environment variables
  - Refresh token
- Date parameters as datetime objects
- Synchronous implementation

### Installation
```bash
pip install jquants-api-client
```

## Migration Design Decisions

### 1. Authentication Strategy
- Primary: Use refresh token from `JQUANTS_REFRESH_TOKEN` environment variable
- Fallback: If refresh token is missing or expired, use `JQUANTS_MAIL_ADDRESS` and `JQUANTS_PASSWORD` to obtain refresh token
- Remove dependency on `JQUANTS_ID_TOKEN`

### 2. Return Value Format
- Convert pandas DataFrame to JSON string for MCP compatibility
- Maintain current response structure with top-level keys (e.g., `{"daily_quotes": [...]}`)
- Convert DataFrame to list of dicts, then wrap with appropriate key
- Use `json.dumps({"key": df.to_dict(orient='records')}, ensure_ascii=False)`

### 3. Async/Sync Handling
- FastMCP can handle synchronous functions
- No need for `asyncio.to_thread()` wrapper

### 4. Pagination Parameters
- Keep `limit` and `start_position` parameters in MCP tools
- Apply slicing after retrieving full data from official library: `data[start_position:start_position + limit]`

## Implementation Tasks

1. Add `jquants-api-client` to dependencies
2. Implement authentication logic with refresh token + email/password fallback
3. Rewrite each tool to use official library methods
4. Convert DataFrame results to JSON strings
5. Update error handling to work with library exceptions
6. Update tests to work with new implementation
