# writer — modern native Word-like CUA app

A **modern, native desktop word processor** (Qt 6 / QML) that looks and
behaves like Microsoft Word, built as a CUA (Computer-Using-Agent) RL
environment with a future MCP control surface.

We **own** the entire user-facing app — UI, dialogs, command/dispatch
mechanism, document state, logging, theming, MCP — and **drive
LibreOffice's real engine headlessly via LibreOfficeKit (LOK)** for the
decades-deep parts that would be a quality trap to reimplement: document
**layout**, **text shaping**, and **.docx/.odt I/O**. (Same proven model as
Collabora Online / the LO mobile apps — native UI + LOK tiled rendering +
UNO command dispatch — but with a from-scratch modern shell.)

**Scope:** Writer only.

## Docs

| Doc | What |
|---|---|
| [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) | canonical design |
| [docs/DECISIONS.md](docs/DECISIONS.md) | critical decisions + rationale |
| [docs/architecture/LOK_REFERENCE.md](docs/architecture/LOK_REFERENCE.md) | LOK capability map |
| [docs/architecture/LOGGING.md](docs/architecture/LOGGING.md) | raw/semantic/outcome logger |
| [docs/last-point.md](docs/last-point.md) · [docs/execution-map.md](docs/execution-map.md) | state · roadmap |
| [CLAUDE.md](CLAUDE.md) · [AGENTS.md](AGENTS.md) | agent guides |

## Status

**Phase W0 (foundations).** Decisions locked, LOK feasibility confirmed,
docs in place. Next: W1 — Writer-only engine strip + headless LOK build +
proof-of-life. Roadmap W0–W8 in [docs/execution-map.md](docs/execution-map.md).
