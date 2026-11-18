# Task List — Mobile Accessories Marketplace

Ordered, test-first backlog. Every task follows **red → green → refactor** and
links to a spec, plan, or ADR where one exists. Status values: `Backlog`,
`Ready`, `In Progress`, `Done`.

Legend: **[T]** test written first · **[I]** integration test · **[E]** end-to-end test.

## In focus — Authentication (S-01)

- **Feature:** Registration & Login · **Status:** Ready · **Specs:**
  [SPEC.md](./docs/features/auth/SPEC.md) · [PLAN.md](./docs/features/auth/PLAN.md)
- **Next action:** approve SPEC.md and PLAN.md, then start Step 1 (failing domain tests).
- **Rule:** no application code until both documents are approved.

---

## Phase 0 — Foundations

| ID | Task | Status | Refs |
| --- | --- | --- | --- |
| F-01 | Confirm technology stack and record it as ADRs | Done | `docs/adr/` |
| F-02 | Scaffold backend (FastAPI, config, health endpoint) | Backlog | `PLAN.md` |
| F-03 | Scaffold frontend (Vue 3 + Vite + TS, routing shell) | Backlog | `PLAN.md` |
| F-04 | Set up Docker Compose (Redis, object storage); SQLite is a local file | Backlog | ADR-005, ADR-0010 |
| F-05 | Database schema + Alembic migration baseline | Backlog | `ARCHITECTURE.md` |
| F-06 | CI pipeline: pytest, Vitest, lint, type-check | Backlog | — |
| F-07 | Error handling, logging, and request-ID middleware | Backlog | `ARCHITECTURE.md` |

## Phase 1 — Sellers & Catalog (MVP discovery)

| ID | Task | Status | Refs |
| --- | --- | --- | --- |
| S-01 | User registration, login, JWT auth (buyer/seller roles) **[T][I]** | Ready | [SPEC](./docs/features/auth/SPEC.md), [PLAN](./docs/features/auth/PLAN.md), ADR-0004, ADR-0006 |
| S-02 | Seller profile CRUD (storefront: name, bio, services, contact) **[T]** | Backlog | `SPEC.md`, ADR-007 |
| S-03 | Product CRUD scoped to seller (title, description, price, stock, status) **[T][I]** | Backlog | `SPEC.md` |
| S-04 | Category taxonomy and product assignment **[T]** | Backlog | `ARCHITECTURE.md` |
| S-05 | Image & portfolio upload to object storage **[T][I]** | Backlog | ADR-005 |
| S-06 | Public seller storefront page (services, prices, images, portfolio) **[T][E]** | Backlog | `SRS.md` |
| S-07 | Product listing page with filters (category, price, seller) **[T][E]** | Backlog | `SRS.md` |
| S-08 | Product detail page **[T][E]** | Backlog | `SRS.md` |
| S-09 | Catalog search + Redis caching of read-heavy responses **[T][I]** | Backlog | ADR-008 |
| S-10 | Side-by-side product comparison (max N products) **[T][E]** | Backlog | `SRS.md` |

## Phase 2 — Cart & Orders

| ID | Task | Status | Refs |
| --- | --- | --- | --- |
| C-01 | Cart add/update/remove, totals calculation **[T][I]** | Backlog | `SPEC.md` |
| C-02 | Stock validation on cart operations **[T]** | Backlog | `ARCHITECTURE.md` |
| C-03 | Checkout: create order with immutable price snapshot **[T][I]** | Backlog | ADR-009 |
| C-04 | Inventory decrement on order commit (no double-booking concepts) **[T][I]** | Backlog | ADR-009 |
| C-05 | Order history and order detail for customer **[T][E]** | Backlog | `SRS.md` |
| C-06 | Seller order report view **[T][E]** | Backlog | `SRS.md` |
| C-07 | Order status workflow (pending → paid → fulfilled → cancelled/refunded) **[T]** | Backlog | `SPEC.md` |

## Phase 3 — Reviews & Trust

| ID | Task | Status | Refs |
| --- | --- | --- | --- |
| R-01 | Product reviews: rating + comment, verified-purchase flag **[T][I]** | Backlog | `SPEC.md` |
| R-02 | Seller reviews and aggregate rating **[T]** | Backlog | `SRS.md` |
| R-03 | Moderation workflow for flagged reviews **[T]** | Backlog | `SRS.md` |
| R-04 | Review helpfulness / sorting **[T]** | Backlog | — |

## Phase 4 — Hardening & Launch

| ID | Task | Status | Refs |
| --- | --- | --- | --- |
| H-01 | Role-based access control enforcement on all endpoints **[T][I]** | Backlog | ADR-006 |
| H-02 | Input validation and rate limiting **[T]** | Backlog | `ARCHITECTURE.md` |
| H-03 | Accessibility pass (WCAG 2.1 AA) on customer flows **[E]** | Backlog | `SRS.md` |
| H-04 | Performance tuning: pagination, indexes, cache invalidation **[T]** | Backlog | ADR-008 |
| H-05 | Observability: metrics, alerting, structured logs | Backlog | `ARCHITECTURE.md` |
| H-06 | Security review (OWASP ASVS basics) | Backlog | `SRS.md` |
| H-07 | Launch checklist and runbook | Backlog | `ROADMAP.md` |

## Phase 5 — Future (out of current scope)

| ID | Task | Status | Refs |
| --- | --- | --- | --- |
| N-01 | Wishlist / favorites | Backlog | `ROADMAP.md` |
| N-02 | Seller messaging / support chat | Backlog | `ROADMAP.md` |
| N-03 | Promo codes and discounts | Backlog | `ROADMAP.md` |
| N-04 | Recommendations based on browsing and purchases | Backlog | `ROADMAP.md` |

---

## How to pick up a task

1. Read the linked spec/plan/ADR and the acceptance criteria.
2. Write the failing test(s) marked by the `[T]/[I]/[E]` tags.
3. Implement the minimum to pass, then refactor.
4. Run all tests and linters, then move the task to `Done` with the commit reference.
