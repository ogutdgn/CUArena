# ms-word — Microsoft Word clone (CUA RL environment)

A native **Qt6** Microsoft-Word-like editor, built as a CUA (computer-using-agent) RL
environment. It **owns** the UI, command dispatch, document state, an always-on
raw/semantic/outcome logger, and an MCP server; it **rents** LibreOffice's real engine via
**LibreOfficeKit (LOK)** for layout, text shaping, and `.docx`/`.odt` I/O. We call this line
**Boundary A**.

> **Status: decisions locked; Phases 0–1 built & verified.** The engine choice, the 692-control
> Word↔LibreOffice ribbon research, the tech stack, and the parity scope are all decided and
> recorded; the clone app (`app/`) is scaffolded with the LOK render/scheduler foundations green
> under CMake/CTest, and the engine has been re-vendored to pristine LibreOffice (built, verified
> running). The earlier "reskin LibreOffice's notebookbar" approach is **superseded** (git
> history retains it).

## Start here

1. [CLAUDE.md](CLAUDE.md) — agent guide, read-order, and locked decisions (read first).
2. [docs/last-point.md](docs/last-point.md) — current state.
3. [docs/execution-map.md](docs/execution-map.md) — phased build roadmap.
4. [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) — Boundary A, process model, components.
5. [docs/research/README.md](docs/research/README.md) — the research catalog (ribbon + tech-stack done; per-feature / UI-tokens / MCP / verifier happen at build time).

## What's where

| Path | What |
|---|---|
| [CLAUDE.md](CLAUDE.md) / [AGENTS.md](AGENTS.md) | agent guides — decisions, doc map, conventions |
| [docs/](docs/) | decisions + research: `architecture/`, `research/` (ribbon, tech-stack), `ui/`, `last-point.md`, `execution-map.md`, `engine-revendor-impact.md` |
| [app/](app/) | the clone app — Phases 0–1 (C++/Qt6; `mwcore` logic + `mwengine` LOK binding; CMake/CTest) |
| [libreoffice-codebase/](libreoffice-codebase/) | vendored LibreOffice engine — pristine LO @ `1f1121d1`, rented via LOK, unmodified |

The clone app (`app/`) is built on `ms-word/build` (cut from `main`) following the phases in
[docs/execution-map.md](docs/execution-map.md); Phases 0–1 are done, Phase 2 (live QML window +
UI kit) is next.
