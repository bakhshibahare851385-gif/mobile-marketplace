# ADR-0005: Store images in S3-compatible object storage

- **Status:** Accepted (assumed — confirm before first commit)
- **Date:** 2026-11-18

## Context

Seller storefronts and products are image-heavy: photos of accessories, service
examples, and portfolio work. Storing binaries in the database is inefficient and
hard to serve globally.

## Decision

Store product and portfolio images in an **S3-compatible object store**. The
database keeps only object keys and metadata. Uploads use signed URLs; keys are
CDN-friendly (e.g., `sellers/{id}/products/{id}/...`).

## Consequences

- Positive: scalable, cheap storage; images served directly via CDN.
- Positive: database stays small and fast.
- Negative: eventual consistency and orphaned objects require cleanup jobs.

## Alternatives considered

- BLOBs in PostgreSQL: simpler deploy but poor scalability and backup cost.
- Local filesystem: unsuitable for horizontal scaling.
