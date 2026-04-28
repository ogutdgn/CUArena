# Project Overview

## Purpose

Build a **pixel-accurate mock of Figma Design** with a defined subset of editing functionality and a comprehensive **action logger**. The mock is the editor-facing piece of a larger CUA (Computer Use Agent) testing system; only the Mock App + logger are in scope for this repo.

The customer has provided the concrete feature list to deliver, so the project is past the "deciding what to build" phase and into focused implementation.

## What to build (current source of truth)

- [`feature-checklist.md`](feature-checklist.md) — the customer-provided feature list. Tick items here as they ship.
- [`execution-map.md`](execution-map.md) — the wave-by-wave implementation order, with main files touched per step.

## Session workflow (mandatory)

Both `feature-checklist.md` and `execution-map.md` must be refreshed every session.

- **At session start:** before any implementation, discuss with the user which features will be tackled this session, then update `execution-map.md` so it reflects the plan (priorities, current wave/step, what's in-flight vs. deferred).
- **At session end:** before closing, apply the session's outcomes to both files:
  - In `feature-checklist.md`, tick newly-shipped items (`[x]`).
  - In `execution-map.md`:
    - Add a new dated entry at the **top** (the **Session log** section) with the session date and a concise list of what shipped that session — this is the project's running record of which session delivered what.
    - In session-log entries, do **not** label items by Wave number (e.g. "Wave 1 shipped: ...") — describe what shipped directly. Wave numbers in the lower plan are not stable across sessions (see renumber rule below).
    - In the lower section (waves / steps), **delete** items that are now fully done. Do **not** annotate them with "Done" or keep them around — the session log is the only place finished work is preserved. Trim sub-bullets the same way when only part of a step ships.
    - **Renumber the lower plan from Wave 1** after deletions: the lower section must always start at Wave 1. When the previous Wave 1 finishes, what was Wave 2 becomes the new Wave 1, Wave 3 becomes 2, and so on. Step numbers restart from 1 the same way.

These two files are the project's living state; do not let them drift from reality.

## Code lives in `test-app/`

The actual application (Vite + React + TS) lives under `test-app/`. For architecture (engine, scene graph, ops, logger, UI shell), see [`test-app/ARCHITECTURE.md`](test-app/ARCHITECTURE.md).

## Reference material — read these first

Three reference docs under `helper/` are the **entry points** to the corpus. Each describes its slice and points back into `helper/figma_docs/`, `helper/analysis/`, `helper/extracted/` as needed.

- [`helper/00-overview.md`](helper/00-overview.md) — project scope, principles, **how-to-use workflows** (§7a) for implementation agents. Start here.
- [`helper/01-ui-schema-extraction.md`](helper/01-ui-schema-extraction.md) — UI schema reference (regions, state matrix, color picker, context menu, etc.).
- [`helper/02-feature-research.md`](helper/02-feature-research.md) — feature spec reference (~250 specs across 34 categories).

These three docs are sufficient to know which file under `helper/figma_docs/`, `helper/analysis/`, or `helper/extracted/` to read for any task. Do not read the corpus blind — go through `helper/00-overview.md §7a` workflows first.

`helper/open-source-example/open-pencil/` is also available as an OpenPencil (open-source Figma-compatible editor) reference. Useful patterns: SceneGraph emitter, inverse-op undo, Figma-HTML clipboard, hit-testing, snap-guides.
