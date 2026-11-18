# SPEC: Authentication (Registration & Login)

- **Status:** Accepted
- **Owner:** <assign>
- **Related tasks:** S-01 (`Task-List.md`)
- **Related ADRs:** ADR-0001 (frontend stack), ADR-0002 (backend stack), ADR-0004 (TDD), ADR-0006 (JWT auth & RBAC), ADR-0010 (SQLite for MVP)

## 1. Problem

The marketplace needs to distinguish buyers, sellers, and administrators so that
sellers can own storefronts and products, customers can place orders and reviews,
and admins can moderate. No identity mechanism exists yet. This feature provides
the minimal, secure foundation: an account can register, log in, refresh its
session, and prove its identity and role to the API.

This is **not** a booking feature. It introduces no availability, scheduling, or
time-zone behavior.

## 2. Goals

- Allow a visitor to register with an email, password, and role (`buyer` or `seller`).
- Allow a registered user to log in and receive a signed access token plus a refresh token.
- Allow a client to obtain a fresh access token by rotating a valid refresh token.
- Expose an authenticated endpoint returning the current user's identity.
- Store passwords securely (never in plain text) and enforce clear input validation.
- Provide a test-first foundation with ≥90% domain and ≥80% API coverage.

## 3. Non-goals

- Admin self-registration (admins are provisioned separately).
- Email verification and password reset (explicitly deferred for MVP).
- Buyer → seller upgrade (deferred to a later feature).
- Server-side token revocation denylist (deferred; logout is client-side token discard).
- Seller storefront creation (S-02) and full RBAC enforcement on all other endpoints (H-01).
- Any booking, appointment, reservation, or availability concept.

## 4. Users & personas

- **Buyer:** registers to browse, compare, order, and review.
- **Seller:** registers to later create a storefront and list products.
- **Admin:** provisioned out of band; only authenticates here.
- **Anonymous visitor:** may browse public catalog pages but not protected routes.

## 5. User stories

- As a **visitor**, I want to register as a buyer or seller so I can use the marketplace.
- As a **registered user**, I want to log in with my email and password so I can access my account.
- As a **logged-in user**, I want my session to renew automatically so I am not logged out mid-session.
- As a **seller**, I want my role recognized so I can later set up my storefront.

## 6. Functional requirements

- **FR-AUTH-1:** Registration accepts `email`, `password`, and `role` where role is exactly `buyer` or `seller`.
- **FR-AUTH-2:** Email is normalized (trimmed, lowercased) and must be unique.
- **FR-AUTH-3:** Password must be 8–72 characters; stored as an Argon2id hash; never returned by any API.
- **FR-AUTH-4:** Duplicate email registration returns `409 Conflict`.
- **FR-AUTH-5:** Login verifies credentials and returns `{access_token, refresh_token, token_type, expires_in, refresh_expires_in}`.
- **FR-AUTH-6:** Access JWT claims: `sub` (user id), `role`, `iat`, `exp`, `jti`, `type: "access"`. Refresh JWT claims: `sub`, `iat`, `exp`, `jti`, `type: "refresh"`.
- **FR-AUTH-7:** Access token expires after 30 minutes (`1800`s); refresh token after 7 days (`604800`s).
- **FR-AUTH-8:** `GET /auth/me` requires a valid access token and returns the user's `id`, `email`, and `role`.
- **FR-AUTH-9:** `POST /auth/logout` requires a valid access token and returns `204`; the client discards both tokens.
- **FR-AUTH-10:** Invalid or missing tokens on protected endpoints return `401`.
- **FR-AUTH-11:** A dependency `require_roles(...)` supports later role checks; buyers cannot reach seller-only routes.
- **FR-AUTH-12:** Authentication failures return a generic message to avoid account enumeration.
- **FR-AUTH-13:** `POST /auth/refresh` accepts a valid refresh token and returns a new access token and a **rotated** refresh token; expired or invalid refresh tokens return `401`.
- **FR-AUTH-14:** A refresh token must never be accepted as an access token, and vice versa (`type` claim enforced).

## 7. Acceptance criteria (Given/When/Then)

### AC-1 — Register as buyer
- **Given** no account with `buyer@example.com` exists
- **When** a visitor posts `{email: " Buyer@Example.com ", password: "s3curePass!", role: "buyer"}`
- **Then** a user is created with normalized email, role `buyer`, a non-plain-text hash, and the API returns `201` with `id`, `email`, `role`.

### AC-2 — Reject invalid registration
- **Given** the registration endpoint
- **When** a visitor posts a password shorter than 8 characters or a role of `admin`
- **Then** the API returns `422` and no user is persisted.

### AC-3 — Duplicate email
- **Given** `buyer@example.com` already exists
- **When** another registration uses the same email (any casing)
- **Then** the API returns `409` and the existing account is unchanged.

### AC-4 — Login success
- **Given** a registered user with correct credentials
- **When** they post their email and password
- **Then** the API returns `200` with an access token (claims `id`, `role`, `type: "access"`, `expires_in: 1800`) and a refresh token (`expires_in: 604800`).

### AC-5 — Login failure
- **Given** a wrong password or unknown email
- **When** a login attempt is made
- **Then** the API returns `401` with the same generic message in both cases and no tokens.

### AC-6 — Protected endpoint
- **Given** no Authorization header
- **When** `GET /auth/me` is called
- **Then** the API returns `401`.
- **Given** a valid access token
- **When** `GET /auth/me` is called
- **Then** the API returns `200` with the matching user's `id`, `email`, and `role`.

### AC-7 — Expired / tampered token
- **Given** an expired or altered access token
- **When** it is used on `GET /auth/me`
- **Then** the API returns `401` and never trusts its claims.

### AC-8 — Role guard
- **Given** a token with role `buyer`
- **When** a seller-only endpoint protected by `require_roles("seller")` is called
- **Then** the API returns `403`.

### AC-9 — Logout
- **Given** a valid access token
- **When** `POST /auth/logout` is called
- **Then** the API returns `204`; no server-side session state is required and the client discards both tokens.

### AC-10 — Refresh rotation
- **Given** a valid, unexpired refresh token
- **When** `POST /auth/refresh` is called
- **Then** the API returns `200` with a new access token and a new refresh token, and the old refresh token claims are no longer valid for further rotation after the next successful rotation.

### AC-11 — Token type separation
- **Given** a valid refresh token
- **When** it is used as a bearer token on `GET /auth/me`
- **Then** the API returns `401`.
- **Given** a valid access token
- **When** it is posted to `POST /auth/refresh`
- **Then** the API returns `401`.

## 8. Data model changes

The `users` table (see `ARCHITECTURE.md`):

| Column | Type | Notes |
| --- | --- | --- |
| `id` | UUID PK | generated on registration |
| `email` | string, unique, indexed | normalized (lower/trim) |
| `password_hash` | string | Argon2id encoded hash |
| `role` | enum | `buyer`, `seller`, `admin` |
| `is_active` | boolean | default `true` |
| `created_at` | datetime | default now |
| `last_login_at` | datetime, nullable | updated on successful login |

Refresh tokens are stateless JWTs; **no database table** is added for them in this MVP. Persistence uses **SQLite** for now (ADR-0010), with a schema designed so the switch to PostgreSQL later requires no domain changes. No booking-related fields.

## 9. API changes

All under `/api/v1`:

| Method | Path | Auth | Request | Response |
| --- | --- | --- | --- | --- |
| POST | `/auth/register` | none | `{email, password, role}` | `201 {id, email, role}` |
| POST | `/auth/login` | none | `{email, password}` | `200 {access_token, refresh_token, token_type, expires_in, refresh_expires_in}` |
| POST | `/auth/refresh` | refresh token in body | `{refresh_token}` | `200 {access_token, refresh_token, expires_in, refresh_expires_in}` |
| POST | `/auth/logout` | Bearer access | — | `204` |
| GET | `/auth/me` | Bearer access | — | `200 {id, email, role}` |

Error envelope follows `ARCHITECTURE.md` (code, message, request ID).

## 10. UX notes

- Registration page: email, password, and role selector limited to Buyer/Seller, with inline validation.
- Login page: email and password; generic "Invalid email or password" error.
- On success, route buyers to the catalog and sellers to storefront setup (S-02).
- Client stores both tokens and transparently refreshes the access token on `401` during MVP.
- Clear empty/loading/error states; labels linked to inputs; keyboard accessible.
- No booking-related copy.

## 11. Cross-cutting concerns

- Auth: stateless JWT per ADR-0006; roles via dependencies; refresh rotation per FR-AUTH-13.
- Validation: Pydantic schemas at the boundary; domain rules in the domain layer.
- Security: HTTPS in production; `JWT_SECRET_KEY` from environment; password hashes never serialized; refuse to log raw tokens.
- Logging: record auth events with request IDs only.
- Storage: SQLite MVP via ADR-0010; connection settings read from environment.
- Testing: TDD per ADR-0004; critical auth flows require integration tests.

## 12. Test plan (TDD)

- **Unit tests (≥90% domain):**
  - email normalization (trim/lowercase), password length boundaries, role whitelist rejects `admin`, value-object equality.
  - password hashing verifies correct/incorrect passwords; hash is not plain text.
  - access/refresh JWT creation and decoding: claims, signature, expiry, tampering, and `type` claim separation.
  - token TTL constants: access 1800s, refresh 604800s, refresh outlives access.
- **Integration tests (≥80% API):**
  - register success/invalid/duplicate (201/422/409).
  - login success, wrong password, unknown email with identical generic 401.
  - refresh success with rotation; refresh with access token rejected; expired/tampered refresh rejected.
  - `GET /auth/me` with no/valid/expired/tampered token; refresh token rejected as bearer.
  - `POST /auth/logout` with valid token; `require_roles` 403 for wrong role.
  - password hash persisted; plain password never stored or returned.
- **E2E test:** register → login → access protected page → silent refresh → logout.

## 13. Risks & mitigations

| Risk | Mitigation |
| --- | --- |
| Privilege escalation via client-supplied role | Whitelist `buyer`/`seller`; `admin` provisioned separately. |
| Refresh token theft | Rotation on use, 7-day expiry, secure client storage; denylist deferred. |
| Credential stuffing / brute force | Generic errors, event logging; rate limiting in H-02. |
| Secret leakage | `JWT_SECRET_KEY` from environment; no secrets in repo or logs. |
| SQLite → PostgreSQL migration | Keep persistence behind repository interfaces; no raw SQL in domain/services. |

## 14. Resolved decisions

- **Refresh tokens:** included — rotating refresh tokens, 7-day TTL (AC-10, FR-AUTH-13).
- **Email verification:** skipped for MVP.
- **Buyer → seller upgrade:** deferred to a later feature.
- **Stack:** Vue.js + FastAPI confirmed; SQLite for MVP, PostgreSQL later (ADR-0010).
