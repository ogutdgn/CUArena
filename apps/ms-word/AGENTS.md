# AGENTS.md — `apps/ms-word/`

> Canonical guide for AI coding agents (Codex, Cursor, Copilot, Claude, …) working in
> `apps/ms-word/`. Mirror of [`CLAUDE.md`](CLAUDE.md), with a bit more detail. **Read the
> `docs/` set before starting any task** (order below).

---

## 1. What this folder is

`apps/ms-word/` = **(1) the rented LibreOffice _engine_** (`libreoffice-codebase/`, driven
headlessly via **LibreOfficeKit / LOK**) **+ (2) the MS-Word-clone _decision record & research_.**

We are building a **native Qt6 Microsoft-Word clone** as a CUA (computer-using-agent) RL
environment. LibreOffice is **rented** purely as a document engine (layout, text shaping,
`.docx`/`.odt` I/O) behind the **LOK** C API; everything that makes the product *Word* — UI,
command dispatch, document state, an always-on logger, and an **MCP server** — is **ours**
(this is "Boundary A").

> The earlier approach — fork LibreOffice, strip it, embed an `rllogger`, and reskin its
> notebookbar to look like Word (old Phase 1–4) — is **superseded**. Its docs were removed;
> git history retains them. Do not treat the reskin as current.

---

## 2. Read this first (order matters)

1. [`docs/last-point.md`](docs/last-point.md) — current state.
2. [`docs/execution-map.md`](docs/execution-map.md) — phased roadmap / what's next.
3. [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) — canonical clone
   architecture: Boundary A, the process model (in-process LOK + MCP sidecar), components, the
   no-core-edits guardrail, distribution.
4. [`docs/research/README.md`](docs/research/README.md) — the research catalog.
5. [`docs/ui/README.md`](docs/ui/README.md) — the UI approach.

---

## 3. Locked decisions

- **Engine:** rent LibreOffice via **LOK in-process** (C/C++). **Boundary A**: own
  UI + dispatch + document state + raw/semantic/outcome logger + MCP; rent the engine only for
  layout/shaping/file I/O. **Scoped parity** (indistinguishable within scope; out-of-scope
  entry points removed). **No-core-edits guardrail**: never edit engine logic to chase a
  feature; the one sanctioned touch is registering dialogs in `vcl/jsdialog/enabled.cxx`. The
  guardrail is policy, not a wall — the engine is committed, buildable, and patchable as
  tracked patches if a feature ever justifies it.
- **Rewrite, not reuse:** the `ms-word-mvp` `writer` prototype proved Boundary A works but a
  multi-agent audit found it PoC-grade (test-only render symbol, full-repaint per keystroke,
  non-credible tests, broken dialog metrics, non-scaling ribbon). Verdict: **clean rewrite**
  keeping the architecture + research + lessons.
- **Tech stack ("Option A"):** native **C++/Qt6 core** driving LOK in-process on one dedicated
  thread (single-threaded per document; parallel rollouts = parallel containers); **QML Fluent
  UI** chrome (document pixels come from LOK tiles, toolkit-independent); **MCP server = a
  separate Python (FastMCP) / TypeScript sidecar** over a local socket (no mature C++ MCP SDK).
  Rejected: web/two-process and single-language Rust/Go/Python LOK-FFI.
- **Scope:** v1 builds the **~487 build-surface controls** (Free + Our-layer-UI + Behavior-shim
  + Optional, ~70% of Word's ribbon). The engine-gap, cloud/AI, and niche families are
  **deferred + documented**, not deleted (see each ribbon tab doc's "Out of scope" section).

---

## 4. Research streams (catalog in `docs/research/README.md`)

| # | Stream | Status | When |
|---|---|---|---|
| #1 | Ribbon structure (Word↔LO, 692 controls) | ✅ done | `docs/research/ribbon/` |
| #2 | Tech-stack decision | ✅ done | `docs/research/tech-stack.md` |
| #3 | Per-feature behavior + state specs (incl. enabled/disabled/checked rules) | ⏳ build-time | per feature-group |
| #4 | UI design-token extraction (Word M365 colors/metrics/typography → QML tokens) | ⏳ build-time | early in build |
| #5 | MCP tool-surface design | ⏳ later | MCP phase |
| #6 | Verifier design (fed by #3) | ⏳ later | verifier phase |

---

## 5. Build phases (full detail in `docs/execution-map.md`)

**0** merge decisions to `main` + scaffold the fresh clone app on a build branch → **1**
refactor-grade foundations (correct LOK render/scheduler path + a real CMake/CTest harness) →
**2** UI design-tokens + bespoke control kit → **3** per-feature build loop (spec → implement →
verify, group by group) → **4** MCP sidecar → **5** verifier → **6** Docker/headless
distribution. (Optional: strip the engine to Writer-only.)

---

## 6. The engine

`libreoffice-codebase/` is the vendored LibreOffice tree. It is built to **LOK** (the headless
`instdir/` + LOK headers) and **not edited day-to-day** (the guardrail in §3). The clone links
the engine only at the LOK C API — no LO library at link time (header-only LOK client +
runtime `dlopen` of `instdir/program`), so the engine stays a swappable, patchable dependency.
Engine build recipe details belong with the build tooling on the build branch.

---

## 7. Conventions

- **Branch flow:** decisions/research on `ms-word/decision-making` → merge to `main` → build on
  a fresh branch off `main`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) `<type>(<scope>): <subject>`;
  short messages; **NEVER** a `Co-Authored-By` / AI-attribution trailer.
- **Owner preferences:** reply in **Turkish** to Turkish questions (docs stay English); state
  **trade-offs explicitly**; **push back** with a counter-view when warranted; **quality over
  speed**.
- Keep `docs/last-point.md` and `docs/execution-map.md` current at session end.
