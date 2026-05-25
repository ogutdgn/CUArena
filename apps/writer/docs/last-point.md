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

**Phase W1 — Engine (DONE — built + proof-of-life passed):**

- **Engine built**: LibreOfficeDev **26.8.0.0.alpha0**, headless, Writer-focused
  flags (gtk/qt/kf/avmedia disabled). `instdir` ~622 MB, 188 `.so`, LOK headers
  present. Recipe + gotchas in
  [`architecture/ENGINE_BUILD.md`](architecture/ENGINE_BUILD.md) §6.
- **LOK proof-of-life PASSED** (`tests/lok_proof_of_life.cpp`): headless init →
  load Writer → paintTile (rendered) → `.uno:InsertText`+`.uno:Bold` →
  saveAs docx+odt; verified docx has our text + `<w:b/>` bold.
  **Boundary A proven end-to-end.**
- Engine smoke: `--version` + txt→docx + txt→pdf all OK.
- **Command catalog** — `tools/gen_command_catalog.py` →
  `resources/command-catalog.json`, **1520 commands**. Feeds UI/dispatch/logger/MCP.
- **Writer functionality map** — `tools/extract_menu_tree.py` →
  `resources/writer-menu-tree.json`, 11 menus / 497 items, 496/497 in catalog.

## Built / code

- `tests/lok_proof_of_life.cpp` (LOK integration smoke, header-only `-ldl`).
- `tools/gen_command_catalog.py` + `tools/extract_menu_tree.py` (+ generated JSON).
- Engine `instdir/` built (gitignored, not committed).

## Environment notes (for next session)

- Build toolchain installed (owner): `libtool`/`ccache` + Qt6
  (`qt6-base-dev`/`qt6-declarative-dev`/`cmake`/`ninja`, Qt **6.4.2**).
- LOK usage: compile `-I <engine>/include ... -ldl`; `#define LOK_USE_UNSTABLE_API`;
  run with `SAL_USE_VCLPLUGIN=svp LO_RL_LOG_DISABLE=1`; `saveAs` format = extension.
- Strip (Calc/Impress/Math) NOT yet done — deferred optimization.

## Current branch

`improve-lo-test` — W0 done; **W1 done** (engine + LOK proof-of-life). Next:
**W2** — Qt app skeleton + LOK binding (Qt6 ready). See
[`execution-map.md`](execution-map.md).
```
