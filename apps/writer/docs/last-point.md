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

## Built / code

_(none yet — W0 is docs + decisions only. First code lands in W1/W2.)_

## Current branch

`improve-lo-test` — W0 in progress. Next: **W1** (engine Writer-only strip +
headless LOK build + proof-of-life). See [`execution-map.md`](execution-map.md).
```
