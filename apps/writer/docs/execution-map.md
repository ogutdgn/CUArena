# Writer — Execution Map

> **What's queued next** — nothing else. Refresh at session end. Pairs with
> [`last-point.md`](last-point.md) (what's done). Full design context in
> [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md).
>
> Last updated: 2026-05-25.

---

## Phase roadmap (W0–W8)

| Phase | Goal | Status |
|---|---|---|
| **W0** | Foundations: decisions locked, LOK feasibility research, docs scaffold, permissions, branch | **done** |
| **W1** | Engine: headless LOK build + proof-of-life (strip deferred) | **DONE** — engine built (26.8 alpha), LOK proof-of-life passed end-to-end |
| **W2** | Qt app skeleton + LOK binding: CMake, `LokEngine` wrapper, tile render→QML canvas, load/save, dispatch, callbacks→signals | **code done + verified headless**; GUI run pending owner QtQuick QML modules |
| **W3** | Command mechanism + ribbon UI: catalog from `*.xcu`, dispatch (**native semantic emit**), Word-like QML ribbon + Fluent icons, `STATE_CHANGED` state | |
| **W4** | Dialogs: `JSDIALOG`→native Qt/QML, `sendDialogEvent`, coverage audit + extend engine `enabled.cxx` for gaps | |
| **W5** | Logger figma-parity: full semantic registry, outcome snapshot, `semanticEventCount`, consolidator, contract conformance | |
| **W6** | MCP surface: dispatch + state + document ops as MCP tools | |
| **W7** | Docker multi-stage: engine→LOK + app → binary runtime, logger default-on | |
| **W8** | Theming/polish: Word palette, Fluent refinement, context menus, a11y | |

---

## W1 — Engine (LOK) — ✅ DONE

- Engine built (LO 26.8.0.0.alpha0, headless), recipe + gotchas in
  [`architecture/ENGINE_BUILD.md`](architecture/ENGINE_BUILD.md) §6.
- LOK proof-of-life passed end-to-end (`tests/lok_proof_of_life.cpp`):
  load → paintTile → `.uno` dispatch → saveAs docx/odt, content verified.
- Command catalog + Writer menu/functionality map generated.
- **Deferred (W1-tail, optimization, not blocking):** strip Calc/Impress/Math;
  `--enable-mergelibs` rebuild. Do opportunistically after W2 is moving.

## W2 — Qt app + LOK binding

Done (code + headless verification):
- ✅ CMake project (Qt6 6.4.2) — `writer` + `writer_render_test` build clean.
- ✅ Qt shell (`main.cpp` + `Main.qml`) — Word-like window placeholders.
- ✅ `LokEngine` binding — init/load/save, `renderTile` (paintTile→QImage),
  `postUno`/`postKey`/`postMouse`, callbacks→queued Qt signals.
- ✅ `DocumentCanvas` (QQuickPaintedItem) blits the page, repaints on signals.
- ✅ Verified headless: render path → valid page PNG; `postUno` dispatch
  confirmed via binding-saved docx.

Also done:
- ✅ QtQuick QML runtime modules installed (owner); **GUI runs** — verified by
  offscreen screenshot: Word-like shell + LOK-rendered (blank) page + status bar.
- ✅ Input wiring code — `DocumentCanvas` forwards key/mouse to
  `postKey`/`postMouse` (Qt→awt key map, px→twip), `LokEngine::typeText`.

Remaining (in priority order):
1. **LOK scheduler / event-loop integration (D9) — THE gating task.** Model
   updates don't render (edits update the doc model but layout +
   `INVALIDATE_TILES` + re-render need LO's scheduler pumped). **Attempt 1
   (runLoop on a worker thread) FAILED** — `soffice_main` needs the main
   thread. **Next: the "inverted loop"** — run `office->runLoop()` on the main
   thread, pump Qt (`processEvents`, likely `QSG_RENDER_LOOP=basic`) in the
   poll callback. Fallback: two-process IPC (Collabora WSD/Kit). See D9.
2. **Verify live edit/render** (screenshot demo: `WRITER_DEMO_TEXT`) once (1) lands.
3. **Tiling + scroll + zoom** — tile cache, `Flickable` viewport, HiDPI,
   `setClientZoom`; cursor/selection overlays from callbacks.
4. **Logger raw-stream scaffold** (`src/logging/`) — grows into W5.

**W2 exit:** GUI opens a doc, renders via LOK tiles, accepts typing with
**live render updates**, saves; `.uno` dispatch wired through the binding.

---

## Open decisions (carry until resolved)

- Engine location & strip depth (W1.1)
- Minimal Writer-only LOK build flags (W1.2)
- Engine-thread ↔ Qt-loop integration (W2)
- Tile cache / HiDPI strategy (W2)
- Dialog coverage gap size vs `completeWriterDialogList()` (W4)
- MCP transport: stdio sidecar vs in-process (W6)
- Log env-var names + outcome cadence (W2/W5)
```
