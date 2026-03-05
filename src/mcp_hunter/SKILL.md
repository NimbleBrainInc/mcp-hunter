# Hunter.io MCP Server — Skill Guide

## Tools

| Tool | Use when... | Cost |
|------|-------------|------|
| `discover_companies` | You need to find companies by industry, location, size, or natural language query | Free |
| `search_domain_emails` | You have a domain/company and need to find email addresses there | 1 credit / 10 emails |
| `find_email` | You know a person's name and company, and need their specific email | 1 credit |
| `verify_email` | You have an email and need to confirm it's deliverable before sending | 0.5 credits |
| `enrich_person` | You have an email or LinkedIn handle and want full profile details | 0.2 credits |
| `enrich_company` | You have a domain and want company info (industry, size, description) | 0.2 credits |
| `check_account` | You need to see remaining credits or plan details before making calls | Free |

## Context Reuse

- Use `domain` from `discover_companies` results to feed `search_domain_emails` or `enrich_company`
- Use `email` from `search_domain_emails` or `find_email` results to feed `verify_email` or `enrich_person`
- Use the `pattern` from `search_domain_emails` to understand a company's email format
- Check `check_account` before batch operations to ensure sufficient credits

## Workflows

### 1. Prospect a Company
1. `discover_companies` with industry/location/size filters to find target companies
2. For each company: `search_domain_emails` with department filter (e.g. "executive", "sales")
3. For key contacts: `verify_email` to confirm deliverability before outreach

### 2. Find and Verify a Specific Contact
1. `find_email` with first_name, last_name, and domain
2. `verify_email` on the returned email to check deliverability
3. `enrich_person` to get their full profile, title, and social handles

### 3. Research a Company
1. `enrich_company` with domain to get industry, description, location, and founding year
2. `search_domain_emails` with seniority="executive" to find decision makers
3. `enrich_person` on key contacts to understand their roles and backgrounds

### 4. Credit-Conscious Batch Lookup
1. `check_account` to see remaining credits
2. `discover_companies` (free) to build target list
3. For each target: start with free `email_count` check (use `search_domain_emails` with limit=0) before investing credits
