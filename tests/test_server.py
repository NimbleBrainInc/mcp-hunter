"""Tests for Hunter.io MCP Server tools and skill resource."""

from unittest.mock import patch

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_hunter.api_client import HunterAPIError
from mcp_hunter.server import SKILL_CONTENT


class TestSkillResource:
    """Test the skill resource and server instructions."""

    @pytest.mark.asyncio
    async def test_initialize_returns_instructions(self, mcp_server):
        """Server instructions reference the skill resource."""
        async with Client(mcp_server) as client:
            result = await client.initialize()
            assert result.instructions is not None
            assert "skill://hunter/usage" in result.instructions

    @pytest.mark.asyncio
    async def test_skill_resource_listed(self, mcp_server):
        """skill://hunter/usage appears in resource listing."""
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            uris = [str(r.uri) for r in resources]
            assert "skill://hunter/usage" in uris

    @pytest.mark.asyncio
    async def test_skill_resource_readable(self, mcp_server):
        """Reading the skill resource returns the full skill content."""
        async with Client(mcp_server) as client:
            contents = await client.read_resource("skill://hunter/usage")
            text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])
            assert "discover_companies" in text
            assert "verify_email" in text
            assert "Context Reuse" in text

    @pytest.mark.asyncio
    async def test_skill_content_matches_constant(self, mcp_server):
        """Resource content matches the SKILL_CONTENT constant."""
        async with Client(mcp_server) as client:
            contents = await client.read_resource("skill://hunter/usage")
            text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])
            assert text == SKILL_CONTENT


class TestToolListing:
    """Test that all tools are registered and discoverable."""

    @pytest.mark.asyncio
    async def test_all_tools_listed(self, mcp_server):
        """All 7 tools appear in tool listing."""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            names = {t.name for t in tools}
            expected = {
                "discover_companies",
                "search_domain_emails",
                "find_email",
                "verify_email",
                "enrich_person",
                "enrich_company",
                "check_account",
            }
            assert expected == names


class TestMCPTools:
    """Test the MCP server tools via FastMCP Client."""

    @pytest.mark.asyncio
    async def test_discover_companies(self, mcp_server, mock_client):
        """Test discover_companies tool."""
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "discover_companies", {"query": "Tech companies in Europe"}
                )
            assert result is not None
            mock_client.discover.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_domain_emails(self, mcp_server, mock_client):
        """Test search_domain_emails tool."""
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("search_domain_emails", {"domain": "example.com"})
            assert result is not None
            mock_client.domain_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_email(self, mcp_server, mock_client):
        """Test find_email tool."""
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool(
                    "find_email",
                    {"first_name": "John", "last_name": "Doe", "domain": "example.com"},
                )
            assert result is not None
            mock_client.find_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email(self, mcp_server, mock_client):
        """Test verify_email tool."""
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("verify_email", {"email": "john@example.com"})
            assert result is not None
            mock_client.verify_email.assert_called_once_with("john@example.com")

    @pytest.mark.asyncio
    async def test_enrich_person(self, mcp_server, mock_client):
        """Test enrich_person tool."""
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("enrich_person", {"email": "john@example.com"})
            assert result is not None
            mock_client.enrich_person.assert_called_once()

    @pytest.mark.asyncio
    async def test_enrich_company(self, mcp_server, mock_client):
        """Test enrich_company tool."""
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("enrich_company", {"domain": "example.com"})
            assert result is not None
            mock_client.enrich_company.assert_called_once_with("example.com")

    @pytest.mark.asyncio
    async def test_check_account(self, mcp_server, mock_client):
        """Test check_account tool."""
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                result = await client.call_tool("check_account", {})
            assert result is not None
            mock_client.account.assert_called_once()

    @pytest.mark.asyncio
    async def test_discover_api_error(self, mcp_server, mock_client):
        """Test discover_companies handles API errors."""
        mock_client.discover.side_effect = HunterAPIError(401, "Unauthorized")
        with patch("mcp_hunter.server.get_client", return_value=mock_client):
            async with Client(mcp_server) as client:
                with pytest.raises(ToolError, match="401"):
                    await client.call_tool("discover_companies", {"query": "test"})
