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

**Phase W2 — Qt app + LOK binding (code done + verified headless; GUI run pending QML modules):**

- **Qt6 app skeleton builds** — `CMakeLists.txt` + `src/main.cpp` +
  `src/ui/qml/Main.qml` (Word-like ribbon tab strip + canvas + status bar, dark).
- **LOK binding** — `src/engine/LokEngine.{h,cpp}` (QObject wrapping
  `lok::Office`/`Document`; init/load/save, `getDocumentSize`, `renderTile`
  paintTile→QImage, `postUno`/`postKey`/`postMouse`, callback thunk →
  queued Qt signals `tilesInvalidated`/`documentSizeChanged`/`unoStateChanged`;
  Office kept alive to dodge teardown abort).
- **Tile canvas** — `src/ui/DocumentCanvas.{h,cpp}` (QQuickPaintedItem,
  blits the rendered page; repaints on engine signals).
- **Verified headless** (`tests/render_test.cpp`, `writer_render_test`):
  LokEngine init + loadBlankWriter OK; `renderTile` → valid 820×1050 page PNG;
  `postUno(.uno:InsertText)` dispatch confirmed (saved docx via the binding
  contains the inserted text). Text not yet visible in the one-shot headless
  render (reactive invalidate→repaint nuance — resolved by the live GUI loop).

## Built / code

- `tests/lok_proof_of_life.cpp` (W1 LOK smoke, header-only `-ldl`).
- `src/main.cpp`, `src/engine/LokEngine.{h,cpp}`, `src/ui/DocumentCanvas.{h,cpp}`,
  `src/ui/qml/Main.qml`, `CMakeLists.txt`. Builds: `writer` + `writer_render_test`.
- `tools/gen_command_catalog.py` + `tools/extract_menu_tree.py` (+ generated JSON).
- Engine `instdir/` built (gitignored). Qt app `build/` gitignored.

**GUI runs (verified):** QtQuick QML runtime modules installed; offscreen
screenshot shows the Word-like shell + the LOK-rendered (blank) page + status
bar. Input wiring added (`DocumentCanvas` key/mouse → `postKey`/`postMouse`,
Qt→awt key map, px→twip; `LokEngine::typeText`). A headless screenshot mode
(`WRITER_SHOT=<png>`, optional `WRITER_DEMO_TEXT`) is built in.

## Gating finding (D9) — next task

Driving LOK by method calls updates the document **model** (binding-saved
docx contains inserted text) but **does not render edits**: layout +
`INVALIDATE_TILES` + tile re-render need LO's scheduler pumped. Static blank
page renders (no layout needed); **live typing/edits won't render until the
LOK event-loop integration** (dedicated engine thread + `runLoop`,
ARCHITECTURE §4) lands. This is W2's #1 task — see
[`DECISIONS.md`](DECISIONS.md) D9 + [`execution-map.md`](execution-map.md).

## Environment notes (for next session)

- Build toolchain installed (owner): `libtool`/`ccache` + Qt6
  (`qt6-base-dev`/`qt6-declarative-dev`/`cmake`/`ninja`, Qt **6.4.2**).
- LOK usage: compile `-I <engine>/include ... -ldl`; `#define LOK_USE_UNSTABLE_API`;
  run with `SAL_USE_VCLPLUGIN=svp LO_RL_LOG_DISABLE=1`; `saveAs` format = extension.
- Strip (Calc/Impress/Math) NOT yet done — deferred optimization.

## Current branch

`improve-lo-test` — W0 done; W1 done; **W2: GUI runs with a LOK-rendered page,
binding + input wiring done.** Next (W2 #1): LOK event-loop integration (D9) so
live edits render; then tiling/scroll/zoom, then W3 (ribbon). See
[`execution-map.md`](execution-map.md).
```
