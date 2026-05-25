# AGENTS.md — Writer app

> Mirror of [`CLAUDE.md`](CLAUDE.md) for Codex / other non-Claude tooling.
> Same content applies; the authoritative, regularly-updated guidance is the
> documentation set under [`docs/`](docs/).

## Start here (read in order)

1. [`docs/last-point.md`](docs/last-point.md) — current state.
2. [`docs/execution-map.md`](docs/execution-map.md) — what's next.
3. [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) — design.
4. [`docs/DECISIONS.md`](docs/DECISIONS.md) — decisions + rationale.
5. [`docs/architecture/LOK_REFERENCE.md`](docs/architecture/LOK_REFERENCE.md) — LOK API map.
6. [`docs/architecture/LOGGING.md`](docs/architecture/LOGGING.md) — logger.
7. [`docs/progress/`](docs/progress/) — session notes.

## One-sentence project

Modern native (Qt 6 / QML) MS-Word-like word processor that owns the UI +
command dispatch + state + logging + MCP surface and drives LibreOffice's
real engine headlessly via LibreOfficeKit (LOK) for layout + shaping +
.docx/.odt I/O. Writer only. CUA RL environment, MCP later.

## Core values

Quality > speed · easy UI iteration · MCP-ready · logger-complete. Record
critical decisions in [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Rules

- Conventional Commits `<type>(writer): ...`; **no AI-attribution footer**.
- Build-verify + smoke-test before "done".
- Don't edit the engine except the sanctioned `vcl/jsdialog/enabled.cxx`
  dialog registration (DECISIONS D6).
- Keep `last-point.md` / `execution-map.md` / `DECISIONS.md` in sync with code.
