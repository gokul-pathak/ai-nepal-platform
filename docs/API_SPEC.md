# API Specification

## Base Information

- Base path: `/api/v1`
- Content type: `application/json`
- Response header: `X-Request-ID` is returned for request tracing

## Endpoints

### GET /api/v1/health

Purpose: service health probe.

Response:

```json
{
  "status": "ok",
  "service": "ai-nepal-platform-backend",
  "environment": {
    "name": "development",
    "api_prefix": "/api/v1"
  },
  "checks": {
    "database": {
      "status": "ok"
    },
    "ai_provider": {
      "status": "ok",
      "provider": "gemini"
    }
  },
  "uptime": {
    "started_at": "2026-05-15T10:20:00.000000+00:00",
    "uptime_seconds": 126.482
  }
}
```

Notes:

- `status` can be `ok` or `degraded`.
- Diagnostic checks return safe summaries only (no secrets).

### GET /api/v1/tools

Purpose: list only active tools.

Response example:

```json
[
  {
    "id": "2ce9e609-2c6b-4ccc-8faa-af78b80f42ff",
    "slug": "translator",
    "name": "Translator",
    "description": "Placeholder description for Translator.",
    "category": "language",
    "is_active": true,
    "created_at": "2026-05-08T07:00:00.000000Z",
    "updated_at": "2026-05-08T07:00:00.000000Z"
  }
]
```

### POST /api/v1/tools/{tool_slug}/run

Purpose: execute a tool prompt using configured AI provider.

Headers:

- Required header: `X-Session-ID: <session_id>`

Request body:

```json
{
  "input": "Translate this to Nepali",
  "language": "ne"
}
```

Success response (HTTP 200):

```json
{
  "tool": "translator",
  "result": "...generated content...",
  "usage": {
    "remaining_daily_requests": 4
  }
}
```

Error responses:

- `400`: missing session header, blank input, or blocked instruction pattern
- `401`: reserved for protected endpoints
- `404`: tool not found
- `422`: validation error (e.g., oversized input exceeding length limit, or schema validation failures)
- `429`: rate limit exceeded (public API abuse prevention, sliding window per session)
- `500`: internal server error
- `502`: upstream AI provider request failed

Rate limit response (HTTP 429):

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

Notes:
- Rate limiting is applied per session ID (`X-Session-ID` header).
- Algorithm: sliding window time-based rate limiting.
- Default limits: 20 requests per 60 seconds (configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`).
- Rate limiting can be disabled via `RATE_LIMIT_ENABLED` environment variable.

### GET /api/v1/sponsors/packages

Purpose: return active sponsor packages.

Response example:

```json
[
  {
    "id": "ab74af8f-4bfe-41c3-a55f-0f4cf13f9e2e",
    "name": "Bronze",
    "slug": "bronze",
    "monthly_request_limit": 5000,
    "price_label": "Starter sponsorship",
    "description": "Sponsor basic user AI credits for local communities.",
    "is_active": true,
    "created_at": "2026-05-09T08:00:00.000000Z",
    "updated_at": "2026-05-09T08:00:00.000000Z"
  }
]
```

### POST /api/v1/sponsors/leads

Purpose: submit sponsor interest lead.

Request body:

```json
{
  "organization_name": "Kathmandu Tech Initiative",
  "contact_name": "Asha Rana",
  "email": "asha@example.com",
  "phone": "+977-9800000000",
  "sponsor_type": "district program",
  "budget_range": "5k-10k USD",
  "target_group": "public schools",
  "message": "Interested in silver package"
}
```

Success response (HTTP 200):

```json
{
  "id": "d2b95cc9-8bf6-4738-b39a-8e3bfe59eb8e",
  "message": "Sponsor interest submitted successfully"
}
```

Validation error response (HTTP 422):

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "Value error, Invalid email address",
      "input": "invalid@@email.com"
    }
  ]
}
```

Response fields:
- `detail`: Array of validation error objects
- `type`: Error type identifier (e.g., "value_error", "missing", "string_too_short")
- `loc`: Location of the error as an array (e.g., ["body", "field_name"])
- `msg`: Human-readable error message
- `input`: The invalid input value that caused the error

### GET /api/v1/metrics/public

Purpose: provide public impact counters.

Security notes:

- Public response includes aggregated counts only.
- No sponsor emails, phone numbers, session IDs, IP hashes, or raw user input are exposed.

Response example:

```json
{
  "total_requests": 1520,
  "total_users_helped": 423,
  "total_sponsor_leads": 17
}
```

### GET /api/v1/admin/metrics

Purpose: provide basic admin dashboard metrics.

Authentication:

- Applies to all `/api/v1/admin/*` routes.
- Required header: `X-Admin-API-Key: <ADMIN_API_KEY>`
- If missing/invalid: HTTP `401`
- If server key not configured: HTTP `503`

Response example:

```json
{
  "total_tool_usage_count": 1520,
  "total_users_helped": 423,
  "usage_count_by_tool": [
    {
      "tool_slug": "translator",
      "count": 900
    },
    {
      "tool_slug": "form-helper",
      "count": 350
    }
  ],
  "sponsor_lead_count": 17,
  "latest_sponsor_leads": [
    {
      "organization_name": "Kathmandu Tech Initiative",
      "contact_name": "Asha Rana",
      "status": "new",
      "created_at": "2026-05-09T08:00:00.000000Z"
    }
  ],
  "latest_tool_usage_records": [
    {
      "tool_slug": "translator",
      "language": "en",
      "status": "success",
      "created_at": "2026-05-09T08:05:00.000000Z"
    }
  ]
}
```

## Database Schema Overview

All API endpoints read from/write to a PostgreSQL database managed by SQLAlchemy ORM and Alembic migrations.

### Core Tables

**tools** - Available AI tools

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key |
| slug | String(120) | URL identifier, unique |
| name | String(200) | Display name |
| description | Text | Tool description |
| category | String(120) | Tool category |
| is_active | Boolean | Availability flag |
| created_at, updated_at | DateTime(tz) | Audit timestamps |

**tool_usage** - Tool execution tracking (for analytics and rate limiting)

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key |
| tool_id | UUID | FK to tools.id (RESTRICT delete) |
| session_id | String(255) | Anonymous session tracker |
| language | String(50) | Request language (en, ne) |
| input_tokens | Integer | Tokens sent to AI |
| output_tokens | Integer | Tokens received from AI |
| status | String(50) | Result status |
| created_at, updated_at | DateTime(tz) | Timestamps |

**sponsor_leads** - Sponsorship inquiries

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key |
| organization_name | String(255) | Sponsor organization |
| contact_name | String(255) | Contact person |
| email | String(255) | Contact email, validated |
| phone | String(50) | Contact phone |
| sponsor_type | String(120) | Type of sponsorship |
| budget_range | String(120) | Budget tier |
| target_group | String(255) | Beneficiary group |
| message | Text | Additional notes |
| status | String(50) | Lead status (new, contacted, won, lost) |
| created_at, updated_at | DateTime(tz) | Timestamps |

**sponsor_packages** - Sponsorship tiers

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key |
| name | String(255) | Package name (Bronze, Silver, Gold) |
| slug | String(120) | URL identifier, unique |
| monthly_request_limit | Integer | API request limit per month |
| price_label | String(120) | Pricing display |
| description | Text | Package details |
| is_active | Boolean | Availability flag |
| created_at, updated_at | DateTime(tz) | Timestamps |

**admin_users** - Administrative accounts

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key |
| email | String(255) | Login email, unique, validated |
| password_hash | String(255) | Bcrypt hash |
| full_name | String(255) | Display name |
| is_active | Boolean | Account status |
| created_at, updated_at | DateTime(tz) | Timestamps |

### Data Integrity

- **Foreign key constraints** with RESTRICT delete behavior prevent orphaning
- **Check constraints** validate email format, non-empty strings, positive integers
- **Unique constraints** on business identifiers (slug, email)
- **Audit timestamps** on all tables (created_at, updated_at)

### Performance Indexes

Indexes optimize common query patterns:

- **tool_usage.session_id** - Rate limit checks, daily usage counts
- **tool_usage.tool_id** - Tool metrics aggregation
- **tool_usage.session_id + created_at** - Time-range filtering
- **sponsor_leads.email** - Duplicate detection, outreach
- **sponsor_leads.status + created_at** - Lead list filtering
- **tools.slug, sponsor_packages.slug, admin_users.email** - Unique lookups

For detailed schema documentation, see `docs/DATABASE_DESIGN.md`.

## Notes

- Sponsor listing and lead submission are included for MVP.
- Basic admin/public metrics endpoints are included for MVP visibility.
- Auth, role permissions, export reports, charts libraries, payments, and sponsor dashboard are not part of this phase.
- Database migrations are managed via Alembic and track schema evolution.
