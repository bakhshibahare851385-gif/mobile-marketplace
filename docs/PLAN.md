# PLAN.md — Implementation Plan Standard

A **PLAN** translates an accepted `SPEC.md` into ordered, test-first steps. Keep
it beside the spec at `docs/plans/<feature>.md` and update it as work proceeds.

## Process

1. Start only from an **Accepted** spec.
2. Break the work into the smallest vertical slices that deliver observable behavior.
3. For each slice, list the failing test first, then the implementation files.
4. Execute red → green → refactor; check off steps as they pass.
5. Finish with the full verification checklist.

## Template

```markdown
# PLAN: <Feature Name>

- Status: Draft | In Progress | Done
- Spec: <link>
- Owner: <name>
- Related tasks: <IDs>

## 1. Approach
Short description of the implementation strategy and how it maps to the architecture.

## 2. Prerequisites
- <migration, config, dependency, ADR decision>

## 3. Steps (test-first)

### Step 1 — <slice name>
- [ ] **Red:** add failing test(s): <paths, behavior>
- [ ] **Green:** implement: <files, functions>
- [ ] **Refactor:** <cleanup>
- [ ] Verify: <command>

### Step 2 — <slice name>
...

## 4. Data & migrations
- <Alembic migration name and purpose; rollback plan>

## 5. API surface
- <new/changed endpoints and contracts>

## 6. Files to touch
- Backend: ...
- Frontend: ...
- Docs: SPEC, Task-List, SRS, ADRs as needed

## 7. Risks & rollback
- <risk> → <mitigation or rollback step>

## 8. Verification checklist
- [ ] `pytest` green, coverage targets met
- [ ] `vitest` / Playwright green
- [ ] `ruff` and `eslint`/`prettier` clean
- [ ] Type checks pass
- [ ] Acceptance criteria from SPEC verified
- [ ] Docs and Task-List updated
- [ ] No booking terminology introduced
```

## Rules

- Tests are committed with the implementation, never deferred.
- Prefer domain-layer tests for business rules and API tests for contracts.
- Keep each step shippable: after every step the suite must be green.
- If a step cannot be kept green, split it further.
- Do not write application code until a spec and plan exist and are accepted.
