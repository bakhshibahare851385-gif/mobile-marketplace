# ROADMAP.md — Delivery Roadmap

Vision: become the trusted marketplace where mobile-accessory sellers showcase
their work and customers confidently discover, compare, and buy.

## Guiding principles

- Discovery before commerce: sellers need a storefront and catalog first.
- Trust is core: orders are immutable and reviews are verified.
- No scheduling features — ever. Stock, carts, orders, and reviews are the model.

## Phases

### Phase 0 — Foundations (documentation complete, code not started)

- Confirm stack and record ADRs.
- Scaffold backend/frontend, Docker Compose, CI, schema baseline.
- Exit criteria: health endpoint, blank app shell, CI green, ADRs accepted.

### Phase 1 — Sellers & Catalog (MVP discovery)

- Authentication and roles.
- Seller storefronts with services, prices, images, and portfolio.
- Product CRUD, categories, images, publish workflow.
- Catalog browse/search/filter, product detail, comparison.
- Exit criteria: a seller can publish a storefront; a customer can browse and
  compare products.

### Phase 2 — Cart & Orders (commerce)

- Cart management and stock validation.
- Checkout with immutable order snapshots and atomic stock decrement.
- Order history, seller order reports, status workflow.
- Exit criteria: end-to-end purchase flow with correct totals and inventory.

### Phase 3 — Reviews & Trust

- Product and seller reviews with verified-purchase flags.
- Aggregate ratings, sorting, moderation.
- Exit criteria: reviews visible on product/storefront pages; moderation works.

### Phase 4 — Hardening & Launch

- RBAC enforcement, validation, rate limiting.
- Accessibility (WCAG 2.1 AA), performance tuning, observability, security review.
- Exit criteria: launch checklist complete, runbook published, SLA targets met.

### Phase 5 — Future opportunities (post-launch)

- Wishlist/favorites, seller messaging, promo codes, recommendations.
- Payment provider integration and multi-currency support.

## Milestone timeline (indicative)

| Milestone | Phase | Target |
| --- | --- | --- |
| M0 Docs & scaffold | 0 | Done (docs) / next sprint (code) |
| M1 Storefront & catalog | 1 | Sprint 2–3 |
| M2 Cart & checkout | 2 | Sprint 4–5 |
| M3 Reviews | 3 | Sprint 6 |
| M4 Launch readiness | 4 | Sprint 7–8 |

Dates are intentionally relative; re-baseline once Phase 0 code starts.

## Dependencies & risks

| Risk | Mitigation |
| --- | --- |
| Stack assumptions unconfirmed | Confirm ADRs before first implementation commit. |
| Image storage cost/latency | Use S3-compatible storage with CDN-friendly keys; lazy thumbnails. |
| Stock oversell on concurrent checkout | Conditional decrements in a single transaction (ADR-009). |
| Catalog slow under growth | Redis caching, pagination, indexes (ADR-008). |
| Scope creep into scheduling | Enforce AGENTS.md vocabulary; reject booking-like requirements. |

## Success metrics

- Storefronts published and products listed (supply).
- Product views, comparison uses, and search-to-detail rate (discovery).
- Cart-to-order conversion and checkout success rate (commerce).
- Verified reviews per product and average rating (trust).
- p95 catalog latency and checkout error rate (quality).

## Maintenance

Review this roadmap at each phase exit. Link delivery status to
[Task-List.md](../Task-List.md) and keep specs/plans under `docs/`.
