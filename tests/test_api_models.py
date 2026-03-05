"""Tests for Hunter.io API models."""

from mcp_hunter.api_models import (
    AccountData,
    CompanyEnrichmentData,
    DiscoverCompany,
    DiscoverEmailsCount,
    DomainEmail,
    DomainSearchData,
    EmailCountData,
    EmailFinderData,
    EmailVerifierData,
    Meta,
    PersonEnrichmentData,
    Source,
    Verification,
)


def test_meta_model() -> None:
    """Test Meta model parsing."""
    data = {"results": 42, "limit": 10, "offset": 0}
    meta = Meta(**data)
    assert meta.results == 42
    assert meta.limit == 10
    assert meta.offset == 0


def test_source_model() -> None:
    """Test Source model parsing."""
    data = {
        "domain": "github.com",
        "uri": "http://github.com/user",
        "extracted_on": "2025-01-01",
        "last_seen_on": "2026-01-01",
        "still_on_page": True,
    }
    source = Source(**data)
    assert source.domain == "github.com"
    assert source.still_on_page is True


def test_domain_email_model() -> None:
    """Test DomainEmail model parsing."""
    data = {
        "value": "john@example.com",
        "type": "personal",
        "confidence": 92,
        "first_name": "John",
        "last_name": "Doe",
        "position": "CTO",
        "seniority": "executive",
        "department": "it",
    }
    email = DomainEmail(**data)
    assert email.value == "john@example.com"
    assert email.confidence == 92
    assert email.seniority == "executive"


def test_domain_search_data() -> None:
    """Test DomainSearchData model."""
    data = {
        "domain": "example.com",
        "pattern": "{first}",
        "organization": "Example Inc",
        "emails": [
            {"value": "john@example.com", "type": "personal", "confidence": 90},
        ],
    }
    result = DomainSearchData(**data)
    assert result.domain == "example.com"
    assert result.pattern == "{first}"
    assert len(result.emails) == 1
    assert result.emails[0].value == "john@example.com"


def test_email_finder_data() -> None:
    """Test EmailFinderData model."""
    data = {
        "email": "alexis@reddit.com",
        "score": 97,
        "domain": "reddit.com",
        "position": "Cofounder",
        "verification": {"date": "2025-01-01", "status": "valid"},
    }
    result = EmailFinderData(**data)
    assert result.email == "alexis@reddit.com"
    assert result.score == 97
    assert result.verification is not None
    assert result.verification.status == "valid"


def test_email_verifier_data() -> None:
    """Test EmailVerifierData model."""
    data = {
        "status": "valid",
        "score": 100,
        "email": "test@example.com",
        "regexp": True,
        "gibberish": False,
        "disposable": False,
        "webmail": False,
        "mx_records": True,
        "smtp_server": True,
        "smtp_check": True,
        "accept_all": False,
        "block": False,
    }
    result = EmailVerifierData(**data)
    assert result.status == "valid"
    assert result.score == 100
    assert result.mx_records is True


def test_person_enrichment_data() -> None:
    """Test PersonEnrichmentData model with camelCase aliases."""
    data = {
        "id": "abc-123",
        "name": {"fullName": "John Doe", "givenName": "John", "familyName": "Doe"},
        "email": "john@example.com",
        "location": "San Francisco, CA",
        "timeZone": "America/Los_Angeles",
        "employment": {"title": "CTO", "name": "Example Inc", "seniority": "executive"},
    }
    result = PersonEnrichmentData(**data)
    assert result.name is not None
    assert result.name.full_name == "John Doe"
    assert result.time_zone == "America/Los_Angeles"
    assert result.employment is not None
    assert result.employment.title == "CTO"


def test_company_enrichment_data() -> None:
    """Test CompanyEnrichmentData model."""
    data = {
        "name": "Hunter",
        "domain": "hunter.io",
        "description": "Email marketing company",
        "foundedYear": 2015,
        "tags": ["email marketing", "lead generation"],
    }
    result = CompanyEnrichmentData(**data)
    assert result.name == "Hunter"
    assert result.founded_year == 2015
    assert len(result.tags) == 2


def test_discover_company() -> None:
    """Test DiscoverCompany model."""
    data = {
        "domain": "hunter.io",
        "organization": "Hunter",
        "emails_count": {"personal": 23, "generic": 5, "total": 28},
    }
    result = DiscoverCompany(**data)
    assert result.domain == "hunter.io"
    assert result.emails_count is not None
    assert result.emails_count.total == 28


def test_email_count_data() -> None:
    """Test EmailCountData model."""
    data = {"total": 100, "personal_emails": 80, "generic_emails": 20}
    result = EmailCountData(**data)
    assert result.total == 100
    assert result.personal_emails == 80


def test_account_data() -> None:
    """Test AccountData model."""
    data = {
        "email": "user@example.com",
        "plan_name": "Starter",
        "reset_date": "2026-04-01",
    }
    result = AccountData(**data)
    assert result.plan_name == "Starter"


def test_verification_model() -> None:
    """Test Verification model."""
    v = Verification(date="2025-06-14", status="valid")
    assert v.status == "valid"
    assert v.date == "2025-06-14"


def test_discover_emails_count() -> None:
    """Test DiscoverEmailsCount model."""
    ec = DiscoverEmailsCount(personal=10, generic=3, total=13)
    assert ec.total == 13
