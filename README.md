# Figma Mock for CUA Testing

A pixel-accurate mock of **Figma Design** with a comprehensive action logger, built as the editor-facing piece of a Computer Use Agent (CUA) testing system. The CUA interacts with the app via screen pixels — clicking buttons, reading labels, and verifying state changes — and the logger captures both raw input events and semantic user-intent events so trajectories can be replayed and asserted against.

Only the Mock App + logger are in scope for this repo. Upstream pieces (CUA model, adapter, bridge) and downstream pieces (test harness, trajectory assertions) live elsewhere.

## Run the app

The application is a Vite + React + TypeScript SPA under [`test-app/`](test-app/).

```bash
cd test-app
npm install
npm run dev        # local dev server
npm run typecheck  # tsc -b --noEmit
npm run build      # production build
```

For architecture (engine, scene graph, ops pipeline, logger, UI shell), see [`test-app/ARCHITECTURE.md`](test-app/ARCHITECTURE.md).

## Source of truth for what to build

- [`feature-checklist.md`](feature-checklist.md) — the customer-provided feature list (33 items) plus three priority slices on top (Prototype, Right-sidebar parity, text-range). Tick items as they ship.
- [`execution-map.md`](execution-map.md) — the wave-by-wave implementation order. Top of the file is a per-session log of what shipped; below is only the pending work, always renumbered to start from Wave 1.

The session workflow that keeps these two files honest is documented in [`CLAUDE.md`](CLAUDE.md) under **Session workflow (mandatory)**.

## Reference material

Documentation corpus and synthesized analysis live under [`helper/`](helper/). Three entry-point docs are sufficient for almost every task:

- [`helper/00-overview.md`](helper/00-overview.md) — project scope, principles, how-to-use workflows.
- [`helper/01-ui-schema-extraction.md`](helper/01-ui-schema-extraction.md) — UI schema (regions, state matrix, color picker, context menu, etc.).
- [`helper/02-feature-research.md`](helper/02-feature-research.md) — ~250 feature specs across 34 categories.

`helper/figma_docs/` (216 scraped Figma help articles) and `helper/analysis/` (synthesized cross-cutting analysis) are reachable from those entry-point docs — don't read them blind.

[`open-source-example/open-pencil/`](open-source-example/open-pencil/) is an open-source Figma-compatible editor kept around as a reference for SceneGraph emitter patterns, inverse-op undo, Figma-HTML clipboard, hit-testing, and snap-guides.

## Regenerating the corpus

The scraped Figma docs already live in `helper/figma_docs/`. If you ever need to rebuild them from scratch:

```bash
cd helper/fetch_script
pip install -r requirements.txt
python3 main.py
```

## Project structure

```
.
├── CLAUDE.md              # AI agent instructions (session workflow + reference map)
├── README.md              # This file
├── feature-checklist.md   # Customer feature list + priority slices
├── execution-map.md       # Session log (top) + pending waves (bottom)
├── test-app/              # The mock app — Vite + React + TS
├── helper/                # Documentation corpus + analysis + extracted feature specs
└── open-source-example/   # OpenPencil reference editor (read-only)
```
