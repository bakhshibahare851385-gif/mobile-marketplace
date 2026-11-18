# ADR-0004: Adopt Test-Driven Development as the default process

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

Correctness matters most in cart totals, checkout, order snapshots, and stock
updates. A regression in these areas directly harms customers and sellers.

## Decision

All application code follows **red → green → refactor**. Tests are written before
implementation; every bug fix starts with a regression test. Coverage targets are
defined in AGENTS.md (≥90% domain, ≥80% API/services, integration tests for
critical flows). A feature needs an accepted SPEC and a PLAN before code.

## Consequences

- Positive: business rules are documented by tests; regressions are caught early.
- Positive: pure domain code stays decoupled from frameworks.
- Negative: higher initial effort; requires discipline and fast test suites.

## Alternatives considered

- Test-after development: faster initially but weaker regression safety.
- No formal spec/plan: leads to scope drift and unclear acceptance criteria.
