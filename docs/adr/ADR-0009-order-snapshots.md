# ADR-0009: Use immutable order snapshots and atomic stock decrement

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

Orders must reflect what the customer actually bought, even if a seller later
changes a product's title, price, or availability. Concurrent checkouts must not
sell more units than exist in stock. This replaces any notion of double-booking
with straightforward inventory control.

## Decision

- On checkout, create `OrderItem` rows containing **snapshots** of product title
  and unit price at purchase time; never mutate committed orders.
- Perform checkout in a single database transaction: conditionally decrement
  `stock` where `stock >= quantity`, insert order items, create the order, and
  clear the cart. On any failure, roll back everything.
- Require an idempotency key so retries cannot create duplicate orders.

## Consequences

- Positive: order history is accurate and auditable; prices cannot drift.
- Positive: atomic transaction prevents overselling under concurrency.
- Negative: snapshots duplicate data; migrations must preserve historical fields.

## Alternatives considered

- Reference live product data from orders: cheaper storage but rewrites history.
- Reserve stock in a separate service: premature for MVP; revisit at scale.
