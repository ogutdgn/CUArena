# Last point — MS Word clone

> **Current state, present tense.** This file records what is *true now* on the
> `ms-word/decision-making` branch — decisions locked and research committed — and
> nothing aspirational. For what comes next, see
> [`execution-map.md`](execution-map.md).

Last updated: 2026-05-29

---

## What `apps/ms-word/` is now

`apps/ms-word/` is **the rented LibreOffice engine + the MS-Word-clone decision
record & research**. The project is a Microsoft Word clone built as a CUA
(computer-using-agent) RL environment inside the `cua-bench` monorepo.

The previous **LibreOffice-reskin approach is superseded** — the old Phase 1–4 work
(stripping LibreOffice, an `rllogger` embedded inside the engine, reskinning LO's
notebookbar) is no longer the plan, and its docs were removed. Git history retains
them; do not treat the reskin as current.

---

## Locked decisions

All foundational decisions are made and recorded on this branch.

- **Engine — LibreOffice via LOK (in-process), "Boundary A."** We rent LibreOffice's
  real engine through LibreOfficeKit (in-process C/C++) for layout, text shaping, and
  `.docx`/`.odt` I/O. We **own** the UI, command dispatch, document state, an always-on
  raw/semantic/outcome logger, and an MCP server.
- **Discipline — scoped parity + no-core-edits.** Indistinguishable within scope, entry
  points removed outside it. We do not edit LO engine logic to chase a feature; the only
  sanctioned engine touch is registering dialogs in `vcl/jsdialog/enabled.cxx`. The
  guardrail is policy, not a wall — the engine source is committed and fully buildable,
  so deeper patches remain possible later as tracked changes if a feature justifies the
  fork-maintenance cost.
- **Clean rewrite.** A prior Qt6/QML prototype (the `writer` app on branch
  `ms-word-mvp`) proved Boundary A works but was found PoC-grade by audit. The verdict is
  a clean rewrite that keeps the proven architecture, this research, and the audit's
  lessons.
- **Tech stack — "Option A."** Native C++/Qt6 core driving LOK in-process on one
  dedicated LOK-owning thread, with a synchronous scheduler-pump step boundary for
  determinism; QML Fluent UI for all chrome (document pixels come from LOK's tile
  buffer); and the MCP server as a separate Python (FastMCP) or TypeScript sidecar over a
  local socket. The core stays the single source of truth; the sidecar holds no state.
- **Scope.** v1 builds the **~487-control build surface** (core editing/formatting +
  Insert/References/Mailings/Review/Layout/Design/View). Three families are **deferred
  and documented** (not deleted, door kept open): (A) engine-gap families (Draw/ink,
  SmartArt/Icons/3D, WordArt, Building Blocks, Table of Authorities, style citations,
  Style Sets), (B) cloud/AI (Copilot, Dictate, Transcribe, AI Editor, Smart Lookup,
  Researcher, online pictures), and (C) niche (CJK envelopes/postcards, postal barcodes,
  M365 reading modes, Activation).
- **Verification discipline.** Every phase / feature meets the definition of done in
  [`verification.md`](verification.md) — *done* = green tests (CMake/CTest, headless) that
  fail when the claim is false. The per-phase bar and per-feature DoD live there.

---

## Committed research

- **Ribbon structure** — [`research/ribbon/`](research/ribbon/) (committed `ea97f7039`).
  A verified Word ↔ LibreOffice comparison across all 10 Word ribbon tabs, **692
  controls**. Work-bucket totals: Free 89 (13%), Our-layer UI 231 (33%), Behavior shim
  144 (21%), Engine gap 114 (16%), Cut 91 (13%), Optional 23 (3%). The build surface we
  own (Free + Our-layer UI + Behavior shim + Optional) = **487 (~70%)**. Engine gap is
  **zero in core document work** — editing, formatting, Track Changes, Mail Merge,
  References, and Layout all map to LO commands — and is entirely cuttable feature
  families.
- **Tech-stack decision** — [`research/tech-stack.md`](research/tech-stack.md). The
  "Option A" rationale, with web/two-process and single-language Rust/Go/Python FFI
  rejected.
- **Writer-app audit** — a one-off investigation of the prior Qt6/QML prototype. Verdict:
  **rewrite** (PoC-grade render path, non-credible test ledger, broken dialog
  metric-fields, non-scaling ribbon).

---

## Not yet done

- **No clone code exists yet.** This branch holds decisions and research only.
- **Per-feature behavior + state specs (stream #3)** — done at build time, just-in-time
  per feature group; feeds both the build and the verifier.
- **UI design-token extraction (stream #4)** — done early in the build (Word M365 exact
  colors/metrics/icons/typography → QML tokens).
- **MCP tool-surface design (stream #5)** — done in the MCP phase.
- **Verifier design (stream #6)** — done in the verifier phase.

---

## Next

1. **Merge** `ms-word/decision-making` to `main`.
2. **Build the clone on a fresh branch** off `main` — a new app directory, following the
   build phases in [`execution-map.md`](execution-map.md).
