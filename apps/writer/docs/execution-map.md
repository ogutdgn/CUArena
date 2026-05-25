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
| **W2** | Qt app skeleton + LOK binding: CMake, C++ `Office`/`Document` wrapper, tile render→QML canvas, load/save, key/mouse injection, core callbacks **+ logger raw-stream scaffold** | **next** (Qt6 6.4.2 ready) |
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

## Next: W2 — Qt app skeleton + LOK binding

1. **CMake project** (`apps/writer/CMakeLists.txt`) — Qt6 6.4.2 (Core/Gui/Qml/
   Quick/QuickControls2/Svg), C++20, ninja. `src/` layout per ARCHITECTURE §8.
2. **Qt shell** — `QGuiApplication` + `QQmlApplicationEngine`, a Word-like
   `ApplicationWindow` (ribbon tab strip placeholder, document canvas area,
   status bar). Compiles + runs (WSLg or `QT_QPA_PLATFORM=offscreen`).
3. **LOK binding** (`src/engine/`) — C++ `LokEngine` (wraps `Office`/`Document`)
   as a `QObject`: load/save, `getDocumentSize`, `postUnoCommand`,
   key/mouse inject; LOK callback pump → Qt signals (engine thread).
4. **Tile → canvas** — a `QQuickItem`/`QQuickPaintedItem` that blits
   `paintTile` output; repaint on `INVALIDATE_TILES`; `setClientZoom` mapping.
5. **Logger raw-stream scaffold** (`src/logging/`) — session dir + raw events
   from the input layer (grows into W5).
6. Lifecycle: keep `Office` alive for app lifetime (avoid the teardown abort).

**W2 exit:** app window opens a .docx, renders it (LOK tiles), accepts typing,
saves; one `.uno` command wired through the binding.

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
