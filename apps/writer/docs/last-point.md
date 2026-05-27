# Writer — Last Point

> **Current state of `apps/writer/`** — what actually exists, nothing
> aspirational. Pairs with [`execution-map.md`](execution-map.md) (what's
> next). Refresh at session end.
>
> Last updated: 2026-05-26.

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

**Phase W3 — Command mechanism + ribbon UI (DONE):**

- **Data-driven ribbon** (DECISIONS D10) — `tools/build_ribbon.py` emits
  `resources/ribbon.json` (8 tabs / 29 groups / **83 commands**), every `.uno:`
  validated against the command catalog, labels auto-pulled. UI is generic QML
  (`Ribbon`/`RibbonGroup`/`RibbonButton`) — adding commands never touches QML.
- **80 Fluent icons** — `tools/fetch_icons.py` pulls them from pinned
  `@fluentui/svg-icons@1.1.328`, recolours to the ribbon tint, bundles into the
  binary via qrc. All 8 tabs render with Word-faithful icons + group labels.
- **Live toggle state** — `STATE_CHANGED` → `unoState` → buttons light up
  (verified: `.uno:Bold` lights blue after dispatch; "Show Changes" reflects
  the engine default). `disabled` state greys buttons.
- **Verified headless** (offscreen screenshots, all 8 tabs): ribbon renders,
  Bold toggle round-trips, dispatch wired through `lokEngine.postUno(cmd,args)`.
  Build clean; `writer_render_test` regression still green.
- **Deferred (correctly):** semantic-event emit on dispatch → W5 (logger);
  dialog targets (Find&Replace, Insert Table, Page Setup…) dispatch but their
  JSDialogs are wired in W4; composite controls (font combo, colour palettes,
  dropdowns) need W4 popups (see execution-map W3 tail).

**Phase W4 — Dialogs (core DONE):**

- **Generic JSDialog→QML renderer** (DECISIONS D11): `DialogWidget.qml`
  (recursive, Loader-by-URL) + `DialogHost.qml` (in-app modal overlay) render
  any LOK `LOK_CALLBACK_JSDIALOG` widget tree natively — one renderer, not
  per-dialog QML. Verified headless: **Word Count** (grid) and **Page Style**
  (10-tab tabcontrol with labels) render cleanly with real data.
- **Round-trip proven** (`tests/dialog_roundtrip.cpp`): open Page Style →
  `sendDialogEvent(windowId=lokWindowId, {"id":"cancel","type":"responsebutton",
  "cmd":"click"})` → engine acks `action:"close"`. `LokEngine` captures
  JSDIALOG/WINDOW callbacks + exposes `sendDialogEvent`.
- **Coverage audit** ([`architecture/W4_DIALOG_COVERAGE.md`](architecture/W4_DIALOG_COVERAGE.md)):
  most formatting dialogs are JSDIALOG (native-renderable, no engine patch);
  InsertTable/Bookmark/Hyperlink/About are WINDOW-only (D6 `enabled.cxx`
  candidates); pickers (InsertGraphic) are OS-native → our own Qt dialog.
  Probes: `tests/dialog_{probe,audit,roundtrip}.cpp`.
- **Engine gotcha found+documented**: `lok_cpp_init` needs an absolute
  `instdir/program` path (ENGINE_BUILD.md) — relative crashes UNO bootstrap.
- **`enabled.cxx` patch landed (D6)**: added `inserttable.ui` +
  `insertbookmark.ui` to `SwriterDialogList`, rebuilt `vcl` → both now render
  natively (Insert Table verified: Columns/Rows/Header spinners correct).
- **Remaining (W4 tail):** enable Hyperlink/About dialogs; OS-picker Qt dialogs;
  renderer polish (formattedfield units, color pickers, multi-col lists).

**Phase W5 — Logger figma-parity (DONE; verifier deferred):**

- **`SessionLogger`** (`src/logging/`) emits the three contract streams as JSONL
  under `~/.writer-rl-logs/<sessionId>/` (env `WRITER_LOG_DIR`/`WRITER_LOG_DISABLE`):
  - **raw[]** — input from `LokEngine` (`postKey`/`typeText`/`postMouse`); base
    fields (eventId/type/timestamp/sessionTime/targetId/modifiers/fields).
  - **semantic[]** — every `postUno` dispatch, mapped to an RL name via
    `resources/uno-names.json` (1520 cmds, `tools/gen_uno_names.py`), with
    `rawEventIdRange` back-link + `args`.
  - **outcome{}** — 1 s cadence: `summary.semanticEventCount` (+ wordCount/
    charCount/page from `StateWordCount`/`StatePageNumber`), `document`
    {modified, pageStyle, formatAtCursor (curated), cursor, size}.
- **Consolidator** `tools/consolidate_log.py` → figma-shaped `session.json`
  ({schemaVersion, sessionId, exportedAt, raw[], semantic[], outcome{}}).
- Verified headless (demo text + `.uno:Bold,.uno:CenterPara`): streams + ranges
  + aggregates correct; `WRITER_LOG_DISABLE` opt-out works; render_test green.
- **Deferred:** a Writer *verifier* (reads these logs) — a later phase; the log
  shape is contract-conformant. Parity checklist in LOGGING.md §4.

**Ribbon expansion + composite controls (W3 tail — DONE):** addressed the
"cramped / missing buttons" feedback by sourcing coverage from LO's own ribbon:
- `build_ribbon.py` v2 draws command coverage from LO `notebookbar.ui` (parsed
  tab→commands) → **9 tabs, 40 groups, 147 items** (was 78); auto-assigns Fluent
  icons via a semantic-name matcher (`tools/fluent-icon-names.txt`) + curated
  overrides; 0 fallback icons.
- **Composite controls**: Font name + size editable combos (`RibbonCombo.qml`,
  live from STATE_CHANGED CharFontName/FontHeight) + Font Color / Highlight
  buttons with colour swatches. Verified: combos show "Liberation Serif" / "12".

**Editor feel (W2 tail — DONE):** the base-editing gaps that made the app feel
skeletal are fixed:
- **Caret** renders + blinks (`DocumentCanvas` overlay from
  `INVALIDATE_VISIBLE_CURSOR`/`CURSOR_VISIBLE`).
- **Text selection** renders (translucent highlight from `TEXT_SELECTION`);
  **drag-select** wired (`mouseMove`→MOUSEMOVE) + double-click word select.
- **Live status bar** — page + word/char count from STATE_CHANGED (incl.
  "Selected: N words" when a selection exists).
Verified headless (select-all highlight + live counts + caret).

## D9 — RESOLVED (live edit render works)

Typed/edited text now renders live in the GUI (verified: black text on the
white page via headless screenshot). `runLoop` was a dead end (returns
immediately); the fix needs no runLoop/threads — a **synchronous scheduler
pump**: dlsym the engine's exported `unit_lok_process_events_to_idle`
(= `Scheduler::ProcessEventsToIdle`) and call it after each dispatch; drive the
canvas repaint ourselves (this headless tiled setup doesn't emit
`INVALIDATE_TILES`); seed the LOK profile with `COLOR_SCHEME_LIBREOFFICE_LIGHT`
for black-on-white; `QSG_RENDER_LOOP=basic`. No engine-source changes. Full
write-up in [`DECISIONS.md`](DECISIONS.md) D9. Commit `7177b9f29`.

## Environment notes (for next session)

- Build toolchain installed (owner): `libtool`/`ccache` + Qt6
  (`qt6-base-dev`/`qt6-declarative-dev`/`cmake`/`ninja`, Qt **6.4.2**).
- LOK usage: compile `-I <engine>/include ... -ldl`; `#define LOK_USE_UNSTABLE_API`;
  run with `SAL_USE_VCLPLUGIN=svp LO_RL_LOG_DISABLE=1`; `saveAs` format = extension.
- Strip (Calc/Impress/Math) NOT yet done — deferred optimization.

## Current branch

`improve-lo-test` — local commits only (not pushed this session, per owner).
W0/W1 done; W2 substantially done (live edit render D9-resolved + scrollable
page); **W3 DONE — full data-driven Word ribbon** (8 tabs, 83 commands, 80
Fluent icons, live toggle state; D10). Next: **W4 dialogs/D6** (JSDialog →
native Qt, wire dialog targets), then W2 tail (zoom/cursor overlays), W5 logger.
See [`execution-map.md`](execution-map.md).
```
