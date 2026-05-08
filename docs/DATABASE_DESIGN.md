# Database Design (Placeholder)

## Current State

- No database models are implemented in this foundation PR.

## Planned Direction

- PostgreSQL as primary relational datastore
- Alembic-driven migration strategy
- Clear separation between domain models and API schemas
- Audit-friendly schema evolution and indexing strategy

## Design Principles

- Least privilege access
- Backward-compatible migrations where possible
- Explicit data retention and soft-delete strategy by domain

## Notes

Detailed schema planning is expected in the next database-focused PR.
