"""Pydantic models for Hunter.io API responses."""

from pydantic import BaseModel, Field

# ============================================================================
# Common Models
# ============================================================================


class Meta(BaseModel):
    """Pagination/meta information from Hunter API."""

    results: int | None = Field(default=None, description="Total results available")
    limit: int | None = Field(default=None, description="Results per page")
    offset: int | None = Field(default=None, description="Current offset")
    params: dict | None = Field(default=None, description="Echoed request params")
    filters: dict | None = Field(default=None, description="Applied filters (Discover)")


class Source(BaseModel):
    """A source where an email was found."""

    domain: str | None = Field(default=None)
    uri: str | None = Field(default=None)
    extracted_on: str | None = Field(default=None)
    last_seen_on: str | None = Field(default=None)
    still_on_page: bool | None = Field(default=None)


class Verification(BaseModel):
    """Email verification status."""

    date: str | None = Field(default=None)
    status: str | None = Field(default=None)


# ============================================================================
# Domain Search Models
# ============================================================================


class DomainEmail(BaseModel):
    """An email found via domain search."""

    value: str | None = Field(default=None, description="Email address")
    type: str | None = Field(default=None, description="personal or generic")
    confidence: int | None = Field(default=None, description="Confidence score 0-100")
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    position: str | None = Field(default=None)
    seniority: str | None = Field(default=None)
    department: str | None = Field(default=None)
    linkedin: str | None = Field(default=None)
    twitter: str | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    sources: list[Source] = Field(default_factory=list)
    verification: Verification | None = Field(default=None)


class DomainSearchData(BaseModel):
    """Data from a domain search response."""

    domain: str | None = Field(default=None)
    disposable: bool | None = Field(default=None)
    webmail: bool | None = Field(default=None)
    accept_all: bool | None = Field(default=None)
    pattern: str | None = Field(default=None, description="Email pattern e.g. {first}")
    organization: str | None = Field(default=None)
    emails: list[DomainEmail] = Field(default_factory=list)
    linked_domains: list[str] = Field(default_factory=list)


# ============================================================================
# Email Finder Models
# ============================================================================


class EmailFinderData(BaseModel):
    """Data from email finder response."""

    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    email: str | None = Field(default=None)
    score: int | None = Field(default=None, description="Confidence score 0-100")
    domain: str | None = Field(default=None)
    accept_all: bool | None = Field(default=None)
    position: str | None = Field(default=None)
    twitter: str | None = Field(default=None)
    linkedin_url: str | None = Field(default=None)
    phone_number: str | None = Field(default=None)
    company: str | None = Field(default=None)
    sources: list[Source] = Field(default_factory=list)
    verification: Verification | None = Field(default=None)


# ============================================================================
# Email Verifier Models
# ============================================================================


class EmailVerifierData(BaseModel):
    """Data from email verification response."""

    status: str | None = Field(
        default=None, description="valid/invalid/accept_all/webmail/disposable/unknown"
    )
    result: str | None = Field(
        default=None, description="deliverable/undeliverable/risky (deprecated)"
    )
    score: int | None = Field(default=None, description="Deliverability score 0-100")
    email: str | None = Field(default=None)
    regexp: bool | None = Field(default=None)
    gibberish: bool | None = Field(default=None)
    disposable: bool | None = Field(default=None)
    webmail: bool | None = Field(default=None)
    mx_records: bool | None = Field(default=None)
    smtp_server: bool | None = Field(default=None)
    smtp_check: bool | None = Field(default=None)
    accept_all: bool | None = Field(default=None)
    block: bool | None = Field(default=None)
    sources: list[Source] = Field(default_factory=list)


# ============================================================================
# Enrichment Models
# ============================================================================


class PersonName(BaseModel):
    """Person name from enrichment."""

    model_config = {"populate_by_name": True}

    full_name: str | None = Field(default=None, alias="fullName")
    given_name: str | None = Field(default=None, alias="givenName")
    family_name: str | None = Field(default=None, alias="familyName")


class Geo(BaseModel):
    """Geographic location."""

    model_config = {"populate_by_name": True}

    city: str | None = Field(default=None)
    state: str | None = Field(default=None)
    state_code: str | None = Field(default=None, alias="stateCode")
    country: str | None = Field(default=None)
    country_code: str | None = Field(default=None, alias="countryCode")
    lat: float | None = Field(default=None)
    lng: float | None = Field(default=None)


class Employment(BaseModel):
    """Employment info from enrichment."""

    domain: str | None = Field(default=None)
    name: str | None = Field(default=None)
    title: str | None = Field(default=None)
    role: str | None = Field(default=None)
    seniority: str | None = Field(default=None)


class SocialHandle(BaseModel):
    """Social media handle."""

    handle: str | None = Field(default=None)


class PersonEnrichmentData(BaseModel):
    """Data from person/email enrichment."""

    model_config = {"populate_by_name": True}

    id: str | None = Field(default=None)
    name: PersonName | None = Field(default=None)
    email: str | None = Field(default=None)
    location: str | None = Field(default=None)
    time_zone: str | None = Field(default=None, alias="timeZone")
    utc_offset: int | None = Field(default=None, alias="utcOffset")
    geo: Geo | None = Field(default=None)
    bio: str | None = Field(default=None)
    site: str | None = Field(default=None)
    avatar: str | None = Field(default=None)
    employment: Employment | None = Field(default=None)
    facebook: SocialHandle | None = Field(default=None)
    github: dict | None = Field(default=None)
    twitter: dict | None = Field(default=None)
    linkedin: SocialHandle | None = Field(default=None)


class CompanyCategory(BaseModel):
    """Company category/industry classification."""

    model_config = {"populate_by_name": True}

    sector: str | None = Field(default=None)
    industry_group: str | None = Field(default=None, alias="industryGroup")
    industry: str | None = Field(default=None)
    sub_industry: str | None = Field(default=None, alias="subIndustry")


class CompanyEnrichmentData(BaseModel):
    """Data from company enrichment."""

    model_config = {"populate_by_name": True}

    id: str | None = Field(default=None)
    name: str | None = Field(default=None)
    legal_name: str | None = Field(default=None, alias="legalName")
    domain: str | None = Field(default=None)
    description: str | None = Field(default=None)
    founded_year: int | None = Field(default=None, alias="foundedYear")
    location: str | None = Field(default=None)
    time_zone: str | None = Field(default=None, alias="timeZone")
    geo: Geo | None = Field(default=None)
    category: CompanyCategory | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)


# ============================================================================
# Discover Models
# ============================================================================


class DiscoverEmailsCount(BaseModel):
    """Email counts for a discovered company."""

    personal: int | None = Field(default=None)
    generic: int | None = Field(default=None)
    total: int | None = Field(default=None)


class DiscoverCompany(BaseModel):
    """A company returned by the Discover endpoint."""

    domain: str | None = Field(default=None)
    organization: str | None = Field(default=None)
    emails_count: DiscoverEmailsCount | None = Field(default=None)


# ============================================================================
# Email Count Models
# ============================================================================


class EmailCountData(BaseModel):
    """Data from email count response."""

    total: int | None = Field(default=None)
    personal_emails: int | None = Field(default=None)
    generic_emails: int | None = Field(default=None)
    department: dict | None = Field(default=None)
    seniority: dict | None = Field(default=None)


# ============================================================================
# Account Models
# ============================================================================


class AccountData(BaseModel):
    """Account information."""

    model_config = {"populate_by_name": True}

    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    email: str | None = Field(default=None)
    plan_name: str | None = Field(default=None)
    plan_level: int | None = Field(default=None)
    reset_date: str | None = Field(default=None)
    calls: dict | None = Field(default=None)
