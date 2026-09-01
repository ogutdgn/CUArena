# System Overview

`cua-bench` is a benchmark for Computer Use Agents. It contains four CUA environments — three TypeScript browser mocks (Figma, Google Sheets, Google Docs) and one real Linux binary (a stripped LibreOffice fork covering Writer / Calc / Impress) — each paired with a logger. Mocks have verifiers shipping alongside; the libreoffice runtime is logger-only for now (verifier planned for a later phase). Agents interact with the environments; logs are scored.

The point of the system is to evaluate **how** an agent achieves a goal, not just whether the final state is right. Two agents can both produce "a square inside a frame", but one did it via direct creation in a frame context (3 actions) and another did it via copy-paste-reparent (8 actions). The semantic event stream and the efficiency multiplier in the verifier surface that difference.

---

## The pieces

```
┌──────────────────┐     ┌──────────────────┐
│ Mock app (UI)    │ ──► │ Three log streams│
│                  │     │  raw / semantic  │
│ figma | sheets   │     │  / outcome       │
│       | docs     │     │                  │
└──────────────────┘     └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Per-app verifier │
                         │ Task → Rubrics   │
                         │ → Checks         │
                         └────────┬─────────┘
                                  ▼
                         final_score = base × multiplier
```

Per app, the contract is:
- The mock produces `figma-mock-log-<sessionId>.json` (or `sheets-mock-log-…`, `docs-mock-log-…`).
- The verifier reads it, runs the task's rubrics, applies the efficiency multiplier, returns a final score in `[0, 1]`.

---

## The three log streams (cross-app)

| Stream | Source | Used by verifier? |
|---|---|---|
| `raw` | every DOM input event (pointer, key, wheel, clipboard) | no — forensics only |
| `semantic` | every meaningful operation dispatched by the engine | yes — efficiency rubric reads turn count |
| `outcome` | live snapshot of full document + summary counts | yes — fundamentals/alignment/color/etc. read here |

The full schema for figma is at [apps/figma/app-docs/logging-documentation.md](../apps/figma/app-docs/logging-documentation.md). Sheets and Docs will have analogous docs once those apps exist. The cross-app contract (what every mock must emit) lives at [log-contract.md](log-contract.md) — currently a placeholder.

---

## Why four apps

A single mock would test agents only against one UI archetype. The four chosen here are deliberately different:

| App | Shape | Primary primitives | What it stresses |
|---|---|---|---|
| **Figma** | TS mock | shapes on a canvas, properties panel, frames | spatial reasoning, drag/drop, geometry, fills/strokes |
| **Sheets** | TS mock | grid, cells, formulas, ranges | tabular reasoning, formula composition, range selection |
| **Docs** | TS mock | text runs, paragraphs, lists, comments | text editing, caret/range, formatting persistence |
| **LibreOffice** | real Linux binary | Writer / Calc / Impress UI (MS-Office-parity ribbon) | transferring agent skills trained on real Office to an open-source equivalent — real OS-level windows, menus, keyboard focus, GTK widgets |

Together they cover the bulk of office-style CUA evaluation surface area, plus the real-binary case that catches behaviours specific to native UIs (window manager interaction, OS clipboard, focus-stealing dialogs) that browser mocks abstract away.

**Real binary vs TS mock — what's different about the libreoffice app:**
- Built from a vendored LibreOffice fork at [apps/ms-word/libreoffice-codebase/](../apps/ms-word/libreoffice-codebase/), not from TypeScript. Requires a WSL/Linux build (~30 min with cached tarballs, ~3 h cold).
- Logger is a C++ module ([rllogger/](../apps/ms-word/libreoffice-codebase/rllogger/)) linked into the binary, default-on, writes to `~/.lo-rl-logs/<sessionId>/`. Same three-stream contract as the TS mocks.
- No verifier yet — Phase 5/6 will add Calc and Impress equivalents of Phase 4's Writer UI parity; verifier framework comes after that.

---

## Per-app structure

Every app in `apps/` follows the same shape:

```
apps/<app>/
├── CLAUDE.md              app-level agent guide
├── app-docs/              ALL docs: feature-checklist + execution-map + mock-doc/ + verifier-doc/ + scripts-doc/ + helper/
├── mock/                  the mock UI codebase
├── verifier/              the verifier framework (Python library, namespace package)
├── delivery-1/            per-task package (prompt.md + verifier.py per task)
└── scripts/               CLI entry-points (run_task / score_log / qa_verifiers) + logs/scores output
```

The `app-docs/helper/`, `mock/`, `verifier/` folders are **per-app** — not shared. Once two apps are shipped end-to-end, the shared parts of the verifier framework will be extracted to `shared/`.

---

## Roadmap pointer

For the order of work and milestones see [roadmap.md](roadmap.md).
