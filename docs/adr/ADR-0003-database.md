# ADR-0003: Use PostgreSQL with Alembic as the primary datastore

- **Status:** Superseded by [ADR-0010](./ADR-0010-sqlite-mvp.md) — SQLite is used for the MVP; PostgreSQL remains the future target.
- **Date:** 2026-11-18

## Context

Marketplace data is relational: sellers own products, carts contain items, orders
contain snapshots, and reviews link to products/sellers. Checkout needs atomic
transactions and conditional stock updates.

## Decision

Use **PostgreSQL** as the single source of truth, accessed via SQLAlchemy, with
**Alembic** migrations. Prices use fixed-precision numeric columns.

## Consequences

- Positive: ACID transactions make atomic checkout and stock decrement reliable.
- Positive: indexes and JSONB support flexible catalog filtering.
- Negative: requires migration discipline; schema changes are explicit.

## Alternatives considered

- MySQL: adequate but weaker feature set for our query needs.
- Document store: poor fit for relational ownership and transactional stock.
