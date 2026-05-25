# Writer — Last Point

> **Current state of `apps/writer/`** — what actually exists, nothing
> aspirational. Pairs with [`execution-map.md`](execution-map.md) (what's
> next). Refresh at session end.
>
> Last updated: 2026-05-25.

---

## Done

**Phase W0 — Foundations (this session, branch `improve-lo-test`):**

- **All foundational decisions locked** — see [`DECISIONS.md`](DECISIONS.md)
  D1–D8 + D-icons. Headline: Boundary A (own UI/dispatch/state/logging/MCP;
  rent LO engine via LOK for layout/shaping/.docx-I/O); Qt 6 (C++ + QML);
  Fluent icons; Writer-only; engine = separate dependency; logger in our
  layer; Docker ships binary.
- **LOK feasibility research done** — full capability map in
  [`architecture/LOK_REFERENCE.md`](architecture/LOK_REFERENCE.md). Verdict:
  feasible. LOK C++ API complete; 72 callbacks; 552 Writer + 993 generic
  `.uno:` commands; `gtktiledviewer` reference; qt6 backend present. One
  risk: selective JSDialog coverage → mitigation = extend engine
  `enabled.cxx` (D6).
- **Architecture written** —
  [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) (layered
  model, components, LOK loop, dialog strategy, structure, distribution).
- **Logger design written** —
  [`architecture/LOGGING.md`](architecture/LOGGING.md) (figma-parity,
  contract-conformant, sourced from our dispatch seam).
- **Repo plumbing:** branch `improve-lo-test`; `apps/writer/` doc scaffold;
  `.claude/settings.local.json` permission allowlist (gitignored).

**Phase W1 — Engine (in progress, committed):**

- Engine build recipe finalized →
  [`architecture/ENGINE_BUILD.md`](architecture/ENGINE_BUILD.md) (headless
  Writer-only LOK; flags verified vs `configure.ac`; `--disable-gtk3/qt*` +
  `--enable-mergelibs`, core LOK C API not gtk glue).
- **Command catalog built** — `tools/gen_command_catalog.py` →
  `resources/command-catalog.json`, **1520 commands** (977 generic + 543
  writer) with labels/tooltips/semanticName/propertiesRaw. Build-independent,
  verified. Feeds UI + dispatch + logger + MCP.

## Built / code

- `apps/writer/tools/gen_command_catalog.py` (+ generated
  `resources/command-catalog.json`). No compiled code yet (engine build +
  Qt app skeleton are blocked on deps — see below).

## Blocked on

- **Build deps (owner sudo).** Engine build + Qt6 not installable by me.
  Exact `sudo apt` commands in
  [`progress/2026-05-25-w0-w1-kickoff.md`](progress/2026-05-25-w0-w1-kickoff.md).

## Current branch

`improve-lo-test` — W0 done; W1 design + command catalog done; engine build
blocked on owner deps. Next: configure+build engine, then Qt skeleton +
LOK proof-of-life. See [`execution-map.md`](execution-map.md).
```
