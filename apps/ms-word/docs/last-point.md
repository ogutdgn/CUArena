# Last point — MS Word clone

> **Current state, present tense.** This file records what is *true now* on the
> `ms-word/build` branch — decisions locked, research committed, and **Phases 0–1 built
> and verified** — and nothing aspirational. For what comes next, see
> [`execution-map.md`](execution-map.md).

Last updated: 2026-05-30

---

## What `apps/ms-word/` is now

`apps/ms-word/` is **the rented LibreOffice engine + the MS-Word-clone decision record &
research + the clone app (`app/`, Phases 0–1 built)**. The project is a Microsoft Word clone
built as a CUA (computer-using-agent) RL environment inside the `cua-bench` monorepo.

The previous **LibreOffice-reskin approach is superseded** — the old Phase 1–4 work
(stripping LibreOffice, an `rllogger` embedded inside the engine, reskinning LO's
notebookbar) is no longer the plan, and its docs were removed. Git history retains
them; do not treat the reskin as current. The reskin had also left the **engine tree itself**
stripped + carrying `rllogger`; that tree was **re-vendored to pristine LibreOffice** during the
build (see [Build status](#build-status) and
[`engine-revendor-impact.md`](engine-revendor-impact.md)).

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

## Build status

Built on the `ms-word/build` branch (cut from `main`); the clone app lives in
[`app/`](../app/) — a CMake project with plain‑C++ `mwcore` (tile geometry / cache / render
orchestration) and `mwengine` (the LOK engine binding), driven by a real CTest harness +
committed fixtures.

**Engine — re‑vendored to pristine.** The committed `libreoffice-codebase/` was the old
reskin's **hacked/stripped tree** (`rllogger` added, ~34 modules / 5,726 files removed) — it
would not build. It was **re‑vendored to pristine LibreOffice @ `1f1121d1`** (v26.8.0.0.alpha0+),
built headless to a **LOK‑capable** `instdir/program/libsofficeapp.so`, and verified to run (a
real `.docx` round‑trip). The architecture's "engine source committed and fully buildable" is now
actually true. Slimming is done via **configure flags, not file deletion** (full analysis:
[`engine-revendor-impact.md`](engine-revendor-impact.md)). **The ~1.4 GB pristine engine swap is
built locally but intentionally left uncommitted**, pending an in‑tree‑vs‑submodule‑vs‑artifact
decision.

**Phase 0 — merge & scaffold.** ✅ Decisions/research merged to `main`; the clone app scaffolded.

**Phase 1 — foundations.** ✅ The verification bar (test types **A + B + C**, run headless, each
failing when the claim is false) is green — `ctest` → **5/5**. Cited tests:
- **A (unit)** — `tst_tilegrid` (INVALIDATE_TILES dirty‑rect → minimal tile set), `tst_tilecache`
  (zoom‑keyed cache, selective invalidate), `tst_rendercontroller` (paint‑on‑miss; repaint only the
  dirty tile — the anti‑full‑repaint guarantee). Each watched red→green; the full‑repaint and
  over‑invalidate regressions were confirmed red.
- **B (headless LOK)** — `tst_lok_smoke`: load a real‑content fixture → `.uno:` dispatch →
  `getTextSelection` → `saveAs` `.docx` → reload, asserting the content round‑trips. Driven through
  the **real engine** with a **deterministic step boundary**: `Scheduler::ProcessEventsToIdle()`
  held under the `Application` SolarMutex — real public symbols, **not** the banned test‑only
  `unit_lok_process_events_to_idle`. Red‑checked (fails when the content is absent).
- **C (render golden‑frame)** — `tst_render_golden`: render the fixture's top‑left tile at 100% via
  the real `paintTile` through `RenderController`, asserting **real laid‑out ink** (2,220 opaque
  dark pixels, not a blank page) **and** an **exact byte‑stable golden hash** of the BGRA tile.

No banned anti‑pattern (verification.md) was introduced: the pump uses a **real public** engine
symbol (no test‑only symbol); rendering honors the dirty rect via `TileGrid`/`TileCache` (no
full‑repaint); tests assert **real content** (no blank‑doc, no "did not crash"); the step boundary
is the **synchronous pump** (no wall‑clock sleep).

---

## Not yet done

- **Live interactive QML window.** Phase 1 proved the render path headlessly (golden frame); a
  live, scrollable, clickable window needs the Qt‑GUI ⇄ dedicated‑LOK‑thread structure (a
  `QGuiApplication` conflicts with LO's VCL app singleton) — Phase 2 territory.
- **Per-feature behavior + state specs (stream #3)** — done at build time, just-in-time
  per feature group; feeds both the build and the verifier.
- **UI design-token extraction (stream #4)** — done early in the build (Word M365 exact
  colors/metrics/icons/typography → QML tokens).
- **MCP tool-surface design (stream #5)** — done in the MCP phase.
- **Verifier design (stream #6)** — done in the verifier phase.

---

## Next

1. **Phase 2 — the live UI kit:** the interactive QML window (Qt‑GUI ⇄ dedicated‑LOK‑thread; a
   tile canvas with scroll / zoom / HiDPI over the now‑working `paintTile` path), the design‑token
   system, and the bespoke ribbon / galleries / JSDialog‑to‑QML dialogs.
2. **Decide the engine‑commit strategy** (in‑tree vs. git‑submodule vs. fetched artifact) and land
   the pristine engine accordingly.
3. **Reconcile the remaining engine‑state docs** per
   [`engine-revendor-impact.md`](engine-revendor-impact.md) (the "committed / fully buildable" claims
   are now true; the ribbon‑research re‑anchoring to stock `notebookbar.ui` is already done).
