# Writer — Architecture (foundational)

> The canonical design for the **modern native Writer app**. Read this
> first when working on `apps/writer/`. Decisions captured here are
> tracked with rationale in [`../DECISIONS.md`](../DECISIONS.md);
> the LOK capability map that grounds the feasibility is in
> [`LOK_REFERENCE.md`](LOK_REFERENCE.md); the logger contract is in
> [`LOGGING.md`](LOGGING.md).
>
> Last updated: 2026-05-25 (Phase W0 — foundations).

---

## 1. What we are building (one paragraph)

A **modern, native desktop word processor** that looks and behaves like
Microsoft Word, built as a CUA (Computer-Using-Agent) RL environment with
a future MCP control surface. We **own** the entire user-facing
application — UI, interaction, command/dispatch mechanism, document
session/state, logging, theming, and the MCP surface — written fresh in
**Qt 6 (C++ core + QML UI)**. We **drive LibreOffice's real engine
headlessly via LibreOfficeKit (LOK)** for the three things that are a
decades-deep quality moat and would be a trap to reimplement: **document
layout, text shaping, and .docx/.odt I/O fidelity**. This is the same
proven architecture Collabora Online and the LibreOffice mobile apps use
(native UI + LOK tiled rendering + UNO command dispatch), but with a
from-scratch modern shell that is fully ours.

This is **not** the previous approach (fork LibreOffice and reskin its own
notebookbar/VCL/GTK chrome). That approach fought LO-internal hardcoded
behaviour at every turn. Here the LO engine is a *dependency behind a
stable API boundary*; the app is ours.

---

## 2. The core principle — "Boundary A" (layered ownership)

The single most important decision (see [`../DECISIONS.md`](../DECISIONS.md) D1).
We draw the ownership line so that "our own modern mechanism", "highest
quality", and "every Writer feature actually works" are all satisfied at
once:

```
┌─────────────────────────────────────────────────────────────────┐
│  OURS — modern, native, fully owned (apps/writer/src/)            │
│                                                                   │
│   ui/        Word-like ribbon + panels + canvas (QML, Fluent)     │
│   dialogs/   JSDialog JSON → native Qt/QML dialogs                │
│   commands/  our command catalog + dispatch mechanism             │
│   document/  session + state model (cursor/selection/format)      │
│   logging/   raw / semantic / outcome  (figma-parity, contract)   │
│   mcp/       MCP control surface (future)                         │
│   engine/    thin C++ binding over the LOK C API                  │
└───────────────────────────────┬───────────────────────────────────┘
                                 │  LibreOfficeKit C API
                                 │  (load / paintTile / postUnoCommand /
                                 │   postKey|MouseEvent / getCommandValues /
                                 │   registerCallback / saveAs / JSDIALOG)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  ENGINE — LibreOffice, Writer-only stripped (separate dependency) │
│                                                                   │
│   layout engine  (sw/source/core/layout — line break, pagination) │
│   text shaping   (HarfBuzz, fonts, complex scripts)               │
│   painting       (renders the document to a bitmap tile)          │
│   .docx/.odt I/O (writerfilter / oox / ww8 / xmloff filters)      │
│   + the shared core they require (vcl, sfx2, svx, editeng, ...)   │
└─────────────────────────────────────────────────────────────────┘
```

**Why this line and not elsewhere** (full reasoning + rejected
alternatives in D1): a word processor is ~7 layers. The document model,
editing/command layer, dialogs, and UI (layers we put above the line)
*benefit* from a modern rewrite. The layout engine, text shaping, and
docx/odt filters (below the line) are ~15-20 years of LibreOffice work;
reimplementing them would make output *quality lower* for years and
contradicts "every feature works". So we own everything that shapes the
experience and the mechanism, and rent the proven document core.

**Honest constraint:** "Writer engine" is *not* a small library. It pulls
in a large shared core (vcl, sfx2, svx, editeng, framework, oox,
writerfilter, sax, i18n, the font/shaping stack). We can delete the *other
apps* (Calc/Impress/Math/peers) but not this shared foundation. See D5.

---

## 3. Components (what each piece does)

| Component | Path (planned) | Responsibility |
|---|---|---|
| **Engine binding** | `src/engine/` | Thin C++ wrapper over the LOK C API: an `Office` (process/init) and `Document` (load/save/render/input/query). Owns the LOK callback pump and translates LOK callbacks into Qt signals. |
| **Tile renderer** | `src/engine/` | Drives `paintTile`/`setClientZoom`; maintains a tile cache keyed by (zoom, x, y); repaints on `INVALIDATE_TILES`; blits into the QML canvas. Coordinate unit is **TWIP** (1/1440 inch) on the engine side; we map to device pixels. |
| **Command mechanism** | `src/commands/` | Our command catalog (generated from `WriterCommands.xcu` + `GenericCommands.xcu`), and the dispatch layer that turns a UI action into `postUnoCommand(".uno:X", argsJson)`. Subscribes to `STATE_CHANGED` + uses `getCommandValues` to drive button enabled/checked state. **This is the seam where semantic logging and MCP both hook in.** |
| **Document/state** | `src/document/` | The session-level state model: open doc URL, modified flag, cursor rect, selection rects, format-at-cursor, part/page info. Fed by LOK callbacks (`INVALIDATE_VISIBLE_CURSOR`, `TEXT_SELECTION`, `STATE_CHANGED`, `DOCUMENT_SIZE_CHANGED`). Source of the `outcome` log stream. |
| **Dialogs** | `src/dialogs/` | Consumes `LOK_CALLBACK_JSDIALOG` (a JSON widget tree), renders it as **native Qt/QML** widgets, and sends user actions back via `sendDialogEvent`. See §5. |
| **UI** | `src/ui/qml/` | The modern Word-like shell: ribbon (tabs/groups/controls), QAT, status bar, context menus, the document canvas. Declarative QML for fast iteration; Fluent UI System Icons. |
| **Logging** | `src/logging/` | raw / semantic / outcome streams, figma-parity, conformant to `overview/log-contract.md`. Cross-cutting. See [`LOGGING.md`](LOGGING.md). |
| **MCP** | `src/mcp/` | Exposes command dispatch + state queries + document ops as MCP tools. Future (W6); the dispatch seam is designed for it now. |

---

## 4. LOK integration specifics

The feasibility is confirmed in [`LOK_REFERENCE.md`](LOK_REFERENCE.md)
(every method/callback below was located in the vendored tree with
file:line). The integration loop:

1. **Init** — `lok::lok_cpp_init(instdir)` → `Office`. Set
   `setOptionalFeatures` for tiled rendering / no-tiled-annotations as
   needed. Register one callback.
2. **Load** — `documentLoadWithOptions(url, opts)` → `Document`. We run
   headless; there is no LO window — *we* are the window.
3. **Render** — on `INVALIDATE_TILES` (or initial paint), call
   `paintTile(buf, canvasW, canvasH, tileX, tileY, tileW, tileH)` for the
   visible/invalidated tiles; blit into the QML canvas. `setClientZoom`
   maps TWIP→pixel.
4. **Input** — keyboard → `postKeyEvent(KEYINPUT/KEYUP, charCode, keyCode)`;
   mouse → `postMouseEvent(type, x, y, count, buttons, modifier)` (coords
   in TWIP). Text selection drag → `setTextSelection`.
5. **Commands** — every ribbon/menu/shortcut action →
   `postUnoCommand(".uno:Bold", argsJson, /*notify*/true)`. Result arrives
   on `UNO_COMMAND_RESULT`; state changes stream on `STATE_CHANGED`.
6. **State/query** — `getCommandValues(".uno:...")` for pull queries;
   `getTextSelection(mime)` to extract selected text/html.
7. **Save** — `saveAs(url, "docx"/"odt"/"pdf", filterOpts)`.

**Threading:** LOK is single-threaded per document and expects to own an
event loop (`runLoop` with poll/wake callbacks). We integrate it with the
Qt event loop on a dedicated engine thread; callbacks marshal to the UI
thread as Qt signals. (Design detail to finalize in W2.)

---

## 5. Dialog strategy — the one real risk, and its mitigation

"Every Writer feature works in our own native UI" hinges on dialogs.
LibreOffice can serialize its native dialogs to a **JSON widget tree** via
`vcl/jsdialog/` (`jsdialogbuilder` → `jsdialogsender` →
`LOK_CALLBACK_JSDIALOG`); the client renders it natively and posts actions
back with `sendDialogEvent`. The `executor.cxx` widget vocabulary covers
the controls we need (button, checkbox, radio, combobox, listbox,
spinbutton, edit, treeview, tabcontrol, etc.).

**The risk (D6):** coverage is *selective*. Only dialogs registered in
`vcl/jsdialog/enabled.cxx` flow through this path; others still try to
create a native window (which fails/blocks headless). LO even ships
`completeWriterDialogList()` listing Writer dialogs "expected but not yet
seen" — i.e. a known gap list.

**Mitigation (chosen, professional, not a hack):**
- Treat dialog coverage as an explicit, audited deliverable in **W4**.
- Where a needed Writer dialog isn't JSON-enabled, extend the engine's
  `vcl/jsdialog/enabled.cxx` to register it. This is a small, well-scoped
  **engine-side patch** — the one sanctioned exception to "don't touch the
  engine" (D6). It is upstream-shaped (the same mechanism LO/Collabora use)
  and survives engine updates as a tracked patch.
- Each enabled dialog gets a coverage entry in the W4 audit doc.

---

## 6. Logging (cross-cutting, mandatory)

Detailed in [`LOGGING.md`](LOGGING.md). Key architectural point: because
of Boundary A we **own the dispatch seam**, so logging is *cleaner and more
complete* than the old engine-embedded `rllogger` ever was:

- `raw[]` ← our input layer (every key/mouse/focus before it reaches LOK)
- `semantic[]` ← our command dispatch (`.uno:*` name + args + `rawEventIdRange`)
- `outcome{}` ← our state model (from LOK callbacks + `getCommandValues`),
  rewritten on a fixed cadence; `summary.semanticEventCount` drives the
  verifier efficiency rubric.

Must conform to [`../../../overview/log-contract.md`](../../../overview/log-contract.md)
and reach **figma-parity** (the figma TS logger is the detail bar). The
engine's `rllogger` is **retired** for this app (D7).

---

## 7. MCP surface (future, designed-for now)

The command mechanism (§3) is the natural MCP seam: an MCP tool call maps
to a `.uno:*` dispatch (or a higher-level composite), and state queries map
to `getCommandValues`/the state model. We design the dispatch layer with a
clean programmatic API now so W6 is wiring, not redesign.

---

## 8. Directory structure (clean, modular — not LO-style)

```
apps/writer/
├── CLAUDE.md / AGENTS.md          entry points → docs/
├── README.md
├── CMakeLists.txt                 (W2) top-level build
├── docs/                          ALL project documentation (this folder)
│   ├── architecture/ARCHITECTURE.md   this file
│   ├── architecture/LOK_REFERENCE.md  LOK capability map (research)
│   ├── architecture/LOGGING.md        logger design + contract
│   ├── DECISIONS.md                   critical decision log
│   ├── last-point.md                  what's done now
│   ├── execution-map.md               phased roadmap / what's next
│   └── progress/                      per-session progress notes
├── src/
│   ├── engine/                    LOK binding, tile renderer, input
│   ├── commands/                  command catalog + dispatch
│   ├── document/                  session + state model
│   ├── dialogs/                   JSDialog → native Qt/QML
│   ├── ui/qml/                    ribbon, panels, canvas, context menus
│   ├── logging/                   raw/semantic/outcome
│   ├── mcp/                       MCP surface (later)
│   └── main.cpp
├── resources/
│   ├── icons/                     Microsoft Fluent UI System Icons (SVG)
│   ├── themes/                    Word-like dark/light palettes
│   └── qml/
└── tests/

ENGINE (separate dependency — D2/D4/D5; physical location TBD in W1):
   the Writer-only deep-stripped LibreOffice source that builds LOK.
   Currently lives at apps/libreoffice/libreoffice-codebase/ and will be
   reduced to Writer-only and clearly demarcated as "engine, not app".
```

---

## 9. Engine boundary & distribution

- **Dev time:** the engine source is present; we build LOK from it; the Qt
  app links against the built `instdir/` + LOK headers. We do **not** touch
  the engine day-to-day (sole sanctioned exception: `enabled.cxx` dialog
  registration, §5).
- **Distribution (W7, Docker, per D8):** multi-stage build — *build stage*
  compiles engine→LOK + our Qt app; *runtime stage* ships only binaries
  (`instdir/` + LOK + app + logger on by default). **Source never ships.**
  RL agents pull the image; they don't build.

---

## 10. Tech stack rationale (summary; full in DECISIONS)

- **Qt 6 (C++ + QML)** over Electron/Tauri (web) — owner requires a *real
  native* app, no web runtime. Over Flutter — Qt is the most battle-tested
  for a heavy native document app + C++ LOK interop, with QML giving modern,
  hot-reloadable, "easy to play with" UI. (D3)
- **Fluent UI System Icons** — MIT, ~2000 icons, exact Word M365 visual
  match. (D-icons)

---

## 11. Open questions (resolve as phases reach them)

- **Engine physical location & strip depth** (W1): in-repo `engine/` vs.
  keep at `apps/libreoffice/libreoffice-codebase/`; how aggressively to
  strip before LOK link breaks.
- **LOK build flags** for a minimal Writer-only headless LOK (which
  `--disable-*` are safe; `--enable-mergelibs`?).
- **Engine thread ↔ Qt loop** integration shape (W2).
- **Tile cache invalidation** strategy + zoom/HiDPI handling (W2).
- **Dialog coverage gap size** — quantify in W4 against
  `completeWriterDialogList()`.
- **MCP transport** (stdio sidecar vs in-process) (W6).
```
