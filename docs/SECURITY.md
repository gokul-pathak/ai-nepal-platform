# Security Guidelines

## Current MVP Controls

- Admin API protection: all `/api/v1/admin/*` endpoints require `X-Admin-API-Key` and return `401` for missing/invalid keys, or `503` when the admin key is not configured.
- Public metrics data minimization: `/api/v1/metrics/public` returns aggregated counters only.
- Input validation: tool run input is length-limited, rejects blank payloads, and blocks prompt-injection phrases.
- Usage abuse control: free usage is capped per session with `429` response on limit exceed.
- Secret hygiene: `.env.example` files contain placeholders only; no real keys in source control.

## CORS Policy

- CORS allowlist is configured via `BACKEND_CORS_ORIGINS` (comma-separated).
- Legacy `ALLOWED_ORIGINS` is still supported for compatibility.
- Wildcard `*` CORS is blocked when `ENVIRONMENT=production`.

## Logging Policy

- Never log `ADMIN_API_KEY` or request headers containing secrets.
- Never log full tool prompts or full user input payloads.
- Log safe error metadata only (provider name and error type), without raw prompt content.

## Error Response Policy

- `400`: invalid request inputs (for example, missing headers or blank input).
- `401`: admin key missing or invalid on admin routes.
- `429`: daily usage limit exceeded.
- `500`: generic internal server error response without sensitive details.

## Out Of Scope For MVP

- Full login/auth system
- JWT or RBAC
- Payment security controls
