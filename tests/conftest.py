"""Shared fixtures for unit tests."""

from unittest.mock import AsyncMock

import pytest

from mcp_hunter.server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp


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
