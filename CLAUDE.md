# Project Overview

## Purpose

Build a **pixel-accurate mock of Figma Design** with a defined subset of editing functionality and a comprehensive **action logger**. The mock is the editor-facing piece of a larger CUA (Computer Use Agent) testing system; only the Mock App + logger are in scope for this repo.

The customer has provided the concrete feature list to deliver, so the project is past the "deciding what to build" phase and into focused implementation.

## What to build (current source of truth)

- [`feature-checklist.md`](feature-checklist.md) — the customer-provided feature list. Tick items here as they ship.
- [`execution-map.md`](execution-map.md) — the wave-by-wave implementation order, with main files touched per step.

## Code lives in `test-app/`

The actual application (Vite + React + TS) lives under `test-app/`. For architecture (engine, scene graph, ops, logger, UI shell), see [`test-app/ARCHITECTURE.md`](test-app/ARCHITECTURE.md).

## Reference material — read these first

Three reference docs under `helper/` are the **entry points** to the corpus. Each describes its slice and points back into `helper/figma_docs/`, `helper/analysis/`, `helper/extracted/` as needed.

- [`helper/00-overview.md`](helper/00-overview.md) — project scope, principles, **how-to-use workflows** (§7a) for implementation agents. Start here.
- [`helper/01-ui-schema-extraction.md`](helper/01-ui-schema-extraction.md) — UI schema reference (regions, state matrix, color picker, context menu, etc.).
- [`helper/02-feature-research.md`](helper/02-feature-research.md) — feature spec reference (~250 specs across 34 categories).

These three docs are sufficient to know which file under `helper/figma_docs/`, `helper/analysis/`, or `helper/extracted/` to read for any task. Do not read the corpus blind — go through `helper/00-overview.md §7a` workflows first.

`helper/open-source-example/open-pencil/` is also available as an OpenPencil (open-source Figma-compatible editor) reference. Useful patterns: SceneGraph emitter, inverse-op undo, Figma-HTML clipboard, hit-testing, snap-guides.
