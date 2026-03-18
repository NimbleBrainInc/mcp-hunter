"""
Shared fixtures and configuration for integration tests.

These tests require a valid HUNTER_API_KEY environment variable.
They make real API calls to Hunter.io and should not be run in CI without proper setup.
"""

import os

import pytest
import pytest_asyncio

from mcp_hunter.api_client import HunterClient


def pytest_configure(config):
    """Check for required environment variables before running tests."""
    if not os.environ.get("HUNTER_API_KEY"):
        pytest.exit(
            "ERROR: HUNTER_API_KEY environment variable is required.\n"
            "Set it before running integration tests:\n"
            "  export HUNTER_API_KEY=your_key_here\n"
            "  make test-integration"
        )


@pytest.fixture
def api_key() -> str:
    """Get the Hunter API key from environment."""
    key = os.environ.get("HUNTER_API_KEY")
    if not key:
        pytest.skip("HUNTER_API_KEY not set")
    return key


@pytest_asyncio.fixture
async def client(api_key: str) -> HunterClient:
    """Create a Hunter client for testing."""
    client = HunterClient(api_key=api_key)
    yield client
    await client.close()


class TestDomains:
    """Well-known domains for testing."""

    # Large companies — reliable email data
    GOOGLE = "google.com"
    STRIPE = "stripe.com"
    HUNTER = "hunter.io"

    # Known tech companies
    GITHUB = "github.com"
    CLOUDFLARE = "cloudflare.com"

    # Batch list for testing
    BATCH = [GOOGLE, STRIPE, HUNTER]


@pytest.fixture
def test_domains() -> type[TestDomains]:
    """Provide test domain constants."""
    return TestDomains
