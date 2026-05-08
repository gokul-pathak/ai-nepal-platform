# Database Design

## Stack

- Database: PostgreSQL
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Driver: `psycopg` (`postgresql+psycopg` URL)

## Environment

- `DATABASE_URL` is loaded from environment variables.
- Example value in `backend/.env.example` is placeholder-only.
- No credentials are hardcoded in application code.

## Schema (Initial)

### tools

- `id` UUID primary key
- `slug` unique, not null
- `name` not null
- `description` text nullable
- `category` nullable
- `is_active` boolean default `true`
- `created_at`, `updated_at` timestamp with timezone

### tool_usage

- `id` UUID primary key
- `tool_id` UUID foreign key references `tools.id`
- `session_id` not null
- `ip_hash` nullable
- `language` nullable
- `input_tokens` default `0`
- `output_tokens` default `0`
- `status` not null
- `created_at` timestamp with timezone

### sponsor_leads

- `id` UUID primary key
- `organization_name` not null
- `contact_name` not null
- `email` not null
- `phone` nullable
- `sponsor_type` nullable
- `budget_range` nullable
- `target_group` nullable
- `message` nullable
- `status` default `new`
- `created_at`, `updated_at` timestamp with timezone

### sponsor_packages

- `id` UUID primary key
- `name` not null
- `slug` unique, not null
- `monthly_request_limit` not null
- `price_label` nullable
- `description` nullable
- `is_active` boolean default `true`
- `created_at`, `updated_at` timestamp with timezone

### admin_users

- `id` UUID primary key
- `email` unique, not null
- `password_hash` not null
- `full_name` nullable
- `is_active` boolean default `true`
- `created_at`, `updated_at` timestamp with timezone

## Migration

- Alembic config is in `backend/alembic.ini`.
- Metadata source is `app.core.database.Base.metadata` via `backend/alembic/env.py`.
- Initial migration: `backend/alembic/versions/20260508_0001_initial_schema.py`.

## Seed Data

Run the tools seed script after migration:

```bash
python scripts/seed_tools.py
```

Seeded slugs:

- `translator`
- `letter-writer`
- `form-helper`
- `agriculture-helper`
- `legal-basic-helper`
