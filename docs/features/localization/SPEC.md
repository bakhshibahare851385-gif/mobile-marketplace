# SPEC: Persian Localization and RTL (fa-IR)

- **Status:** Draft — awaiting approval
- **Owner:** <assign>
- **Related tasks:** new task L-01 (to be added to `Task-List.md` on approval)
- **Related ADRs:** ADR-0001 (Vue 3 + Vite + TypeScript), ADR-0004 (TDD); ADR-0011 (i18n approach — to be written on approval)

## 1. Problem

The frontend currently renders all UI text in English and uses a left-to-right
layout. Persian-speaking buyers and sellers cannot comfortably read the Login and
Register forms, and the LTR alignment is unnatural for a Persian-language
interface. The marketplace must present these two pages in Persian with a proper
right-to-left layout while keeping the existing backend API contract unchanged.

## 2. Goals

- Render every user-visible string on the Login and Register views in Persian.
- Set the document language to `fa` and the layout direction to `rtl`.
- Map backend error codes to Persian messages in the frontend.
- Preserve all existing behavior: submit payloads, token storage, and API wiring.
- Keep the change test-first, with no regression in the current 9 frontend tests.

## 3. Non-goals

- No new pages. Per the teacher's instruction, only Login and Register exist — no
  dashboards, product lists, route guards, or E2E tests.
- No backend changes. Backend error messages remain in English; the frontend
  translates by `error.code`.
- No language switcher and no second locale. Persian is the only UI language.
- No date/number formatting work — these pages contain none.
- No translation-management service or external translation API.
- No third-party UI component library; the existing two views use plain Vue + CSS.

## 4. Users & personas

- **Persian-speaking buyer:** signs in or registers to browse and purchase accessories.
- **Persian-speaking seller:** signs in or registers to later manage a storefront.

## 5. User stories

- As a Persian-speaking seller, I want the sign-in form in Persian so I can use the marketplace confidently.
- As a Persian-speaking buyer, I want fields and buttons aligned right-to-left so the form feels natural.
- As a user, I want to understand backend errors (wrong password, duplicate email) in Persian.

## 6. Functional requirements

- **FR-LOC-1:** `index.html` declares `lang="fa"` and `dir="rtl"`; the app root inherits RTL.
- **FR-LOC-2:** All static strings in `LoginView.vue` and `RegisterView.vue` come from a Persian message catalog; no user-visible English literals remain in either template.
- **FR-LOC-3:** The catalog covers headings, subtitles, field labels, hints, button labels, loading states, success messages, switch links, and generic error fallbacks.
- **FR-LOC-4:** Backend error codes `invalid_credentials`, `duplicate_email`, `unauthorized`, and `invalid_token` map to dedicated Persian messages. Unknown codes and non-`ApiError` failures use a generic Persian fallback.
- **FR-LOC-5:** Email and password inputs keep `dir="ltr"` for correct address/password rendering, while labels, hints, and buttons remain RTL.
- **FR-LOC-6:** Register role options are displayed in Persian but keep the exact values `buyer` and `seller` sent to the backend.
- **FR-LOC-7:** CSS uses logical properties (`margin-inline`, `padding-inline`, `text-align`) so RTL alignment is correct without duplicated rules.
- **FR-LOC-8:** A Persian-capable font stack is used (system fallbacks preferred; no mandatory web-font download).
- **FR-LOC-9:** Existing behavior is unchanged — submit payloads, token storage, and register→login flow stay identical.

## 7. Acceptance criteria (Given/When/Then)

### AC-1 — Persian login page
- **Given** a visitor opens `/login`
- **When** the page renders
- **Then** the heading, subtitle, labels, button, and switch link are all in Persian and no English user-facing text is present.

### AC-2 — Persian register page
- **Given** a visitor opens `/register`
- **When** the page renders
- **Then** all text is Persian, and the role selector shows Persian labels while submitting `buyer` or `seller`.

### AC-3 — Document direction
- **Given** either page is loaded
- **When** the DOM is inspected
- **Then** `html` has `lang="fa"` and `dir="rtl"`.

### AC-4 — Input direction
- **Given** the RTL form
- **When** the email and password inputs are inspected
- **Then** they have `dir="ltr"` so credentials display correctly.

### AC-5 — Backend errors in Persian
- **Given** the backend returns `ApiError` with code `duplicate_email`
- **When** the register form displays the error
- **Then** the message is the Persian translation for "An account with this email already exists", not the English backend text.

### AC-6 — Unknown error fallback
- **Given** an error with an unmapped code or a non-`ApiError` failure
- **When** a form displays it
- **Then** a generic Persian error message is shown and no English text leaks.

### AC-7 — Behavior unchanged
- **Given** valid credentials on the Login form
- **When** the form is submitted
- **Then** the store still receives `{email, password}` and both tokens are stored exactly as before.

### AC-8 — Tests
- **Given** `npm test`, `npm run typecheck`, and `npm run build`
- **When** they are run
- **Then** all pass, including new localization tests and the existing 9 tests.

## 8. Data model changes

None. No backend schema or API contract changes.

## 9. API changes

None. The frontend continues to call `POST /api/v1/auth/register` and
`POST /api/v1/auth/login`. Localization uses the existing `error.code` field from
the backend error envelope.

## 10. UX notes

- Right-align headings, labels, inputs, buttons, and links.
- Keep email addresses and passwords left-to-right; place icons/indicators sensibly for RTL.
- Persian button states: e.g. "ورود" / "در حال ورود…" and "ایجاد حساب" / "در حال ایجاد حساب…".
- Document title should be Persian.
- Use readable Persian typography with a system font fallback chain.

## 11. Cross-cutting concerns

- **i18n approach:** decide between a typed catalog module and `vue-i18n`; record the choice in a new ADR-0011 before implementation (technology decision per AGENTS.md).
- **TDD:** write catalog/error-mapping tests and component tests before changing views.
- **Typecheck:** catalog keys should be typed to prevent missing translations.
- **Backend decoupling:** translate by `error.code`, never by parsing English messages.

## 12. Test plan (TDD)

- **Unit tests:** every catalog key exists and is non-empty; error-code mapping covers all known codes; unknown codes fall back to Persian; no English literals remain in the catalog values.
- **Component tests (Login):** Persian heading/labels/button; `dir="rtl"` on the page container and `dir="ltr"` on inputs; submit payload unchanged; Persian error shown for `invalid_credentials`.
- **Component tests (Register):** Persian text; role options Persian with underlying values `buyer`/`seller`; Persian error for `duplicate_email`.
- **Document test:** `index.html` contains `lang="fa"` and `dir="rtl"`.
- **Verification:** `npm test`, `npm run typecheck`, `npm run build`.

## 13. Risks & mitigations

| Risk | Mitigation |
| --- | --- |
| Hard-coded English strings overlooked | Catalog-only rendering plus a test that scans for English literals in views. |
| RTL breaks layout | Use logical CSS properties; assert direction attributes in tests. |
| Email/password rendered RTL incorrectly | Force `dir="ltr"` on credential inputs. |
| Backend error codes drift | Map by code with a generic Persian fallback; document mapping in the catalog. |
| i18n dependency adds weight | ADR-0011 compares a lightweight typed catalog vs `vue-i18n`. |

## 14. Open questions

- Should we use `vue-i18n`, or a lightweight typed Persian catalog object?
- Should email/password inputs stay `dir="ltr"` (recommended), or follow RTL?
- Should a language switcher be planned for a later phase?
- Which Persian font stack: system fallbacks only, or bundle a web font such as Vazirmatn?
