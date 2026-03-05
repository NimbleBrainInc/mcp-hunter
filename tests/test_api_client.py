"""Unit tests for the Hunter.io API client."""

import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from mcp_hunter.api_client import HunterAPIError, HunterClient


@pytest_asyncio.fixture
async def mock_client():
    """Create a HunterClient with mocked session."""
    client = HunterClient(api_key="test_key")
    client._session = AsyncMock()
    yield client
    await client.close()


class TestClientInitialization:
    """Test client creation and configuration."""

    def test_init_with_explicit_key(self):
        """Client accepts an explicit API key."""
        client = HunterClient(api_key="explicit_key")
        assert client.api_key == "explicit_key"

    def test_init_with_env_var(self):
        """Client falls back to HUNTER_API_KEY env var."""
        os.environ["HUNTER_API_KEY"] = "env_key"
        try:
            client = HunterClient()
            assert client.api_key == "env_key"
        finally:
            del os.environ["HUNTER_API_KEY"]

    def test_init_without_key_raises(self):
        """Client raises ValueError when no key is available."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove HUNTER_API_KEY if present
            os.environ.pop("HUNTER_API_KEY", None)
            with pytest.raises(ValueError, match="HUNTER_API_KEY is required"):
                HunterClient()

    def test_custom_timeout(self):
        """Client accepts a custom timeout."""
        client = HunterClient(api_key="key", timeout=60.0)
        assert client.timeout == 60.0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Client works as an async context manager."""
        async with HunterClient(api_key="test") as client:
            assert client._session is not None
        assert client._session is None


class TestClientMethods:
    """Test API client methods with mocked responses."""

    @pytest.mark.asyncio
    async def test_discover(self, mock_client):
        """Test discover endpoint (POST)."""
        mock_response = {
            "data": [{"domain": "stripe.com", "organization": "Stripe"}],
            "meta": {"results": 1},
        }
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.discover(query="fintech companies")

        assert result["data"][0]["domain"] == "stripe.com"

    @pytest.mark.asyncio
    async def test_discover_with_structured_filters(self, mock_client):
        """Test discover with structured industry/location filters."""
        mock_response = {"data": [], "meta": {"results": 0}}
        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            await mock_client.discover(
                industry={"include": ["Software Development"]},
                headquarters_location={"include": [{"country": "US"}]},
                headcount=["11-50", "51-200"],
            )
            mock_req.assert_called_once()
            call_kwargs = mock_req.call_args
            assert call_kwargs[0][0] == "POST"
            assert call_kwargs[0][1] == "/discover"

    @pytest.mark.asyncio
    async def test_domain_search(self, mock_client):
        """Test domain search endpoint."""
        mock_response = {
            "data": {
                "domain": "example.com",
                "emails": [{"value": "john@example.com", "confidence": 92}],
            }
        }
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.domain_search(domain="example.com", limit=10)

        assert result["data"]["domain"] == "example.com"
        assert len(result["data"]["emails"]) == 1

    @pytest.mark.asyncio
    async def test_domain_search_by_company(self, mock_client):
        """Test domain search with company name instead of domain."""
        mock_response = {"data": {"domain": "stripe.com", "emails": []}}
        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            await mock_client.domain_search(company="Stripe")
            args = mock_req.call_args
            assert args[1]["params"]["company"] == "Stripe"

    @pytest.mark.asyncio
    async def test_find_email(self, mock_client):
        """Test email finder endpoint."""
        mock_response = {"data": {"email": "alexis@reddit.com", "score": 97}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.find_email(
                first_name="Alexis", last_name="Ohanian", domain="reddit.com"
            )

        assert result["data"]["email"] == "alexis@reddit.com"
        assert result["data"]["score"] == 97

    @pytest.mark.asyncio
    async def test_find_email_by_linkedin(self, mock_client):
        """Test email finder with LinkedIn handle."""
        mock_response = {"data": {"email": "john@example.com", "score": 80}}
        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            await mock_client.find_email(linkedin_handle="johndoe")
            args = mock_req.call_args
            assert args[1]["params"]["linkedin_handle"] == "johndoe"

    @pytest.mark.asyncio
    async def test_verify_email(self, mock_client):
        """Test email verification endpoint."""
        mock_response = {"data": {"status": "valid", "score": 100, "email": "test@example.com"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.verify_email("test@example.com")

        assert result["data"]["status"] == "valid"
        assert result["data"]["score"] == 100

    @pytest.mark.asyncio
    async def test_enrich_person(self, mock_client):
        """Test person enrichment endpoint."""
        mock_response = {
            "data": {
                "name": {"fullName": "John Doe"},
                "employment": {"title": "CTO", "name": "Example Inc"},
            }
        }
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.enrich_person(email="john@example.com")

        assert result["data"]["name"]["fullName"] == "John Doe"

    @pytest.mark.asyncio
    async def test_enrich_company(self, mock_client):
        """Test company enrichment endpoint."""
        mock_response = {"data": {"name": "Hunter", "domain": "hunter.io", "foundedYear": 2015}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.enrich_company("hunter.io")

        assert result["data"]["name"] == "Hunter"
        assert result["data"]["foundedYear"] == 2015

    @pytest.mark.asyncio
    async def test_email_count(self, mock_client):
        """Test email count endpoint (free)."""
        mock_response = {"data": {"total": 100, "personal_emails": 80, "generic_emails": 20}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.email_count("example.com")

        assert result["data"]["total"] == 100

    @pytest.mark.asyncio
    async def test_account(self, mock_client):
        """Test account info endpoint."""
        mock_response = {"data": {"plan_name": "Starter", "email": "user@test.com"}}
        with patch.object(mock_client, "_request", return_value=mock_response):
            result = await mock_client.account()

        assert result["data"]["plan_name"] == "Starter"


class TestErrorHandling:
    """Test error handling for API errors."""

    @pytest.mark.asyncio
    async def test_401_unauthorized(self, mock_client):
        """Test handling of unauthorized errors."""
        with patch.object(
            mock_client,
            "_request",
            side_effect=HunterAPIError(401, "Invalid API key"),
        ):
            with pytest.raises(HunterAPIError) as exc_info:
                await mock_client.domain_search(domain="example.com")
            assert exc_info.value.status == 401
            assert "Invalid API key" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_429_rate_limit(self, mock_client):
        """Test handling of rate limit errors."""
        with patch.object(
            mock_client,
            "_request",
            side_effect=HunterAPIError(429, "Rate limit exceeded"),
        ):
            with pytest.raises(HunterAPIError) as exc_info:
                await mock_client.find_email(first_name="John", last_name="Doe", domain="x.com")
            assert exc_info.value.status == 429

    @pytest.mark.asyncio
    async def test_422_invalid_params(self, mock_client):
        """Test handling of validation errors."""
        with patch.object(
            mock_client,
            "_request",
            side_effect=HunterAPIError(422, "Domain is required"),
        ):
            with pytest.raises(HunterAPIError) as exc_info:
                await mock_client.domain_search()
            assert exc_info.value.status == 422

    @pytest.mark.asyncio
    async def test_network_error(self, mock_client):
        """Test handling of network errors."""
        with patch.object(
            mock_client,
            "_request",
            side_effect=HunterAPIError(500, "Network error: Connection failed"),
        ):
            with pytest.raises(HunterAPIError) as exc_info:
                await mock_client.account()
            assert exc_info.value.status == 500
            assert "Network error" in exc_info.value.message

    def test_error_string_representation(self):
        """Test HunterAPIError string format."""
        err = HunterAPIError(401, "Unauthorized", {"id": "auth_error"})
        assert "401" in str(err)
        assert "Unauthorized" in str(err)
        assert err.details == {"id": "auth_error"}
