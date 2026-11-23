# ADR-0011: Use a lightweight typed Persian catalog

- **Status:** Accepted
- **Date:** 2026-11-20
- **Related:** [Localization SPEC](../features/localization/SPEC.md), ADR-0001

## Context

The frontend needs Persian (fa-IR) text and RTL layout on the Login and Register
pages only. There is a single locale, two pages, and a small, fixed set of
strings. Adding a full i18n framework would introduce a dependency and
configuration for little benefit.

## Decision

Use a **flat, typed TypeScript catalog** in `frontend/src/i18n/fa.ts` with
dot-separated keys and a `t(key: MessageKey)` helper. Backend error codes are
translated by a separate mapping helper in `frontend/src/i18n/errors.ts` using
the existing `error.code` field. No new npm dependency is added.

## Consequences

- Positive: zero new dependencies; compile-time safety for missing keys via
  `MessageKey`; simple to test.
- Positive: backend messages stay in English and are translated by code, not by
  parsing text.
- Negative: adding another locale later requires a new catalog and a keyed
  abstraction; acceptable for the current single-locale scope.

## Alternatives considered

- `vue-i18n`: more features (pluralization, interpolation, locale switching) but
  unnecessary for two pages and one locale.
- Hard-coded Persian strings in templates: simplest but untestable for
  completeness and error translation.
