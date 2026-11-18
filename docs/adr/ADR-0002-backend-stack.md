# ADR-0002: Use Python 3.12 + FastAPI for the backend API

- **Status:** Accepted (confirmed 2026-11-18)
- **Date:** 2026-11-18

## Context

The backend exposes a REST JSON API, enforces marketplace business rules, and
must be highly testable (TDD). Pydantic validation and async support are valuable
for a read-heavy catalog and concurrent checkout.

## Decision

Implement the API in **Python 3.12 with FastAPI and Pydantic**, with a layered
structure (API → services → domain → infrastructure).

## Consequences

- Positive: automatic OpenAPI docs, strong validation, excellent pytest support.
- Positive: pure domain layer keeps business rules framework-independent for TDD.
- Negative: async ORM choices need care to avoid lazy-loading pitfalls.

## Alternatives considered

- Django REST Framework: batteries included but heavier and less explicit layering.
- Node/NestJS: would align languages but contradicts the Python hint in the brief.
