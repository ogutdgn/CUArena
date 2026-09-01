# CLAUDE.md — `envs/ms-word-native/` (this folder)

> **SUPERSEDED — read [`../../docs/decisions/engine-rent-vs-own.md`](../../docs/decisions/engine-rent-vs-own.md) first.**
> This line was replaced by [`envs/ms-word`](../ms-word/) on 2026-06-03. The vendored
> LibreOffice engine (`libreoffice-codebase/`) has been removed from the tree and from git
> history, so nothing here builds as-is. The docs below describe the design as it stood;
> they are kept as a decision record, not as instructions to continue.

> Context file for Claude Code (and other agents) working in `envs/ms-word-native/` (this folder).
> **Short by design** — the real content lives in [`docs/`](docs/). Mirror for
> non-Claude tooling: [`AGENTS.md`](AGENTS.md).

---

## What this folder is now

`envs/ms-word-native/` (this folder) is **(1) the rented LibreOffice _engine_** (`libreoffice-codebase/`,
driven headlessly via **LibreOfficeKit / LOK**), **(2) the MS-Word-clone _decision record
& research_**, **and (3) the clone _app_ itself** (`app/` — Phases 0–1 built & verified).
We are building a native **Qt6 Microsoft-Word clone** as a CUA (computer-using-
agent) RL environment; LibreOffice is rented purely as a document engine behind the LOK
boundary.

> The earlier "reskin LibreOffice's own notebookbar UI" approach (old Phase 1–4) is
> **superseded** — git history retains it.

---

## Read this first (order matters)

1. **[`docs/last-point.md`](docs/last-point.md)** — current state.
2. **[`docs/execution-map.md`](docs/execution-map.md)** — phased roadmap / what's next.
3. **[`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)** — the canonical
   clone architecture (Boundary A, process model, components, the no-core-edits guardrail).
4. **[`docs/research/README.md`](docs/research/README.md)** — the research catalog (6 streams);
   findings in [`docs/research/ribbon/`](docs/research/ribbon/) (#1) and
   [`docs/research/tech-stack.md`](docs/research/tech-stack.md) (#2).
5. **[`docs/ui/README.md`](docs/ui/README.md)** — the UI approach (QML + Fluent icons + design tokens).

---

## Locked decisions (one-liners; full rationale in the docs)

- **Engine:** rent LibreOffice via **LOK in-process** (C/C++); **Boundary A** — own
  UI + dispatch + state + logger + MCP, rent the engine only for layout/shaping/`.docx`;
  **scoped parity**; **no-core-edits guardrail** (only sanctioned engine touch = registering
  dialogs in `vcl/jsdialog/enabled.cxx`).
- **Rewrite, not reuse:** the `ms-word-mvp` `writer` prototype proved the architecture but is
  PoC-grade (audited) → **clean rewrite**, keeping the architecture + research + lessons.
- **Tech stack ("Option A"):** native **C++/Qt6 core + QML UI**, in-process LOK on one thread;
  **MCP server as a Python (FastMCP) / TS sidecar** over a local socket.
- **Scope:** v1 builds the **~487 build-surface controls**; engine-gap / cloud-AI / niche
  families are **deferred + documented** (not deleted; engine stays patchable).

---

## Doc map

| Path | Holds |
|---|---|
| `docs/last-point.md` | current state (refresh at session end) |
| `docs/execution-map.md` | phased build roadmap |
| `docs/verification.md` | verification protocol — how every phase/feature proves it works (definition of done, test types, banned anti-patterns) |
| `docs/architecture/ARCHITECTURE.md` | the clone's canonical architecture |
| `docs/architecture/WRITER_CALC_EXTRACTION.md` | engine strip reference (which LO modules can be removed) |
| `docs/research/` | all research: catalog + #1 ribbon (`ribbon/`) + #2 tech-stack (`tech-stack.md`); #3–#6 written at build time |
| `docs/engine-revendor-impact.md` | the pristine engine re-vendor: why, what changed, which doc claims it makes true |
| `docs/ui/README.md` | UI approach (QML + Fluent + design tokens) |
| `app/` | the clone app — Phases 0–1 (C++/Qt6; `mwcore` logic + `mwengine` LOK binding; CMake/CTest) |
| `libreoffice-codebase/` | the vendored LibreOffice engine — pristine LO @ `1f1121d1`, built to LOK, rented unmodified |

---

## Workflow + conventions

- Decisions + research + **Phases 0–1 (the clone app + the in-tree pristine engine)** are
  merged to `main` (branch history: `ms-word/decision-making` → `ms-word/build`, both merged).
  **Phase 2 continues on a fresh branch off `main`** (e.g. `ms-word/ui-kit`).
- **Commits:** Conventional Commits, short messages, **never** a `Co-Authored-By` /
  AI-attribution trailer.
- **Reply in Turkish** to Turkish questions (owner preference); docs stay English.
- Owner wants **trade-offs stated explicitly** and **push-back when warranted** — don't
  blindly agree, and prioritize **quality over speed**.
- **Verification:** every phase/feature meets the definition of done in
  [`docs/verification.md`](docs/verification.md) — *done* = green tests that fail when the
  claim is false.
