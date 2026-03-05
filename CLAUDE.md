# Hunter.io MCP Server

MCP server providing Hunter.io email discovery, verification, and enrichment via FastMCP.

## Architecture

```
src/mcp_hunter/
├── server.py      # MCP tools (FastMCP) + entrypoints
├── api_client.py  # Async HTTP client for Hunter.io API v2
└── api_models.py  # Pydantic models for API responses
```

## Critical

- Package name: `@nimblebraininc/hunter` (npm-style scope, matches GitHub org)
- Manifest uses module execution: `python -m mcp_hunter.server`
- Server needs both entrypoints:
  ```python
  app = mcp.http_app()  # HTTP deployment
  if __name__ == "__main__":
      mcp.run()  # Stdio for Claude Desktop / mpak
  ```
- All logs to stderr (stdout is reserved for JSON-RPC)
- Auth via `X-API-KEY` header (not query param, per Hunter.io security recommendation)

## user_config

API key configured via manifest `user_config`, not hardcoded:
```json
{
  "user_config": {
    "api_key": {
      "type": "string",
      "sensitive": true,
      "required": true
    }
  },
  "server": {
    "mcp_config": {
      "env": { "HUNTER_API_KEY": "${user_config.api_key}" }
    }
  }
}
```

## Tooling

- **Package manager**: uv (not pip)
- **Linting/formatting**: ruff (not flake8, black, isort)
- **Type checking**: ty (not mypy, pyright)
- **Testing**: pytest with pytest-asyncio

## Commands

```bash
uv sync --dev               # Install dependencies
uv run ruff format src/ tests/   # Format
uv run ruff check src/ tests/    # Lint
uv run ty check src/             # Type check
uv run pytest tests/ -v          # Test
make check                       # All of the above
```

## Version Management

Version lives in four files that MUST stay in sync:

| File | Field |
|------|-------|
| `manifest.json` | `version` |
| `server.json` | `version` |
| `pyproject.toml` | `version` |
| `src/mcp_hunter/__init__.py` | `__version__` |

Bump all at once: `make bump VERSION=0.2.0`

## Adding New Tools

1. Add response model to `api_models.py`
2. Add client method to `api_client.py`
3. Add `@mcp.tool()` function to `server.py`
4. Add tests to `tests/`
5. Run `make check` to verify
