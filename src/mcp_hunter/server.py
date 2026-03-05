"""Hunter.io MCP Server - FastMCP Implementation.

Intent-based tools for email discovery, verification, and enrichment
via the Hunter.io API v2.
"""

import logging
import os
import sys
from importlib.resources import files

from fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_hunter.api_client import HunterAPIError, HunterClient

SKILL_CONTENT = files("mcp_hunter").joinpath("SKILL.md").read_text()

# Logging setup - all logs to stderr (stdout is reserved for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_hunter")

logger.info("Hunter.io server module loading...")

# Create MCP server
mcp = FastMCP("Hunter.io", instructions=SKILL_CONTENT)

# Global client instance (lazy initialization)
_client: HunterClient | None = None


def get_client(ctx: Context | None = None) -> HunterClient:
    """Get or create the API client instance."""
    global _client
    if _client is None:
        api_key = os.environ.get("HUNTER_API_KEY")
        if not api_key:
            msg = "HUNTER_API_KEY environment variable is required"
            if ctx:
                ctx.error(msg)
            raise ValueError(msg)
        _client = HunterClient(api_key=api_key)
    return _client


# Health endpoint for HTTP transport
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-hunter"})


# ============================================================================
# Tools
# ============================================================================


@mcp.tool()
async def discover_companies(
    query: str | None = None,
    industry: list[str] | None = None,
    location_country: str | None = None,
    location_continent: str | None = None,
    headcount: list[str] | None = None,
    limit: int = 20,
    offset: int = 0,
    ctx: Context | None = None,
) -> dict:
    """Discover companies matching search criteria using AI-powered natural language or structured filters.

    Use natural language via `query` (e.g. "SaaS companies in Europe with 50-200 employees")
    or structured filters. This is free and costs no credits.

    Args:
        query: Natural language search (e.g. "Tech startups in San Francisco").
            An AI assistant will select appropriate filters for you.
        industry: Industries to include (e.g. ["Software Development", "Information Technology"])
        location_country: ISO country code to filter by (e.g. "US", "FR")
        location_continent: Continent filter (Europe, Asia, North America, etc.)
        headcount: Company sizes to include (e.g. ["1-10", "11-50", "51-200"])
        limit: Max results to return (default 20, max 100)
        offset: Number of results to skip for pagination
        ctx: MCP context for logging

    Returns:
        Companies matching criteria with domain, name, and email counts
    """
    client = get_client(ctx)
    try:
        kwargs: dict = {}
        if query:
            kwargs["query"] = query
        if industry:
            kwargs["industry"] = {"include": industry}
        if location_country or location_continent:
            loc: dict = {"include": []}
            if location_country:
                loc["include"].append({"country": location_country})
            elif location_continent:
                loc["include"].append({"continent": location_continent})
            kwargs["headquarters_location"] = loc
        if headcount:
            kwargs["headcount"] = headcount
        kwargs["limit"] = limit
        kwargs["offset"] = offset

        return await client.discover(**kwargs)
    except HunterAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def search_domain_emails(
    domain: str | None = None,
    company: str | None = None,
    department: str | None = None,
    seniority: str | None = None,
    email_type: str | None = None,
    limit: int = 10,
    offset: int = 0,
    ctx: Context | None = None,
) -> dict:
    """Find all email addresses for a company domain. Costs 1 credit per 10 emails returned.

    Provide either domain or company name (domain gives better results).

    Args:
        domain: Company website domain (e.g. "stripe.com")
        company: Company name (e.g. "Stripe"). Use domain when possible for better results.
        department: Filter by department: executive, it, finance, management, sales,
            legal, support, hr, marketing, communication, education, design, health, operations
        seniority: Filter by seniority: junior, senior, executive
        email_type: Filter by type: "personal" or "generic" (role-based)
        limit: Max emails to return (default 10, max 100)
        offset: Number of emails to skip for pagination
        ctx: MCP context for logging

    Returns:
        Email addresses with names, positions, departments, confidence scores, and sources
    """
    client = get_client(ctx)
    try:
        return await client.domain_search(
            domain=domain,
            company=company,
            limit=limit,
            offset=offset,
            type=email_type,
            seniority=seniority,
            department=department,
        )
    except HunterAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def find_email(
    first_name: str | None = None,
    last_name: str | None = None,
    full_name: str | None = None,
    domain: str | None = None,
    company: str | None = None,
    linkedin_handle: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """Find a specific person's professional email address. Costs 1 credit per successful lookup.

    Provide name + domain/company, OR a LinkedIn handle. Domain gives better results than company name.

    Args:
        first_name: Person's first name (preferred over full_name)
        last_name: Person's last name (preferred over full_name)
        full_name: Person's full name (use first_name + last_name when possible)
        domain: Company domain (e.g. "stripe.com"). Preferred over company name.
        company: Company name (e.g. "Stripe")
        linkedin_handle: LinkedIn profile handle (alternative to name+domain)
        ctx: MCP context for logging

    Returns:
        Email address with confidence score, position, and verification status
    """
    client = get_client(ctx)
    try:
        return await client.find_email(
            domain=domain,
            company=company,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            linkedin_handle=linkedin_handle,
        )
    except HunterAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def verify_email(
    email: str,
    ctx: Context | None = None,
) -> dict:
    """Verify if an email address is deliverable. Costs 0.5 credits.

    Checks MX records, SMTP server, and actual deliverability. Returns status:
    valid, invalid, accept_all, webmail, disposable, or unknown.

    Args:
        email: The email address to verify
        ctx: MCP context for logging

    Returns:
        Verification status, deliverability score, and detailed checks
    """
    client = get_client(ctx)
    try:
        return await client.verify_email(email)
    except HunterAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def enrich_person(
    email: str | None = None,
    linkedin_handle: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """Get full profile for a person from their email or LinkedIn handle. Costs 0.2 credits.

    Returns name, location, timezone, employment details, and social handles.

    Args:
        email: The person's email address
        linkedin_handle: LinkedIn profile handle (prioritized when both provided)
        ctx: MCP context for logging

    Returns:
        Person profile with name, location, employment, and social links
    """
    client = get_client(ctx)
    try:
        return await client.enrich_person(email=email, linkedin_handle=linkedin_handle)
    except HunterAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def enrich_company(
    domain: str,
    ctx: Context | None = None,
) -> dict:
    """Get detailed company information from a domain name. Costs 0.2 credits.

    Returns industry, description, location, founded year, tags, and classification.

    Args:
        domain: Company domain name (e.g. "stripe.com")
        ctx: MCP context for logging

    Returns:
        Company profile with industry, description, location, and metadata
    """
    client = get_client(ctx)
    try:
        return await client.enrich_company(domain)
    except HunterAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def check_account(
    ctx: Context | None = None,
) -> dict:
    """Check your Hunter.io account status, plan, and remaining credits. Free, no credits used.

    Args:
        ctx: MCP context for logging

    Returns:
        Account details including plan name, remaining searches and verifications
    """
    client = get_client(ctx)
    try:
        return await client.account()
    except HunterAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Resources
# ============================================================================


@mcp.resource("skill://hunter/usage")
def skill_usage() -> str:
    """Usage guide for the Hunter.io MCP server tools."""
    return SKILL_CONTENT


# ============================================================================
# Entrypoints
# ============================================================================

# ASGI app for HTTP deployment (uvicorn mcp_hunter.server:app)
app = mcp.http_app()

# Stdio entrypoint for Claude Desktop / mpak
if __name__ == "__main__":
    logger.info("Running in stdio mode")
    mcp.run()
