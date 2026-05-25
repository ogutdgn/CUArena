# CLAUDE.md — Writer app

> Agent guide for the **modern native Writer app**. This file is short; all
> real guidance lives in [`docs/`](docs/). Read the docs in order below
> before starting any task here.

---

## Read this first (order matters)

1. **[`docs/last-point.md`](docs/last-point.md)** — what actually exists now.
2. **[`docs/execution-map.md`](docs/execution-map.md)** — what's queued next.
3. **[`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)**
   — the canonical design (Boundary A, components, LOK loop, dialogs,
   structure, distribution).
4. **[`docs/DECISIONS.md`](docs/DECISIONS.md)** — *why* things are the way
   they are; rejected alternatives. Append new critical decisions here.
5. **[`docs/architecture/LOK_REFERENCE.md`](docs/architecture/LOK_REFERENCE.md)**
   — LOK capability map (don't re-research; extend).
6. **[`docs/architecture/LOGGING.md`](docs/architecture/LOGGING.md)** — the
   raw/semantic/outcome logger (figma-parity, contract-conformant).
7. **[`docs/progress/`](docs/progress/)** — per-session progress notes.

`last-point.md` / `execution-map.md` are refreshed at session end. Mirror of
this guide for non-Claude tooling: [`AGENTS.md`](AGENTS.md).

---

## Project in one sentence

A modern, native (Qt 6 / QML) Microsoft-Word-like word processor that
**owns** the entire UI + command/dispatch + state + logging + MCP surface,
and **drives LibreOffice's real engine headlessly via LibreOfficeKit (LOK)**
for layout + text shaping + .docx/.odt I/O. CUA RL environment, MCP-bound
later. **Writer only.**

---

## Core values (arbitrate every trade-off)

1. **Quality > speed.** No quick/temporary hacks; professional solutions.
2. **Easy UI iteration** (QML, hot-reloadable, ours).
3. **MCP-ready** — the command dispatch seam is the MCP seam.
4. **Logger-complete** — raw/semantic/outcome, figma-parity, always.

When a critical decision comes up, choose by these values and **record it in
[`docs/DECISIONS.md`](docs/DECISIONS.md)** with rationale + rejected options.

---

## Working rules

- **No `Co-Authored-By: Claude`** (or any AI attribution) in commits — owner
  request, carried over from the libreoffice app. Conventional Commits:
  `<type>(writer): <subject>`.
- **Build-verify + smoke-test** before declaring done. Don't start the next
  step on a red build.
- **Don't touch the engine** day-to-day. The *one* sanctioned exception is
  registering dialogs in `vcl/jsdialog/enabled.cxx` (DECISIONS D6).
- **Keep docs in sync** — update `last-point.md` / `execution-map.md` /
  `DECISIONS.md` in the same change as the code. Doc drift = build failure.
- **Reply in Turkish** to Turkish questions (owner preference); docs stay
  English.
- Owner wants **trade-offs stated explicitly** and push-back when warranted
  — don't blindly agree.

---

## Relationship to the rest of the repo

- The **engine** is the (Writer-stripped) LibreOffice tree, currently at
  `../libreoffice/libreoffice-codebase/`. It is a build-time dependency, not
  this app's code. See ARCHITECTURE §9.
- The cross-app log contract is
  [`../../overview/log-contract.md`](../../overview/log-contract.md); the
  figma logger (`../figma/mock/src/logger/`) is the detail bar.
- This app supersedes the libreoffice app's Phase 4 "reskin" direction with
  a from-scratch native build (DECISIONS D1).
```
