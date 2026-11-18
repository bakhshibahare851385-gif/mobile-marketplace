# PLAN: Authentication (Registration & Login)

- **Status:** Accepted
- **Spec:** [docs/features/auth/SPEC.md](./SPEC.md)
- **Owner:** <assign>
- **Related tasks:** S-01 (`Task-List.md`)

## 1. Approach

Implement auth vertically in thin, test-first slices following the layered
architecture (`ARCHITECTURE.md`): pure domain rules → persistence → API → frontend.
Each step starts with a failing test and ends green. Business rules (email
normalization, password policy, role whitelist, token TTLs) live in the domain
layer so they are framework-independent and unit-testable. FastAPI routers only
validate and orchestrate; authorization is enforced via dependencies.

Refresh tokens are stateless JWTs with rotation (no DB table). SQLite is the MVP
database; persistence stays behind repository interfaces so PostgreSQL can be
adopted later without touching the domain (ADR-0010).

No application code is written until this plan and the SPEC are approved.

## 2. Prerequisites

- SPEC and this plan approved.
- Stack confirmed: Vue 3 + TypeScript frontend, Python 3.12 + FastAPI backend, SQLite MVP (ADR-0001/0002/0010).
- Dependencies: `argon2-cffi`, `pyjwt`, `sqlalchemy`, `alembic`, `pydantic-settings`, `pytest`.
- Environment: `JWT_SECRET_KEY` and `DATABASE_URL` (e.g. `sqlite:///./marketplace.db`) supplied to the server.

## 3. Steps (test-first)

### Step 1 — Domain rules (pure functions) — Done
- [x] **Red:** tests for email normalization (trim + lowercase), password length (8–72), role whitelist (`buyer`/`seller` accepted, `admin` rejected), value-object construction/equality, and token policy constants (access 1800s, refresh 604800s, refresh outlives access, expiry boundaries).
- [x] **Green:** implement `Email`, `PasswordPolicy`, `Role` domain objects/helpers and `token_policy` with no framework imports.
- [x] **Refactor:** remove duplication; keep functions pure.
- [x] Verify: `pytest backend/tests/unit/test_auth_domain.py` green (42 passed).

### Step 2 — Password hashing & token service (domain-facing interfaces) — Done
- [x] **Red:** tests for Argon2id hashing (non-plain hash, correct/wrong password), and token creation/decoding for **both** access and refresh tokens: claims, signature verification, expiry, tampering, type-claim separation, and refresh rotation semantics.
- [x] **Green:** implement Argon2id hasher, JWT token service, token DTOs, and auth errors.
- [x] **Refactor:** clock injection for deterministic expiry tests; consumed refresh `jti` set kept inside the service.
- [x] Verify: `pytest backend/tests/unit` green (75 passed).

### Step 3 — User persistence & migration (SQLite) — Done (migration not run)
- [x] **Red:** repository contract tests for create, find-by-email (normalized), unique constraint, and that plain passwords are never stored.
- [x] **Green:** `User` SQLAlchemy model + repository; Alembic `0001_create_users_table` **written but not run** per user instruction.
- [x] **Refactor:** DTOs keep domain↔persistence mapping isolated; duplicate handling via `IntegrityError` catch/rollback; no raw SQL outside repositories.
- [x] Verify: repository tests green within `pytest tests/unit` (90 passed). `alembic upgrade head` deferred.

### Step 4 — Registration endpoint — Done
- [x] **Red:** API tests for 201 success (normalized email, hashed password), 422 invalid input/role, 409 duplicate email.
- [x] **Green:** Pydantic schemas + `POST /api/v1/auth/register` service and router.
- [x] **Refactor:** thin router; rules in domain/service; application ports for repository and hasher; central `DuplicateEmailError` handler.
- [x] Verify: `pytest tests` green (107 passed); `httpx2` installed to silence the TestClient deprecation warning.

### Step 5 — Login endpoint — Done
- [x] **Red:** API tests for 200 access + refresh tokens (correct claims/TTLs), 401 wrong password, 401 unknown email with identical generic message; `last_login_at` updated.
- [x] **Green:** `POST /api/v1/auth/login` with credential verification and both tokens issued.
- [x] **Refactor:** constant generic failure path via `InvalidCredentialsError`; shared token service instance.
- [x] Verify: `pytest tests` green (118 passed).

### Step 6 — Auth dependencies, refresh & protected endpoints — Done
- [x] **Red:** tests for `get_current_user` (401 missing/expired/tampered), `/auth/me` success, `require_roles` 403 for wrong role, `/auth/logout` 204, `/auth/refresh` rotation success and 401 for expired/tampered/wrong-type tokens.
- [x] **Green:** JWT decode dependency, `GET /auth/me`, `POST /auth/logout`, `POST /auth/refresh`, `require_roles(...)`.
- [x] **Refactor:** shared `_error_response` helper is the single source of truth for auth error envelopes.
- [x] Verify: `pytest tests` green (139 passed).

### Step 7 — Frontend auth flow — Implemented (not verified locally)
- [x] **Red:** Vitest tests written for the Pinia auth store and both views (token storage, login/register payloads, backend error messages, accessible labels).
- [x] **Green:** Vite + Vue 3 + TypeScript + Pinia + Router scaffold; `LoginView.vue`, `RegisterView.vue`, auth store, API client.
- [x] **Refactor:** accessible labels, `role="alert"` error states, minimal styling.
- [x] Verify: `npm test` (9 passed), `npm run typecheck` (clean), `npm run build` (built in 1.02s) — all green.
- Scope note: per teacher instruction, only Login and Register pages exist — no dashboards, product lists, route guards, or E2E tests.

### Step 8 — E2E & documentation
- [ ] **Red/E2E:** Playwright journey: register → login → protected page → silent refresh → logout; wrong-password error.
- [ ] **Green:** fix integration gaps; confirm coverage targets.
- [ ] Verify: `pytest`, `vitest`, `playwright`, `ruff`, `eslint`, type checks all green.
- [ ] Update `Task-List.md` (S-01 → Done) and link this SPEC/PLAN.

## 4. Data & migrations

- `0001_create_users_table`: `id` (UUID PK), `email` (unique, indexed), `password_hash`, `role` enum (`buyer`, `seller`, `admin`), `is_active` boolean default true, `created_at`, `last_login_at` nullable.
- **SQLite** file via `DATABASE_URL`; Alembic batch mode for future table alterations. No refresh-token table.
- Rollback: `alembic downgrade -1` drops the table (safe in development).

## 5. API surface

| Method | Path | Auth | Response |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | none | `201 {id, email, role}` |
| POST | `/api/v1/auth/login` | none | `200 {access_token, refresh_token, expires_in, refresh_expires_in}` |
| POST | `/api/v1/auth/refresh` | refresh token in body | `200 {access_token, refresh_token, ...}` |
| POST | `/api/v1/auth/logout` | Bearer access | `204` |
| GET | `/api/v1/auth/me` | Bearer access | `200 {id, email, role}` |

Shared dependencies: `get_current_user` (401 on invalid access token); `require_roles("seller"|"admin")` (403 on wrong role).

## 6. Files to touch

- **Backend:** `backend/app/domain/auth/` (email/password/role rules, token policy, interfaces), `backend/app/application/auth/` (services), `backend/app/infrastructure/auth/` (Argon2id, JWT, user repository), `backend/app/api/v1/auth.py`, `backend/app/infrastructure/db/models/user.py`, `backend/alembic/versions/0001_create_users_table.py`, `backend/app/core/config.py`.
- **Tests:** `backend/tests/unit/test_auth_*.py`, `backend/tests/integration/test_auth_api.py`.
- **Frontend:** `frontend/src/views/LoginView.vue`, `RegisterView.vue`, `frontend/src/stores/auth.ts`, `frontend/src/api/auth.ts`, `frontend/src/router/index.ts`, corresponding tests.
- **Docs:** this `SPEC.md`, `PLAN.md`, `Task-List.md`; ADRs only if a decision changes.

## 7. Risks & rollback

| Risk | Mitigation / rollback |
| --- | --- |
| Refresh token theft | Rotation on each refresh; short access TTL; client storage hardening. |
| Privilege escalation via role field | Whitelist registration roles; admin provisioned separately. |
| Brute force / credential stuffing | Generic errors, event logging; rate limiting in H-02. |
| Secret misconfiguration | `JWT_SECRET_KEY` from env; fail fast on startup if missing. |
| SQLite → PostgreSQL later | Repository interfaces; no domain dependency on SQLite. |
| Migration issues | Downgrade path defined; no production data yet. |

## 8. Verification checklist

- [ ] `pytest` green; domain ≥90%, API ≥80% coverage.
- [ ] `vitest` and Playwright green.
- [ ] `ruff`, `eslint`/`prettier`, and type checks clean.
- [ ] All acceptance criteria in SPEC.md verified.
- [ ] `Task-List.md` S-01 updated; docs unchanged otherwise.
- [ ] No booking concepts or terminology introduced.
- [ ] SPEC approved before any application code is written.
