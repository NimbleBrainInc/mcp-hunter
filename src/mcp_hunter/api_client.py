"""Async HTTP client for Hunter.io API v2."""

import os
from typing import Any

import aiohttp
from aiohttp import ClientError


class HunterAPIError(Exception):
    """Exception raised for Hunter.io API errors."""

    def __init__(self, status: int, message: str, details: dict[str, Any] | None = None) -> None:
        self.status = status
        self.message = message
        self.details = details
        super().__init__(f"Hunter API Error {status}: {message}")


class HunterClient:
    """Async client for Hunter.io API v2."""

    BASE_URL = "https://api.hunter.io/v2"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("HUNTER_API_KEY")
        if not self.api_key:
            raise ValueError("HUNTER_API_KEY is required")
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "HunterClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _ensure_session(self) -> None:
        if not self._session:
            headers = {
                "User-Agent": "mcp-server-hunter/0.1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key or "",
            }
            self._session = aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: Any | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Hunter.io API."""
        await self._ensure_session()
        url = f"{self.BASE_URL}{path}"

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            if not self._session:
                raise RuntimeError("Session not initialized")

            kwargs: dict[str, Any] = {}
            if json_data is not None:
                kwargs["json"] = json_data
            if params:
                kwargs["params"] = params

            async with self._session.request(method, url, **kwargs) as response:
                result = await response.json()

                if response.status >= 400:
                    error_msg = "Unknown error"
                    if isinstance(result, dict) and "errors" in result:
                        errors = result["errors"]
                        if isinstance(errors, list) and errors:
                            error_msg = errors[0].get("details", str(errors[0]))
                        elif isinstance(errors, dict):
                            error_msg = str(errors)

                    raise HunterAPIError(response.status, error_msg, result)

                return result

        except ClientError as e:
            raise HunterAPIError(500, f"Network error: {str(e)}") from e

    # ========================================================================
    # Discover
    # ========================================================================

    async def discover(
        self,
        query: str | None = None,
        organization: dict | None = None,
        headquarters_location: dict | None = None,
        industry: dict | None = None,
        headcount: list[str] | None = None,
        company_type: dict | None = None,
        year_founded: dict | None = None,
        keywords: dict | None = None,
        technology: dict | None = None,
        funding: dict | None = None,
        similar_to: dict | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Discover companies matching criteria."""
        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if organization:
            body["organization"] = organization
        if headquarters_location:
            body["headquarters_location"] = headquarters_location
        if industry:
            body["industry"] = industry
        if headcount:
            body["headcount"] = headcount
        if company_type:
            body["company_type"] = company_type
        if year_founded:
            body["year_founded"] = year_founded
        if keywords:
            body["keywords"] = keywords
        if technology:
            body["technology"] = technology
        if funding:
            body["funding"] = funding
        if similar_to:
            body["similar_to"] = similar_to
        if limit:
            body["limit"] = limit
        if offset:
            body["offset"] = offset
        return await self._request("POST", "/discover", json_data=body)

    # ========================================================================
    # Domain Search
    # ========================================================================

    async def domain_search(
        self,
        domain: str | None = None,
        company: str | None = None,
        limit: int = 10,
        offset: int = 0,
        type: str | None = None,
        seniority: str | None = None,
        department: str | None = None,
    ) -> dict[str, Any]:
        """Search for email addresses by domain or company name."""
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        if domain:
            params["domain"] = domain
        if company:
            params["company"] = company
        if type:
            params["type"] = type
        if seniority:
            params["seniority"] = seniority
        if department:
            params["department"] = department
        return await self._request("GET", "/domain-search", params=params)

    # ========================================================================
    # Email Finder
    # ========================================================================

    async def find_email(
        self,
        domain: str | None = None,
        company: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        full_name: str | None = None,
        linkedin_handle: str | None = None,
        max_duration: int | None = None,
    ) -> dict[str, Any]:
        """Find the most likely email address for a person."""
        params: dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        if company:
            params["company"] = company
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if full_name:
            params["full_name"] = full_name
        if linkedin_handle:
            params["linkedin_handle"] = linkedin_handle
        if max_duration:
            params["max_duration"] = max_duration
        return await self._request("GET", "/email-finder", params=params)

    # ========================================================================
    # Email Verifier
    # ========================================================================

    async def verify_email(self, email: str) -> dict[str, Any]:
        """Verify the deliverability of an email address."""
        return await self._request("GET", "/email-verifier", params={"email": email})

    # ========================================================================
    # Enrichment
    # ========================================================================

    async def enrich_person(
        self,
        email: str | None = None,
        linkedin_handle: str | None = None,
    ) -> dict[str, Any]:
        """Get person information from email or LinkedIn handle."""
        params: dict[str, Any] = {}
        if email:
            params["email"] = email
        if linkedin_handle:
            params["linkedin_handle"] = linkedin_handle
        return await self._request("GET", "/people/find", params=params)

    async def enrich_company(self, domain: str) -> dict[str, Any]:
        """Get company information from domain."""
        return await self._request("GET", "/companies/find", params={"domain": domain})

    # ========================================================================
    # Email Count (Free)
    # ========================================================================

    async def email_count(self, domain: str) -> dict[str, Any]:
        """Get email count for a domain (free, no credits)."""
        return await self._request("GET", "/email-count", params={"domain": domain})

    # ========================================================================
    # Account (Free)
    # ========================================================================

    async def account(self) -> dict[str, Any]:
        """Get account information and remaining credits."""
        return await self._request("GET", "/account")
