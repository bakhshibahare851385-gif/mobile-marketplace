# AGENTS.md — Contributor & AI Agent Guide

> This file is the source of truth for every human contributor and AI agent working
> in this repository. Read it fully before making any change.

## 1. Project identity

**Mobile Accessories Marketplace** is a two-sided online marketplace for mobile
accessories:

- **Sellers** own a dedicated public page (storefront) where they showcase their
  services, products, prices, images, and portfolio.
- **Customers** browse the catalog, view seller pages, compare products, add items
  to a cart, place orders, and leave reviews.

### What this project is NOT

This is **not** a scheduling / booking / reservation platform. Never introduce:

- time slots, availability calendars, or reservations
- double-booking or conflict detection
- time-zone conversion for appointments
- the words "booking", "appointment", "reservation", or "slot" in code, docs, or UI

If a concept resembles scheduling, model it as a **marketplace** concept instead:

| Booking concept (forbidden) | Marketplace concept (use this) |
| --- | --- |
| Slot / appointment | Product / Service offering |
| Availability window | Stock status / published flag |
| Double-booking check | Inventory decrement on order |
| Booking confirmation | Order confirmation |
| Calendar | Catalog / Storefront |
| Service provider | Seller |
| Client | Customer |

### Core domain vocabulary

| Term | Meaning |
| --- | --- |
| **Seller** | A user account with a storefront, portfolio, and product listings. |
| **Storefront** | A seller's dedicated public page showing services, prices, images, and portfolio. |
| **Product** | An accessory or service listed by a seller with price, images, stock, and description. |
| **Category** | A taxonomy node used to organize and filter products (cases, chargers, screens, etc.). |
| **Cart** | A customer's temporary collection of products before checkout. |
| **Order** | A committed purchase; an immutable snapshot of items, prices, and buyer details. |
| **Order Item** | A line in an order capturing product, quantity, and the price paid. |
| **Review** | A customer's rating and comment attached to a product or seller. |

## 2. Assumed technology stack

> **Assumption:** No application code exists yet. The stack below is inferred from
> the project brief (Python + Vue). Confirm or correct it in `docs/adr/` before the
> first implementation commit.

| Layer | Technology |
| --- | --- |
| Frontend | Vue 3 + Vite + TypeScript, Pinia, Vue Router |
| Backend | Python 3.12 + FastAPI + Pydantic, Alembic |
| Database | SQLite (MVP; PostgreSQL later — ADR-0010) |
| Cache | Redis (read-heavy catalog caching, sessions) |
| Object storage | S3-compatible store for product/portfolio images |
| Testing | pytest (backend), Vitest + Playwright (frontend) |
| Packaging | Docker / Docker Compose |

Architectural choices are recorded as ADRs in `docs/adr/`.

## 3. Repository layout

```
.
├── AGENTS.md              # this guide
├── README.md              # human-facing overview and quick start
├── Task-List.md           # ordered, TDD-oriented task backlog
├── docs/
│   ├── ARCHITECTURE.md    # system design, modules, data model, flows
│   ├── SRS.md             # Software Requirements Specification
│   ├── ROADMAP.md         # phased delivery plan and milestones
│   ├── SPEC.md            # standard for writing feature specifications
│   ├── PLAN.md            # standard for writing implementation plans
│   └── adr/               # Architecture Decision Records
│       ├── README.md      # ADR index
│       └── ADR-00xx-*.md
├── backend/               # FastAPI application (future)
└── frontend/              # Vue application (future)
```

Do not move or rename documentation files without updating every cross-reference.

## 4. Engineering standards (non-negotiable)

### 4.1 Test-Driven Development (TDD)

All application code is written test-first using **red → green → refactor**:

1. **Red:** write a failing test that expresses the desired behavior.
2. **Green:** write the minimum code to make it pass.
3. **Refactor:** clean up while keeping tests green.

A change without tests is not complete. Every bug fix starts with a regression test.

Coverage expectations:

- Domain/business logic: ≥ 90% line coverage.
- API handlers and services: ≥ 80% line coverage.
- Critical flows (cart, checkout, order snapshot) require integration tests.

### 4.2 SPEC.md — feature specification

Before implementing a feature, create or update a spec following `docs/SPEC.md`.
A spec states the problem, goals/non-goals, user stories, functional requirements,
acceptance criteria in Given/When/Then form, data and API changes, and the test plan.

No implementation may begin without an agreed spec for non-trivial features.

### 4.3 PLAN.md — implementation plan

Translate an accepted spec into a plan following `docs/PLAN.md`. The plan breaks
work into small, test-first steps and lists files, migrations, and verification
commands. Keep the plan updated as work progresses.

### 4.4 ADRs — Architecture Decision Records

Any decision that affects structure, technology, data modeling, or cross-cutting
behavior must be captured in an ADR under `docs/adr/`. Use the index in
`docs/adr/README.md`. ADRs are immutable once accepted; supersede them with a new
ADR rather than editing history.

## 5. Workflow for agents

1. Read `AGENTS.md`, the relevant `docs/*` files, `Task-List.md`, and any existing
   `SPEC.md`/`PLAN.md` for the feature.
2. Confirm the task's acceptance criteria and tests **before** writing code.
3. Write the failing test, then the implementation, then refactor.
4. Run the full test suite and linters; report results.
5. Update `Task-List.md` status and link the relevant spec/plan/ADR.
6. Do not commit secrets. Use environment variables via `{env:VAR}` style references.

## 6. Style conventions

- Write clear, present-tense documentation with no booking terminology.
- Use the domain vocabulary from section 1 consistently.
- Prefer small, focused files and pure functions in the domain layer.
- Keep controllers thin: validation and orchestration in services, rules in the domain.
- Format Python with `ruff`; TypeScript/Vue with `prettier` + `eslint`.
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.

## 7. Definition of done

A task is done only when:

- [ ] Acceptance criteria from the spec pass.
- [ ] Tests were written first and the full suite is green.
- [ ] Linting and type checks pass.
- [ ] Documentation (README/SRS/ADR/Task-List) is updated where relevant.
- [ ] No forbidden booking concepts or terminology remain.
- [ ] Changes are reviewed against this guide.
