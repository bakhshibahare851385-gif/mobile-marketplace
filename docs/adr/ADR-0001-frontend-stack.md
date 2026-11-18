# ADR-0001: Use Vue 3 + TypeScript + Vite for the frontend

- **Status:** Accepted (confirmed 2026-11-18)
- **Date:** 2026-11-18

## Context

The frontend must support dynamic pages: seller storefronts, a filterable catalog,
a comparison view, cart, checkout, and reviews. It needs strong typing to keep
domain models consistent, a fast dev server, and a component ecosystem.

## Decision

Build the SPA with **Vue 3 (Composition API) + TypeScript + Vite**, using Pinia
for state (cart, comparison list, session) and Vue Router for navigation.

## Consequences

- Positive: type-safe domain models; fast builds; mature routing/state tooling.
- Positive: Pinia suits ephemeral client state such as cart and comparison tray.
- Negative: assumes team familiarity with Vue; a React alternative would need a
  superseding ADR.

## Alternatives considered

- React + TypeScript: equally viable; not chosen per project brief (Vue hint).
- Server-rendered pages: simpler SEO but less fluid comparison/cart interactions.
