# Roadmap

> **Status: HIGH-LEVEL PLAN.** Sequence is decided; per-app scope and milestones will be refined as each app's research-flow runs.

---

## Sequence

1. **Figma** — active. Mock + verifier shipping. Pending work tracked in `apps/figma/app-docs/execution-map.md`.
2. **Sheets** — next. Will start with a research cycle (Google Sheets help docs → filtered helper → architecture decision), then mock skeleton, then verifier.
3. **Docs** — last. Text editing has the hardest semantic-event design (caret/range/run model); doing it after Figma's `text-range` work and Sheets' verifier-framework lessons gives the best foundation.

The sequence is **chained, not parallel**: we may do small overlapping work on the next app while finishing the current one (e.g. begin Sheets research while figma fills/gradients ship), but full implementation of two apps in parallel is out of scope.

---

## Why Sheets before Docs

- Sheets has a bounded op set (set cell, set range, formula, sort/filter, format) that maps cleanly to the existing logger pattern.
- Verifier checks for Sheets are deterministic (cell-value equals, range-sum equals, formula-result equals).
- Docs requires a more sophisticated edit-state model (caret/range, run merging, undo coalescing per keystroke vs per word). The figma `text-range` item (`#36`) tackles a piece of this; finishing that first reduces unknowns when Docs starts.

---

## Milestones

### Figma — current

Tracked in [apps/figma/app-docs/execution-map.md](../apps/figma/app-docs/execution-map.md).
Open priorities: outcome-stream correlation IDs, unsupported-button toast / rename UX hardening, fill/color expansion (gradient + image), vector finishing, prototype panel, right-sidebar parity, text-range edit-state.

### Sheets — pending

- M0: research cycle → committed `apps/sheets/helper/`
- M1: architecture decision (stack, state shape, op set) → `apps/sheets/app-docs/architecture.md`
- M2: minimum mock (grid, cell input, basic formulas) + logger
- M3: verifier framework (initially a copy of figma's, refactored as needed)
- M4: first 5 tasks + verifier scripts
- M5: shared verifier framework carve-out into `shared/` (after M4 ships)

### Docs — pending

- M0: research cycle → committed `apps/docs/helper/`
- M1: architecture decision (text model, run merging, edit-state)
- M2: minimum mock (single-paragraph editing, runs, basic formatting) + logger
- M3: verifier (uses shared framework from `shared/`)
- M4: first 5 tasks + verifier scripts

---

## Out of scope (for cua-bench)

- Real cloud sync, real auth, real collaboration cursors.
- Pixel-perfect rendering of every Figma/Sheets/Docs screen — only the surfaces an agent interacts with for evaluation tasks.
- Fully complete feature coverage of any of the three products.
- Cross-app tasks (a task that uses two apps).
