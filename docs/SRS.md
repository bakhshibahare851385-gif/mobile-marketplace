# SRS.md — Software Requirements Specification

**Project:** Mobile Accessories Marketplace
**Version:** 0.1 (documentation phase)
**Scope:** Seller storefronts, product catalog, comparison, cart, orders, reviews.

> This is a marketplace, not a booking system. Requirements involving time slots,
> availability calendars, double-booking, or time zones are explicitly excluded.

## 1. Introduction

### 1.1 Purpose

Define the functional and non-functional requirements for a two-sided marketplace
where sellers showcase mobile accessories and services, and customers discover,
compare, and purchase them.

### 1.2 Definitions

| Term | Definition |
| --- | --- |
| Seller | A user with a storefront who lists products/services. |
| Storefront | A seller's dedicated public page. |
| Product | A listing with title, description, price, images, stock, and status. |
| Cart | Temporary collection of products selected for purchase. |
| Order | Committed purchase with immutable item/price snapshots. |
| Review | Customer rating (1–5) and comment on a product or seller. |

## 2. Stakeholders

| Role | Description |
| --- | --- |
| Customer (buyer) | Browses, compares, purchases, and reviews. |
| Seller | Manages a storefront, products, images, and portfolio. |
| Admin | Moderates content and manages categories. |

## 3. Functional requirements

### 3.1 Accounts & access (FR-A)

- **FR-A1:** Users can register as buyer or seller with email and password.
- **FR-A2:** Users can log in and receive a JWT; roles are enforced on endpoints.
- **FR-A3:** Sellers can only modify their own storefront and products.
- **FR-A4:** Admins can suspend sellers and hide content.

### 3.2 Seller storefront (FR-S)

- **FR-S1:** A seller has one dedicated public storefront page.
- **FR-S2:** The storefront displays seller name, bio, services with prices,
  images, and a portfolio.
- **FR-S3:** Sellers can create, update, and publish/unpublish their storefront.
- **FR-S4:** Storefronts have a stable public URL (e.g., `/sellers/{slug}`).

### 3.3 Products & catalog (FR-P)

- **FR-P1:** Sellers create products with title, description, price, stock,
  category, images, and status (draft/published/archived).
- **FR-P2:** Only published products appear in the public catalog.
- **FR-P3:** Customers can browse by category and filter by price range and seller.
- **FR-P4:** Customers can search products by keyword.
- **FR-P5:** Product detail page shows images, price, stock status, seller link,
  and reviews.
- **FR-P6:** Catalog results are paginated and sortable by price/relevance.

### 3.4 Product comparison (FR-CMP)

- **FR-CMP1:** Customers can add products to a comparison list (up to N=4).
- **FR-CMP2:** Comparison view shows products side by side with price, category,
  seller, and key attributes.
- **FR-CMP3:** Customers can remove products from the comparison list.

### 3.5 Cart (FR-C)

- **FR-C1:** Customers can add a published product with available stock to the cart.
- **FR-C2:** Customers can change quantities and remove items.
- **FR-C3:** The cart shows line totals and a grand total using current prices.
- **FR-C4:** Cart operations validate stock and show an error when stock is insufficient.

### 3.6 Orders (FR-O)

- **FR-O1:** Customers can check out an existing cart into an order.
- **FR-O2:** Checkout records an immutable snapshot of product title and unit price
  per order item.
- **FR-O3:** Checkout decrements stock atomically; failure leaves cart and stock unchanged.
- **FR-O4:** Order statuses: pending → paid → fulfilled, with cancel/refund paths.
- **FR-O5:** Customers can view their order history and order detail.
- **FR-O6:** Sellers can view orders containing their products.
- **FR-O7:** Checkout is idempotent to prevent duplicate orders on retry.

### 3.7 Reviews (FR-R)

- **FR-R1:** Customers can review products and sellers with a 1–5 rating and comment.
- **FR-R2:** Reviews are marked `verified_purchase` when backed by an order.
- **FR-R3:** Product/seller pages show the aggregate rating and visible reviews.
- **FR-R4:** Customers can sort reviews by rating or recency.
- **FR-R5:** Flagged reviews are hidden pending admin moderation.

### 3.8 Administration (FR-AD)

- **FR-AD1:** Admins manage the category taxonomy.
- **FR-AD2:** Admins moderate sellers, products, and reviews.

## 4. User stories (key)

- As a **customer**, I want to compare products side by side so I can choose the
  best value.
- As a **customer**, I want a cart and a reliable checkout so my purchase is
  recorded accurately.
- As a **seller**, I want a dedicated storefront so I can showcase my services,
  prices, and portfolio.
- As a **seller**, I want to manage stock so customers cannot buy more than I have.
- As a **customer**, I want to review a product so other buyers can trust my experience.

## 5. Non-functional requirements

| ID | Category | Requirement |
| --- | --- | --- |
| NFR-1 | Performance | p95 cached catalog response < 200 ms; paginate large lists. |
| NFR-2 | Correctness | Checkout is atomic; stock never negative; order snapshots immutable. |
| NFR-3 | Security | Passwords hashed; JWT auth; RBAC; ownership checks; HTTPS only. |
| NFR-4 | Privacy | No payment card data stored directly (use a payment provider — future). |
| NFR-5 | Usability | Clear empty/loading/error states; consistent terminology. |
| NFR-6 | Accessibility | WCAG 2.1 AA on customer flows. |
| NFR-7 | Compatibility | Modern evergreen browsers; responsive layout. |
| NFR-8 | Localization | Currency-formatted prices; UTF-8 content. |
| NFR-9 | Maintainability | TDD with coverage targets per AGENTS.md; documented ADRs. |
| NFR-10 | Observability | Structured logs, request IDs, health/readiness checks. |

## 6. Data requirements

- Persist users, sellers, storefront content, products, categories, images, carts,
  orders, order items, and reviews in SQLite for the MVP (PostgreSQL later, ADR-0010).
- Store prices as fixed-precision decimals, never floats.
- Store images in object storage; keep only object keys in the database.
- Retain order snapshots even if a product is archived or deleted.
- Full schema: [ARCHITECTURE.md](./ARCHITECTURE.md#5-domain-data-model).

## 7. External interfaces

- Object storage API (S3-compatible) for images and portfolio files.
- Redis for caching and session/token denylist (optional).
- Payment provider integration is a future phase; orders currently track status only.

## 8. Constraints & assumptions

- Stack confirmed: Vue 3 + FastAPI; SQLite for the MVP, PostgreSQL later (ADR-0001/0002/0010).
- No scheduling, appointment, or reservation features in any phase.
- Inventory is simple stock counting, not warehouse-level management.
- Initial launch targets a single currency and language.

## 9. Acceptance criteria (platform-level)

- A seller can publish a storefront with products and images.
- A customer can browse, filter, search, and compare products.
- A customer can add to cart and check out into an order with correct totals and
  decremented stock.
- A customer can view orders and leave verified reviews.
- All acceptance criteria are covered by automated tests written test-first.
