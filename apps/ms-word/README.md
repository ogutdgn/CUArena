# ms-word — Microsoft Word clone (CUA RL environment)

A native **Qt6** Microsoft-Word-like editor, built as a CUA (computer-using-agent) RL
environment. It **owns** the UI, command dispatch, document state, an always-on
raw/semantic/outcome logger, and an MCP server; it **rents** LibreOffice's real engine via
**LibreOfficeKit (LOK)** for layout, text shaping, and `.docx`/`.odt` I/O. We call this line
**Boundary A**.

> **Status: decisions locked; build not started.** The engine choice, the 692-control
> Word↔LibreOffice ribbon research, the tech stack, and the parity scope are all decided and
> recorded. The earlier "reskin LibreOffice's notebookbar" approach is **superseded** (git
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
| [docs/](docs/) | decisions + research: `architecture/`, `research/` (ribbon, tech-stack), `ui/`, `last-point.md`, `execution-map.md` |
| [libreoffice-codebase/](libreoffice-codebase/) | vendored LibreOffice engine — rented via LOK, not edited day-to-day |

The clone's app code does not exist yet; it is built on a fresh branch off `main` following
the phases in [docs/execution-map.md](docs/execution-map.md).
