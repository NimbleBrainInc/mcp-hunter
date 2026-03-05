# Hunter.io MCP Server

An MCP (Model Context Protocol) server that provides access to the Hunter.io API, enabling AI assistants to discover, verify, and enrich email addresses and company data.

## Features

- **Discover companies** with AI-powered natural language search or structured filters
- **Search domain emails** — find all email addresses for a company
- **Find specific emails** by name + domain or LinkedIn handle
- **Verify email deliverability** with detailed SMTP checks
- **Enrich person profiles** from email or LinkedIn
- **Enrich company data** from domain
- **Check account credits** and usage

## Installation

### Using mpak (Recommended)

```bash
# Configure your API key
mpak config set @nimblebraininc/hunter api_key=your_api_key_here

# Run the server
mpak run @nimblebraininc/hunter
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/NimbleBrainInc/mcp-hunter.git
cd mcp-hunter

# Install dependencies with uv
uv sync

# Set your API key
export HUNTER_API_KEY=your_api_key_here

# Run the server
uv run python -m mcp_hunter.server
```

## Configuration

### Getting Your API Key

1. Go to https://hunter.io/api-keys
2. Create a new API key
3. Copy the key

### Claude Desktop Configuration

Add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "hunter": {
      "command": "mpak",
      "args": ["run", "@nimblebraininc/hunter"]
    }
  }
}
```

## Available Tools

| Tool | Description | Cost |
|------|-------------|------|
| `discover_companies` | Find companies via AI search or filters | Free |
| `search_domain_emails` | Find all emails for a domain | 1 credit / 10 emails |
| `find_email` | Find a person's email by name+domain | 1 credit |
| `verify_email` | Verify email deliverability | 0.5 credits |
| `enrich_person` | Get person profile from email/LinkedIn | 0.2 credits |
| `enrich_company` | Get company details from domain | 0.2 credits |
| `check_account` | View plan and remaining credits | Free |

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest tests/ -v

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run ty check src/

# Run all checks
make check
```

## License

MIT
