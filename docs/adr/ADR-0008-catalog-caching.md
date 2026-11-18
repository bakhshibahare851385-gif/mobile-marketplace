# ADR-0008: Cache read-heavy catalog responses with Redis

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

Catalog browsing, filtering, and search are read-heavy and far outnumber writes.
Hitting Postgres for every listing query would add latency under growth.

## Decision

Cache hot catalog/search responses in **Redis** with short TTLs and explicit
invalidation when products, categories, or seller status change. Paginate all
list responses. Cache keys include the normalized filter set.

## Consequences

- Positive: low p95 latency for common queries; reduced database load.
- Positive: explicit invalidation keeps listings consistent after edits.
- Negative: cache invalidation bugs can serve stale listings; mitigate with
  integration tests and short TTLs.

## Alternatives considered

- No cache: simpler but latency and DB load grow with traffic.
- Full-text search engine (Elasticsearch): useful later; overkill for MVP.
