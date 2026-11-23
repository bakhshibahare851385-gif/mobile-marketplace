# Architecture Decision Records (ADRs)

This directory records every decision that shapes the structure, technology,
data model, or cross-cutting behavior of the Mobile Accessories Marketplace.

ADRs are immutable once Accepted. To change a decision, write a new ADR that
supersedes the old one and update this index.

| ADR | Title | Status |
| --- | --- | --- |
| [0001](./ADR-0001-frontend-stack.md) | Use Vue 3 + TypeScript + Vite for the frontend | Accepted (confirmed) |
| [0002](./ADR-0002-backend-stack.md) | Use Python 3.12 + FastAPI for the backend API | Accepted (confirmed) |
| [0003](./ADR-0003-database.md) | Use PostgreSQL with Alembic as the primary datastore | Superseded by ADR-0010 |
| [0004](./ADR-0004-tdd.md) | Adopt Test-Driven Development as the default process | Accepted |
| [0005](./ADR-0005-image-storage.md) | Store images in S3-compatible object storage | Accepted (assumed) |
| [0006](./ADR-0006-auth-and-rbac.md) | Use stateless JWT auth with role-based access control | Accepted |
| [0007](./ADR-0007-storefront-model.md) | Model the seller storefront as a first-class entity | Accepted |
| [0008](./ADR-0008-catalog-caching.md) | Cache read-heavy catalog responses with Redis | Accepted |
| [0009](./ADR-0009-order-snapshots.md) | Use immutable order snapshots and atomic stock decrement | Accepted |
| [0010](./ADR-0010-sqlite-mvp.md) | Use SQLite for the MVP, migrate to PostgreSQL later | Accepted |
| [0011](./ADR-0011-i18n-approach.md) | Use a lightweight typed Persian catalog | Accepted |
