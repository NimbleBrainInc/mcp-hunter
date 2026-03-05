"""
Smoke test: verify the LLM reads the skill resource and selects the correct tool.

Requires ANTHROPIC_API_KEY and HUNTER_API_KEY in environment.
"""

import os

import anthropic
import pytest
from fastmcp import Client

from mcp_hunter.server import mcp


def get_anthropic_client() -> anthropic.Anthropic:
    token = os.environ.get("ANTHROPIC_API_KEY")
    if not token:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=token)


async def get_server_context() -> dict:
    """Extract instructions, skill content, and tool definitions from the MCP server."""
    async with Client(mcp) as client:
        init = await client.initialize()
        instructions = init.instructions

        resources = await client.list_resources()
        skill_text = ""
        for r in resources:
            if "skill://" in str(r.uri):
                contents = await client.read_resource(str(r.uri))
                skill_text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])

        tools_list = await client.list_tools()
        tools = []
        for t in tools_list:
            tool_def = {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema,
            }
            tools.append(tool_def)

        return {
            "instructions": instructions,
            "skill": skill_text,
            "tools": tools,
        }


class TestSkillLLMInvocation:
    """Test that an LLM reads the skill and makes correct tool choices."""

    @pytest.mark.asyncio
    async def test_find_person_email_selects_find_email(self):
        """When asked to find someone's email, the LLM should call find_email.

        The skill teaches: use find_email when you know a person's name and company.
        """
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an email intelligence assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": "Find the email for John Doe at stripe.com"}],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"

        tool_name = tool_calls[0].name
        assert tool_name == "find_email", (
            f"LLM called {tool_name} instead of find_email. "
            "Skill instructs: use find_email when you know name + domain."
        )

    @pytest.mark.asyncio
    async def test_company_research_selects_enrich_company(self):
        """When asked to research a company, the LLM should call enrich_company.

        The skill's 'Research a Company' workflow starts with enrich_company.
        """
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an email intelligence assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[
                {"role": "user", "content": "Tell me about stripe.com — what industry are they in?"}
            ],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"

        tool_name = tool_calls[0].name
        assert tool_name == "enrich_company", (
            f"LLM called {tool_name} instead of enrich_company. "
            "Skill instructs: use enrich_company to research a company."
        )

    @pytest.mark.asyncio
    async def test_discover_companies_for_prospecting(self):
        """When asked to find companies, the LLM should call discover_companies.

        The skill's 'Prospect a Company' workflow starts with discover_companies.
        """
        ctx = await get_server_context()
        client = get_anthropic_client()

        system = (
            f"You are an email intelligence assistant.\n\n"
            f"## Server Instructions\n{ctx['instructions']}\n\n"
            f"## Skill Resource\n{ctx['skill']}"
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[
                {"role": "user", "content": "Find SaaS companies in Germany with 50-200 employees"}
            ],
            tools=[{"type": "custom", **t} for t in ctx["tools"]],
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        assert len(tool_calls) > 0, "LLM did not call any tool"

        tool_name = tool_calls[0].name
        assert tool_name == "discover_companies", (
            f"LLM called {tool_name} instead of discover_companies. "
            "Skill instructs: use discover_companies for prospecting."
        )
