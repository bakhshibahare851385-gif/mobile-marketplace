# ADR-0007: Model the seller storefront as a first-class entity

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

The product brief centers on each seller having a **dedicated page** showcasing
services, prices, images, and portfolio. Treating this as an afterthought of the
user model would scatter content fields and complicate public URLs.

## Decision

Introduce a `Seller` entity linked to a user account, holding storefront content
(name, bio, services with prices, portfolio items, status). Products reference
the seller. Storefronts have a stable slug-based public URL.

## Consequences

- Positive: clear ownership; easy to query a seller's products and reviews.
- Positive: storefront content can evolve independently of authentication.
- Negative: one-to-one seller/user requires careful account-to-seller upgrade flow.

## Alternatives considered

- Storefront fields directly on User: simpler but conflates identity and content.
- CMS-backed pages: flexible but adds an external dependency for MVP.
