# API Specification

## Base Information

- Base path: `/api/v1`
- Content type: `application/json`

## Endpoints

### GET /api/v1/health

Purpose: service health probe.

Response:

```json
{
  "status": "ok",
  "service": "ai-nepal-platform-backend"
}
```

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

## Notes

- Auth, sponsor, admin action, and AI execution APIs are intentionally not implemented in this phase.
