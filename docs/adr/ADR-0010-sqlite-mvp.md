# ADR-0010: Use SQLite for the MVP, migrate to PostgreSQL later

- **Status:** Accepted
- **Date:** 2026-11-18
- **Supersedes:** [ADR-0003](./ADR-0003-database.md)

## Context

ADR-0003 selected PostgreSQL as the primary datastore. The project brief has now
confirmed that the MVP should use **SQLite** for simplicity, with a planned switch
to PostgreSQL later. The domain model is still relational, and checkout/review
flows will eventually need the concurrency guarantees PostgreSQL provides.

## Decision

Use **SQLite** as the MVP database, accessed through SQLAlchemy with Alembic
migrations (batch mode for future alterations). Keep all persistence behind
repository interfaces so no domain or service code depends on SQLite specifics.
PostgreSQL remains the target for a later migration (superseding ADR-0003 at that
time).

## Consequences

- Positive: zero infrastructure setup; ideal for local development and the MVP.
- Positive: repository isolation keeps the future PostgreSQL migration cheap.
- Negative: weaker write concurrency; unsuitable for production scale — revisit before launch.
- Negative: SQLite enums/stored as strings; use portable SQLAlchemy types.

## Alternatives considered

- PostgreSQL now (ADR-0003): more robust but heavier setup than the MVP needs.
- In-memory store: not durable; unsuitable for orders and reviews.
