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
| **W2** | Qt app + LOK binding: CMake, `LokEngine`, tile canvas, load/save, dispatch, **live edit render (D9 resolved)** | mostly done — live typing renders; remaining: tiling/scroll/zoom, cursor/selection overlays |
| **W3** | Command mechanism + ribbon UI: catalog from `*.xcu`, dispatch, Word-like QML ribbon + Fluent icons, `STATE_CHANGED` state | **DONE** — data-driven ribbon (8 tabs / 29 groups / 83 cmds), 80 Fluent icons, toggle state live (D10). Semantic emit → W5; dialog targets → W4 |
| **W4** | Dialogs: `JSDIALOG`→native Qt/QML, `sendDialogEvent`, coverage audit + extend engine `enabled.cxx` for gaps | **core DONE** — generic JSDialog→QML renderer (WordCount/PageDialog verified), round-trip proven, audit written (D11). Remaining: `enabled.cxx` patches for WINDOW-only (InsertTable/Bookmark/Hyperlink) |
| **W5** | Logger figma-parity: full semantic registry, outcome snapshot, `semanticEventCount`, consolidator, contract conformance | |
| **W6** | MCP surface: dispatch + state + document ops as MCP tools | |
| **W7** | Docker multi-stage: engine→LOK + app → binary runtime, logger default-on | |
| **W8** | Theming/polish: Word palette, Fluent refinement, context menus, a11y | |

---

## Open problems / backlog (durable — don't lose these)

Tracked so nothing is forgotten while moving between phases. Tick when done.

**W2 tail (after ribbon, or interleaved):**
- [ ] **Zoom** controls (`setClientZoom`); currently fixed fit-width (~100%).
- [ ] **Cursor + selection overlays** — we receive `INVALIDATE_VISIBLE_CURSOR`
      (type 1) + `TEXT_SELECTION` (type 2) callbacks but don't draw the caret /
      selection yet. (Editor feel.)
- [ ] **Tile cache** — currently re-renders the whole doc per paint; fine for
      1–few pages, needs tiling for big docs.
- [ ] **Status bar wiring** — "Page 1 / 0 words" in Main.qml are hardcoded
      placeholders; wire to real page/word count (`getCommandValues`).

**W3 tail / polish (optional, after W4 starts paying off):**
- [ ] **Composite controls** — Font name + size combo boxes, Font/Highlight
      colour split-buttons with palettes, line-spacing/bullets dropdowns. W3
      renders these as plain buttons (dispatch-only); the dropdown/palette UI
      needs W4 (popups) to be useful.
- [ ] **Quick Access Toolbar** (Save/Undo/Redo in the title area) — Word has it;
      we put Undo/Redo in a Home group for now.
- [ ] **Keyboard accelerators / mnemonics** on the ribbon (Alt-key tips).

**Engine / config:**
- [ ] **Strip** Calc(`sc`)/Impress(`sd`)/Math(`starmath`) + peers (Writer-only).
- [ ] **Light color scheme** is currently seeded per-profile as a stopgap; fold
      into our own theming model (Boundary A) — we may later offer doc dark mode.
- [x] **`Properties` bitmask** — not needed for W3: ribbon toggle flags come
      from the curated spec in `build_ribbon.py`, not the raw bitmask.

**W4 tail (remaining dialog work):**
- [ ] **`enabled.cxx` patches (D6)** for WINDOW-only dialogs: InsertTable
      (priority), InsertBookmark, HyperlinkDialog, About. Register each in
      `vcl/jsdialog/enabled.cxx`, rebuild `vcl`, re-audit.
- [ ] **OS-native pickers as our own Qt dialogs**: InsertGraphic (Picture),
      File ▸ Open/Save — wire a native `FileDialog`, not a JSDialog.
- [ ] **Renderer polish**: grid alignment for value columns, formattedfield
      units (″/cm), combobox `change` for editable combos, treeview/listbox
      multi-column, color pickers; re-verify Spelling/Zoom in GUI.

**Phases:** W3 ribbon ✅ · W4 dialogs core ✅ (enabled.cxx tail) · W5 logger ·
W6 MCP · W7 Docker · W8 theming. (See the phase table + D-entries in DECISIONS.md.)

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
1. ✅ **DONE — LOK scheduler / live edit render (D9).** Solved via synchronous
   scheduler pump (`unit_lok_process_events_to_idle`) + self-driven repaint +
   light color scheme. Typed text renders live. See D9.
2. **Tiling + scroll + zoom** — currently the whole page is rendered into the
   item width (readable but small); want a tile cache + `Flickable` viewport +
   zoom (`setClientZoom`) so text is comfortably legible, + cursor/selection
   overlays from callbacks. (Next W2 task.)
3. **Logger raw-stream scaffold** (`src/logging/`) — grows into W5.

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
