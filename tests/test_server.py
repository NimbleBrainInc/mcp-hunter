"""Tests for Hunter.io MCP Server tools."""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_hunter.api_client import HunterAPIError


@pytest.fixture
def mock_client():
    """Create a mock API client."""
    client = AsyncMock()
    client.discover = AsyncMock(
        return_value={
            "data": [{"domain": "example.com", "organization": "Example"}],
            "meta": {"results": 1},
        }
    )
    client.domain_search = AsyncMock(
        return_value={
            "data": {
                "domain": "example.com",
                "emails": [{"value": "john@example.com", "confidence": 90}],
            },
        }
    )
    client.find_email = AsyncMock(
        return_value={
            "data": {"email": "john@example.com", "score": 95},
        }
    )
    client.verify_email = AsyncMock(
        return_value={
            "data": {"status": "valid", "score": 100, "email": "john@example.com"},
        }
    )
    client.enrich_person = AsyncMock(
        return_value={
            "data": {"name": {"fullName": "John Doe"}, "email": "john@example.com"},
        }
    )
    client.enrich_company = AsyncMock(
        return_value={
            "data": {"name": "Example Inc", "domain": "example.com"},
        }
    )
    client.account = AsyncMock(
        return_value={
            "data": {"plan_name": "Starter", "email": "user@test.com"},
        }
    )
    return client


@pytest.mark.asyncio
async def test_discover_companies(mock_client):
    """Test discover_companies tool."""
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import discover_companies

        result = await discover_companies(query="Tech companies in Europe")
        assert "data" in result
        mock_client.discover.assert_called_once()


@pytest.mark.asyncio
async def test_search_domain_emails(mock_client):
    """Test search_domain_emails tool."""
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import search_domain_emails

        result = await search_domain_emails(domain="example.com")
        assert "data" in result
        mock_client.domain_search.assert_called_once()


@pytest.mark.asyncio
async def test_find_email(mock_client):
    """Test find_email tool."""
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import find_email

        result = await find_email(first_name="John", last_name="Doe", domain="example.com")
        assert "data" in result
        mock_client.find_email.assert_called_once()


@pytest.mark.asyncio
async def test_verify_email(mock_client):
    """Test verify_email tool."""
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import verify_email

        result = await verify_email(email="john@example.com")
        assert "data" in result
        mock_client.verify_email.assert_called_once_with("john@example.com")


@pytest.mark.asyncio
async def test_enrich_person(mock_client):
    """Test enrich_person tool."""
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import enrich_person

        result = await enrich_person(email="john@example.com")
        assert "data" in result
        mock_client.enrich_person.assert_called_once()


@pytest.mark.asyncio
async def test_enrich_company(mock_client):
    """Test enrich_company tool."""
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import enrich_company

        result = await enrich_company(domain="example.com")
        assert "data" in result
        mock_client.enrich_company.assert_called_once_with("example.com")


@pytest.mark.asyncio
async def test_check_account(mock_client):
    """Test check_account tool."""
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import check_account

        result = await check_account()
        assert "data" in result
        mock_client.account.assert_called_once()


@pytest.mark.asyncio
async def test_discover_api_error(mock_client):
    """Test discover_companies handles API errors."""
    mock_client.discover = AsyncMock(side_effect=HunterAPIError(401, "Unauthorized"))
    with patch("mcp_hunter.server.get_client", return_value=mock_client):
        from mcp_hunter.server import discover_companies

        with pytest.raises(HunterAPIError):
            await discover_companies(query="test")
