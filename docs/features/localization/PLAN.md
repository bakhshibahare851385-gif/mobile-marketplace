# PLAN: Persian Localization and RTL (fa-IR)

- **Status:** Done
- **Spec:** [docs/features/localization/SPEC.md](./SPEC.md)
- **Owner:** <assign>
- **Related tasks:** L-01 (`Task-List.md`)
- **Decisions:** [ADR-0011](../../adr/ADR-0011-i18n-approach.md)

## 1. Approach

Introduce a single Persian message catalog and a typed `t(key)` helper, then
replace every user-visible string in the two views with catalog lookups. Backend
errors are translated by their `error.code` through a dedicated mapping helper,
so no English backend text is parsed. Direction is set at the document level
(`lang="fa"`, `dir="rtl"`) and CSS is converted to logical properties. Credential
inputs explicitly use `dir="ltr"`.

All work follows red → green → refactor in small steps; existing tests stayed
green throughout. No new pages were added.

## 2. Prerequisites

- SPEC and this plan approved.
- ADR-0011 recorded: lightweight typed catalog, no new runtime dependency.
- Task `L-01` added to `Task-List.md`.

## 3. Steps (test-first)

### Step 1 — Persian catalog and error-code mapping — Done
- [x] **Red:** unit tests for non-empty Persian catalog values, no English strings, all backend error codes mapped, unknown codes/non-ApiError fallbacks.
- [x] **Green:** `src/i18n/fa.ts` (typed catalog + `t`) and `src/i18n/errors.ts` (`messageForError`).
- [x] **Refactor:** `MessageKey` type makes missing keys fail `vue-tsc`.
- [x] Verify: all catalog/error tests green (10 tests).

### Step 2 — Document direction and base layout — Done
- [x] **Red:** document test for `lang="fa"` / `dir="rtl"` / Persian title.
- [x] **Green:** `index.html` updated; logical properties + Persian fallback font stack in `style.css`.
- [x] **Refactor:** removed physical margin/padding rules; LTR credential input rule added.
- [x] Verify: direction tests green (3 tests).

### Step 3 — LoginView in Persian — Done
- [x] **Red:** tests for Persian text, RTL container, `dir="ltr"` inputs, unchanged payload, Persian `invalid_credentials` error.
- [x] **Green:** literals replaced with `t(...)`; `messageForError` in catch.
- [x] **Refactor:** no inline English strings remain.
- [x] Verify: `LoginView.spec.ts` green (4 tests).

### Step 4 — RegisterView in Persian — Done
- [x] **Red:** tests for Persian text, Persian role labels with values `buyer`/`seller`, LTR inputs, Persian `duplicate_email` error.
- [x] **Green:** literals replaced; `messageForError`; role values unchanged.
- [x] **Refactor:** no inline English strings remain.
- [x] Verify: `RegisterView.spec.ts` green (5 tests).

### Step 5 — Verification and documentation — Done
- [x] `npm test` — 25 passed (6 files).
- [x] `npm run typecheck` — clean.
- [x] `npm run build` — built in 1.08s.
- [x] Scanned views: no hard-coded English text.
- [x] Task-List L-01 → Done; ADR-0011 linked.

## 4. Data & migrations

None.

## 5. API surface

Unchanged: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`.

## 6. Files touched

- **New:** `frontend/src/i18n/fa.ts`, `frontend/src/i18n/errors.ts`, their tests, `frontend/src/tests/direction.spec.ts`, `docs/adr/ADR-0011-i18n-approach.md`.
- **Modified:** `frontend/index.html`, `frontend/src/style.css`, both views and their tests, `Task-List.md`, this SPEC/PLAN, ADR index.
- **Unmodified:** backend files, router, auth store, API client contract.

## 7. Risks & rollback

All mitigations applied: typed catalog, direction assertions, LTR credential inputs,
error-code fallback with Persian generic message, no new runtime dependency.

## 8. Verification checklist

- [x] `npm test` green (25 passed).
- [x] `npm run typecheck` clean.
- [x] `npm run build` succeeds.
- [x] `index.html` has `lang="fa"` and `dir="rtl"`.
- [x] No user-visible English strings in the two views.
- [x] Submit payloads and token storage unchanged.
- [x] ADR-0011 written; `Task-List.md` L-01 updated.
- [x] No new pages, no backend changes, no E2E tests.
