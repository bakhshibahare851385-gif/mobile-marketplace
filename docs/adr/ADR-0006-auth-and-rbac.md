# ADR-0006: Use stateless JWT auth with role-based access control

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

Three roles exist: buyer, seller, and admin. The API is horizontally scaled, so
server-side sessions add coordination overhead. Sellers must only edit their own
storefront and products.

## Decision

Issue **stateless JWT access tokens** on login. Enforce roles via dependency
injection and check ownership in the service layer (e.g., a seller may only
modify products whose `seller_id` matches their seller profile).

## Consequences

- Positive: API replicas need no shared session store.
- Positive: clear authorization model mapped to the three personas.
- Negative: token revocation needs a denylist (e.g., Redis) or short expiry.

## Alternatives considered

- Server-side sessions: simpler revocation but sticky/shared-state complexity.
- OAuth provider: heavier; defer until enterprise SSO is required.
