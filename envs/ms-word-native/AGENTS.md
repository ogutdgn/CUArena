# AGENTS.md — `envs/ms-word-native/` (this folder)

> **SUPERSEDED — read [`../../docs/decisions/engine-rent-vs-own.md`](../../docs/decisions/engine-rent-vs-own.md) first.**
> This line was replaced by [`envs/ms-word`](../ms-word/) on 2026-06-03. The vendored
> LibreOffice engine (`libreoffice-codebase/`) has been removed from the tree and from git
> history, so nothing here builds as-is. The docs below describe the design as it stood;
> they are kept as a decision record, not as instructions to continue.

> Canonical guide for AI coding agents (Codex, Cursor, Copilot, Claude, …) working in
> `envs/ms-word-native/` (this folder). Mirror of [`CLAUDE.md`](CLAUDE.md), with a bit more detail. **Read the
> `docs/` set before starting any task** (order below).

---

## 1. What this folder is

`envs/ms-word-native/` (this folder) = **(1) the rented LibreOffice _engine_** (`libreoffice-codebase/`, driven
headlessly via **LibreOfficeKit / LOK**) **+ (2) the MS-Word-clone _decision record & research_
+ (3) the clone _app_** (`app/` — Phases 0–1 built & verified).

We are building a **native Qt6 Microsoft-Word clone** as a CUA (computer-using-agent) RL
environment. LibreOffice is **rented** purely as a document engine (layout, text shaping,
`.docx`/`.odt` I/O) behind the **LOK** C API; everything that makes the product *Word* — UI,
command dispatch, document state, an always-on logger, and an **MCP server** — is **ours**
(this is "Boundary A").

> The earlier approach — fork LibreOffice, strip it, embed an `rllogger`, and reskin its
> notebookbar to look like Word (old Phase 1–4) — is **superseded**. Its docs were removed **and
> its damage to the engine tree was undone**: the stripped/`rllogger`-carrying tree was
> re-vendored to pristine LibreOffice (see §6). Git history retains the old work. Do not treat
> the reskin as current.

---

## 2. Read this first (order matters)

1. [`docs/last-point.md`](docs/last-point.md) — current state.
2. [`docs/execution-map.md`](docs/execution-map.md) — phased roadmap / what's next.
3. [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) — canonical clone
   architecture: Boundary A, the process model (in-process LOK + MCP sidecar), components, the
   no-core-edits guardrail, distribution.
4. [`docs/research/README.md`](docs/research/README.md) — the research catalog.
5. [`docs/ui/README.md`](docs/ui/README.md) — the UI approach.
6. [`docs/verification.md`](docs/verification.md) — the verification protocol: the definition
   of done for every phase / feature.
7. [`docs/engine-revendor-impact.md`](docs/engine-revendor-impact.md) — the pristine engine
   re-vendor (what changed in `libreoffice-codebase/` and why); the built app lives in `app/`.

---

## 3. Locked decisions

- **Engine:** rent LibreOffice via **LOK in-process** (C/C++). **Boundary A**: own
  UI + dispatch + document state + raw/semantic/outcome logger + MCP; rent the engine only for
  layout/shaping/file I/O. **Scoped parity** (indistinguishable within scope; out-of-scope
  entry points removed). **No-core-edits guardrail**: never edit engine logic to chase a
  feature; the one sanctioned touch is registering dialogs in `vcl/jsdialog/enabled.cxx`. The
  guardrail is policy, not a wall — the engine source is pristine, fully buildable (verified),
  and patchable as tracked patches if a feature ever justifies it.
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

**0** merge decisions to `main` + scaffold the fresh clone app on a build branch ✅ → **1**
refactor-grade foundations (correct LOK render/scheduler path + a real CMake/CTest harness) ✅ →
**2** UI design-tokens + bespoke control kit → **3** per-feature build loop (spec → implement →
verify, group by group) → **4** MCP sidecar → **5** verifier → **6** Docker/headless
distribution. (Optional: strip the engine to Writer-only.) Phases 0–1 are **built & verified**
(app in `app/`); next is Phase 2.

---

## 6. The engine

`libreoffice-codebase/` is the vendored LibreOffice tree. The old reskin had left it
**stripped + carrying `rllogger`** (it would not build); it was **re-vendored to pristine
LibreOffice @ `1f1121d1`** (v26.8.0.0.alpha0+) and built headless to a LOK-capable
`instdir/program/libsofficeapp.so`, verified running (a real `.docx` round-trip). It is rented
**unmodified** (the guardrail in §3) — slimming is done via configure flags, not file deletion.
The clone links the engine only at the LOK C API — no LO library at link time (header-only LOK
client + runtime `dlopen` of `instdir/program`), so the engine stays a swappable, patchable
dependency. The ~1.4 GB pristine swap is built locally; an in-tree-vs-submodule-vs-artifact
commit decision is **deferred until the engine is frozen**. Full analysis:
[`docs/engine-revendor-impact.md`](docs/engine-revendor-impact.md).

---

## 7. Conventions

- **Branch flow:** decisions/research merged to `main` (was `ms-word/decision-making`); the
  build now happens on `ms-word/build` (cut from `main`), which merges back to `main`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) `<type>(<scope>): <subject>`;
  short messages; **NEVER** a `Co-Authored-By` / AI-attribution trailer.
- **Owner preferences:** reply in **Turkish** to Turkish questions (docs stay English); state
  **trade-offs explicitly**; **push back** with a counter-view when warranted; **quality over
  speed**.
- **Verification:** every phase / feature meets the definition of done in
  [`docs/verification.md`](docs/verification.md) — *done* = green tests that fail when the
  claim is false.
- Keep `docs/last-point.md` and `docs/execution-map.md` current at session end.
