"""
Core tools integration tests.

Tests basic Hunter.io API functionality with real API calls.
Note: Some tests consume credits. Run sparingly.
"""

import pytest
from conftest import TestDomains

from mcp_hunter.api_client import HunterAPIError, HunterClient


async def has_discover_access(client: HunterClient) -> bool:
    """Check if the plan supports the Discover endpoint."""
    try:
        await client.discover(query="test", limit=1)
        return True
    except HunterAPIError as e:
        if e.status == 400 and "limited" in e.message.lower():
            return False
        raise


class TestDiscover:
    """Test the Discover endpoint (free, but requires a qualifying plan)."""

    @pytest.mark.asyncio
    async def test_discover_by_query(self, client: HunterClient):
        """Test natural language discovery."""
        if not await has_discover_access(client):
            pytest.skip("Discover endpoint requires a qualifying plan")
        result = await client.discover(query="SaaS companies in San Francisco", limit=5)

        assert "data" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

        company = result["data"][0]
        assert "domain" in company
        print(f"Discovered: {company.get('organization', 'N/A')} ({company['domain']})")

    @pytest.mark.asyncio
    async def test_discover_by_industry(self, client: HunterClient):
        """Test structured industry filter."""
        if not await has_discover_access(client):
            pytest.skip("Discover endpoint requires a qualifying plan")
        result = await client.discover(
            industry={"include": ["Software Development"]},
            headcount=["51-200"],
            limit=3,
        )

        assert "data" in result
        assert isinstance(result["data"], list)
        print(f"Found {len(result['data'])} companies in Software Development (51-200)")

    @pytest.mark.asyncio
    async def test_discover_pagination(self, client: HunterClient):
        """Test discover with pagination."""
        if not await has_discover_access(client):
            pytest.skip("Discover endpoint requires a qualifying plan")
        page1 = await client.discover(query="tech companies", limit=2, offset=0)
        page2 = await client.discover(query="tech companies", limit=2, offset=2)

        assert "data" in page1
        assert "data" in page2
        # Pages should have different results (unless very few total)
        if len(page1["data"]) > 0 and len(page2["data"]) > 0:
            assert page1["data"][0].get("domain") != page2["data"][0].get("domain")


class TestDomainSearch:
    """Test domain search (costs 1 credit / 10 emails)."""

    @pytest.mark.asyncio
    async def test_search_known_domain(self, client: HunterClient):
        """Test searching a well-known domain."""
        result = await client.domain_search(domain=TestDomains.HUNTER, limit=5)

        assert "data" in result
        data = result["data"]
        assert data["domain"] == TestDomains.HUNTER
        assert "emails" in data
        assert len(data["emails"]) > 0

        email = data["emails"][0]
        assert "value" in email
        assert "confidence" in email
        print(f"Found {len(data['emails'])} emails at {TestDomains.HUNTER}")

    @pytest.mark.asyncio
    async def test_search_with_filters(self, client: HunterClient):
        """Test domain search with department/seniority filters."""
        result = await client.domain_search(
            domain=TestDomains.GOOGLE,
            seniority="executive",
            limit=3,
        )

        assert "data" in result
        print(f"Found {len(result['data'].get('emails', []))} executive emails at Google")


class TestEmailVerification:
    """Test email verification (costs 0.5 credits)."""

    @pytest.mark.asyncio
    async def test_verify_valid_looking_email(self, client: HunterClient):
        """Test verifying an email from a known domain."""
        # First find an email to verify
        search = await client.domain_search(domain=TestDomains.HUNTER, limit=1)
        emails = search["data"].get("emails", [])
        if not emails:
            pytest.skip("No emails found to verify")

        email = emails[0]["value"]
        result = await client.verify_email(email)

        assert "data" in result
        data = result["data"]
        assert "status" in data
        assert data["status"] in (
            "valid",
            "invalid",
            "accept_all",
            "webmail",
            "disposable",
            "unknown",
        )
        assert "score" in data
        print(f"Verified {email}: status={data['status']}, score={data['score']}")


class TestEnrichment:
    """Test enrichment endpoints (cost 0.2 credits each)."""

    @pytest.mark.asyncio
    async def test_enrich_company(self, client: HunterClient):
        """Test company enrichment for a known domain."""
        result = await client.enrich_company(TestDomains.STRIPE)

        assert "data" in result
        data = result["data"]
        assert data.get("domain") == TestDomains.STRIPE or data.get("name") is not None
        print(f"Company: {data.get('name', 'N/A')}, Founded: {data.get('foundedYear', 'N/A')}")

    @pytest.mark.asyncio
    async def test_enrich_person_from_search(self, client: HunterClient):
        """Test person enrichment using an email found via search."""
        search = await client.domain_search(domain=TestDomains.HUNTER, limit=1)
        emails = search["data"].get("emails", [])
        if not emails:
            pytest.skip("No emails found for enrichment")

        email = emails[0]["value"]
        result = await client.enrich_person(email=email)

        assert "data" in result
        print(f"Enriched {email}: {result['data'].get('name', {}).get('fullName', 'N/A')}")


class TestEmailCount:
    """Test email count (free, no credits)."""

    @pytest.mark.asyncio
    async def test_email_count(self, client: HunterClient):
        """Test getting email count for a domain."""
        result = await client.email_count(TestDomains.GOOGLE)

        assert "data" in result
        data = result["data"]
        assert "total" in data
        assert data["total"] > 0
        print(f"Email count for {TestDomains.GOOGLE}: {data['total']}")


class TestAccount:
    """Test account info (free)."""

    @pytest.mark.asyncio
    async def test_get_account_info(self, client: HunterClient):
        """Test getting account information and credits."""
        result = await client.account()

        assert "data" in result
        data = result["data"]
        assert "plan_name" in data
        assert "email" in data
        print(f"Plan: {data['plan_name']}, Email: {data['email']}")
