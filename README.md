# Hunter.io MCP Server

[![mpak](https://img.shields.io/badge/mpak-registry-blue)](https://mpak.dev/packages/@nimblebraininc/hunter?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)
[![NimbleBrain](https://img.shields.io/badge/NimbleBrain-nimblebrain.ai-purple)](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)
[![Discord](https://img.shields.io/badge/Discord-community-5865F2)](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An [MCP](https://modelcontextprotocol.io) server that provides access to the Hunter.io API, enabling AI assistants to discover, verify, and enrich email addresses and company data.

**[View on mpak registry](https://mpak.dev/packages/@nimblebraininc/hunter?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)** | **Built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)**

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
mpak install @nimblebraininc/hunter
```

### Claude Code

```bash
claude mcp add hunter -- mpak run @nimblebraininc/hunter
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

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

See the [mpak registry page](https://mpak.dev/packages/@nimblebraininc/hunter?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter) for full install options.

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

Get your API key at [hunter.io/api-keys](https://hunter.io/api-keys), then configure it:

```bash
mpak config set @nimblebraininc/hunter api_key=your_api_key_here
```

## Tools

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

## About

Hunter.io MCP Server is published on the [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter) and built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter). mpak is an open registry for [Model Context Protocol](https://modelcontextprotocol.io) servers.

- [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)
- [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)
- [MCP specification](https://modelcontextprotocol.io)
- [Discord community](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-hunter)

## License

MIT
