# Mobile Accessories Marketplace

A two-sided marketplace where sellers showcase their mobile-accessory services,
products, prices, images, and portfolio on a dedicated storefront page, and
customers browse, compare, and buy accessories.

> **Note:** This project is a marketplace, **not** a booking/reservation system.
> There are no time slots, availability calendars, double-booking rules, or
> time-zone logic. See [AGENTS.md](./AGENTS.md) for the full domain vocabulary.

## Features

### For customers

- Browse and search a catalog of accessories organized by category.
- Filter and **compare** products side by side on price, specs, and seller.
- View seller storefronts with services, prices, images, and portfolio.
- Add products to a **cart** and adjust quantities.
- Checkout into an **order** with a stable price snapshot.
- View order history and leave **reviews** and ratings.

### For sellers

- Create and manage a dedicated **storefront** page.
- List products with descriptions, prices, stock, images, and portfolio items.
- Manage inventory and product visibility (published/unpublished).
- Respond to customer reviews and view order reports.

### For administrators

- Moderate sellers, products, and reviews.
- Manage categories and platform-wide settings.

## Architecture at a glance

```
┌───────────────┐        HTTPS/JSON        ┌───────────────┐
│  Vue 3 SPA    │ ────────────────────────▶ │  FastAPI API  │
│  (frontend/)  │ ◀──────────────────────── │  (backend/)   │
└───────────────┘                           └──────┬────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────┐
                    ▼                              ▼              ▼
             ┌─────────────┐               ┌─────────────┐ ┌─────────────┐
             │   SQLite    │               │   Redis     │ │ S3 storage  │
             │ (source of  │               │  (cache /   │ │ (images /   │
             │  truth)     │               │  sessions)  │ │ portfolio)  │
             └─────────────┘               └─────────────┘ └─────────────┘
```

Full details: [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Technology stack

| Layer | Choice |
| --- | --- |
| Frontend | Vue 3, Vite, TypeScript, Pinia, Vue Router |
| Backend | Python 3.12, FastAPI, Pydantic, Alembic |
| Database | SQLite (MVP; PostgreSQL later — ADR-0010) |
| Cache | Redis |
| Images | S3-compatible object storage |
| Tests | pytest, Vitest, Playwright |

> The stack is an assumption recorded in `docs/adr/`; confirm it before the first
> implementation commit.

## Getting started

Prerequisites: Python 3.12+, Node 20+, Docker (optional).

1. Clone the repository and copy `.env.example` to `.env` (when added).
2. Start services: `docker compose up -d` (Redis, minio). SQLite is a local file; no database container is needed for the MVP.
3. Backend: install dependencies, run `alembic upgrade head`, start the API.
4. Frontend: install dependencies, start the Vite dev server.
5. Run the test suites before opening a pull request.

Detailed commands will be added alongside the first implementation (see
[Task-List.md](./Task-List.md)).

## Development practice

- **TDD:** every change starts with a failing test (red → green → refactor).
- **Specs:** non-trivial features are described in a `SPEC.md` first.
- **Plans:** implementation steps are tracked in a `PLAN.md`.
- **ADRs:** architectural decisions live in [docs/adr/](./docs/adr/).

## Documentation index

| Document | Purpose |
| --- | --- |
| [AGENTS.md](./AGENTS.md) | Rules and conventions for contributors and agents |
| [Task-List.md](./Task-List.md) | Ordered, test-first task backlog |
| [docs/SRS.md](./docs/SRS.md) | Software requirements |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System design and data model |
| [docs/ROADMAP.md](./docs/ROADMAP.md) | Delivery phases and milestones |
| [docs/SPEC.md](./docs/SPEC.md) | Feature-specification standard |
| [docs/PLAN.md](./docs/PLAN.md) | Implementation-plan standard |
| [docs/adr/README.md](./docs/adr/README.md) | Architecture Decision Records |

## Status

Documentation phase complete. Application implementation has not started yet.
