# SPEC.md — Feature Specification Standard

A **SPEC** describes *what* to build and *why*, independent of implementation.
Create one under `docs/specs/<feature>.md` before starting non-trivial work, and
link it from `Task-List.md`. An accepted spec is the input to a `PLAN.md`.

## Process

1. Draft the spec using the template below.
2. Review it with the team; resolve open questions.
3. Mark it **Accepted**. Only then create the implementation plan.
4. If scope changes, update the spec first, then the plan.

## Template

```markdown
# SPEC: <Feature Name>

- Status: Draft | Accepted | Superseded
- Owner: <name>
- Related tasks: <IDs from Task-List.md>
- Related ADRs: <IDs>

## 1. Problem
What user or platform problem does this solve? State it in one or two paragraphs.

## 2. Goals
- <measurable goal>

## 3. Non-goals
- <explicitly out of scope — especially anything resembling booking/scheduling>

## 4. Users & personas
- Customer: ...
- Seller: ...
- Admin: ...

## 5. User stories
- As a <persona>, I want <capability>, so that <value>.

## 6. Functional requirements
- FR-1: <observable behavior>
- FR-2: ...

## 7. Acceptance criteria (Given/When/Then)
### AC-1
- Given <precondition>
- When <action>
- Then <observable outcome>

## 8. Data model changes
- New/updated entities, fields, relationships. Refer to ARCHITECTURE.md.

## 9. API changes
- Endpoints, request/response shapes, status codes.

## 10. UX notes
- Pages, components, states (empty, loading, error), accessibility.

## 11. Cross-cutting concerns
- Auth/permissions, validation, i18n/currency, logging.

## 12. Test plan (TDD)
- Unit tests: <behaviors>
- Integration tests: <API/database flows>
- E2E tests: <critical user journeys>
- Coverage target: <per AGENTS.md section 4.1>

## 13. Risks & mitigations
- <risk> → <mitigation>

## 14. Open questions
- <question and owner>
```

## Rules

- Acceptance criteria must be observable and testable; avoid vague words like
  "fast" or "user-friendly" without a measurable definition.
- Never describe time slots, availability, double-booking, or appointments.
- Model stock as inventory, purchases as orders, and feedback as reviews.
- Keep prices and product details in orders as snapshots (see ADR-009).
- Every functional requirement must map to at least one acceptance criterion.

## Example (abridged)

> **SPEC: Product Comparison**
> - Goals: let a customer compare up to 4 products side by side.
> - Non-goals: no availability calendars or delivery-time scheduling.
> - FR-1: A customer can add a product to a comparison list.
> - AC-1: Given a product in the catalog, when the customer clicks "Compare", then
>   the product appears in the comparison tray.
> - Test plan: unit tests for comparison-state store; E2E test for the compare flow.
