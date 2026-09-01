# Task QA Actions

Tracks follow-up work discovered from `task-qa.md` and from recurring verifier QA runs.

Use this file for actions, decisions, and status changes. Keep the full audit detail in `task-qa.md`.

---

## Current Status

Last verified: 2026-05-08

- `qa_verifiers.py`: `42 OK | 8 STRICT | 0 LENIENT | 0 CRASH`
- `qa_verifier_framework.py`: `2 OK | 0 FAIL`
- `qa_per_task/_runner.py all`: `50 tasks | 0 bug(s)`
- The `origin/delivery-1` verifier hardening was ported into the new `apps/figma/` layout without restoring the old root `delivery-1/`, `test-verifier/`, `test-app/`, or `project-documents/` layout.

---

## Open Actions

No open task QA actions at the moment.

---

## Closed Actions

### 2026-05-08 - delivery-1 hardening port

Status: closed

Context:
- The old `delivery-1` branch contained verifier hardening and per-task stress QA written against the previous root project layout.
- Main now uses `apps/figma/delivery-1`, `apps/figma/verifier`, and `apps/figma/scripts` as the canonical paths.

Outcome:
- Ported the delivery task prompt/verifier updates into `apps/figma/delivery-1`.
- Ported verifier hardening primitives and rubrics into `apps/figma/verifier` while preserving the newer logger-aligned page, prototype, center-position, polygon-vertex, and line-endpoint checks.
- Ported per-task stress QA into `apps/figma/scripts/qa_per_task` with a runner that loads canonical `delivery-1/task_NN/verifier.py` files.
- Verification: `qa_verifier_framework.py` passed, `qa_verifiers.py` returned 42 OK / 8 STRICT / 0 CRASH, and `qa_per_task/_runner.py all` returned 0 bug(s).

### 2026-05-07 - Transform and logger regression pass

Status: closed

Context:
- Core transform, frame nesting, overlay, line/arrow, and logger fixes were committed on `figma/ui-feature-bug`.
- QA was rerun after the changes.

Outcome:
- All 50 verifier QA smoke tests remained OK.
- No task moved between `planned`, `in_scope`, or `shipped`.
- No check primitive needed to change.

### 2026-05-08 - Position coordinate model pass

Status: closed

Context:
- Position panel X/Y changed to engine-level center-origin values while outcome storage stayed parent-local bbox geometry.
- QA was rerun after the change.

Outcome:
- All 50 verifier QA smoke tests remained OK.
- No task scope or check primitive changed.

### 2026-05-08 - Logger/verifier capability audit

Status: closed

Context:
- Logger schema and verifier checker coverage were re-audited before starting the next UI improvement batch.
- `delivery-1/` remains untouched; framework additions were made only under `verifier/`, `scripts/`, and `app-docs/`.

Outcome:
- Logger docs now include page background opacity/hidden, polygon/star option events, file rename, and prototype `delayMs` update fields.
- Added verifier primitives for document name, page background opacity/hidden, prototype connection existence, center-position checks, and line/arrow endpoint length/angle/shared-endpoint checks.
- Added `qa_verifier_framework.py` so shared checker primitives can be tested even before delivery tasks adopt them.
