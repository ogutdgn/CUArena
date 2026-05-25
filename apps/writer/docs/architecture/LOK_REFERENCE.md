# LOK Capability Map (research reference)

> Result of the Phase W0 deep-dive into the vendored LibreOffice tree, to
> ground the [`ARCHITECTURE.md`](ARCHITECTURE.md) feasibility. **Don't
> re-research this** — extend it. All paths are relative to the engine tree
> `apps/libreoffice/libreoffice-codebase/` unless noted.
>
> Last updated: 2026-05-25 (W0). Verdict: **architecture is feasible**; the
> only real risk is selective JSDialog coverage (see §3).

---

## 1. LOK C++ API — complete & stable

Headers:
- `include/LibreOfficeKit/LibreOfficeKit.h` — C API structs
- `include/LibreOfficeKit/LibreOfficeKit.hxx` — C++ wrappers (`lok::` namespace)

Key **Document** methods (file:LibreOfficeKit.h line — purpose):

| Capability | Line | Signature |
|---|---|---|
| Load | 58-66 | `documentLoad(url)`, `documentLoadWithOptions(url, opts)` |
| Save | 201-204 | `saveAs(url, format, filterOptions)` → e.g. `"docx"`, `"odt"`, `"pdf"` |
| Doc type | 209 | `getDocumentType()` → `LOK_DOCTYPE_TEXT` for Writer |
| **Paint tile** | 234-241 | `paintTile(buf, canvasW, canvasH, tileX, tileY, tileW, tileH)` → RGBA/BGRA |
| Doc size | 247-249 | `getDocumentSize(&w, &h)` (TWIPs) |
| Init render | 252-253 | `initializeForRendering(args)` (before first paint) |
| **postKeyEvent** | 261-264 | `postKeyEvent(type, charCode, keyCode)` — `LOK_KEYEVENT_KEYINPUT/KEYUP` |
| **postMouseEvent** | 267-273 | `postMouseEvent(type, x, y, count, buttons, modifier)` |
| **postUnoCommand** | 276-279 | `postUnoCommand(cmd, argsJson, bNotifyWhenFinished)` |
| setTextSelection | 282-285 | `setTextSelection(type, x, y)` |
| getTextSelection | 288-290 | `getTextSelection(mimeType, &usedMime)` (text/plain, text/html) |
| setGraphicSelection | 298-302 | shape/image select |
| resetSelection | 304-305 | clear selection |
| **getCommandValues** | 307-308 | `getCommandValues(cmd)` → JSON state |
| setClientZoom | 311-315 | `setClientZoom(tilePxW, tilePxH, twipW, twipH)` |
| setClientVisibleArea | 318 | viewport hint (TWIPs) |
| Views | 321-329, 356-358 | `createView/destroyView/setView/getView/getViewsCount/getViewIds` |
| renderFont | 332-336 | glyph bitmap |
| paintPartTile | 344-353 | (Calc/Impress — N/A for Writer) |
| **paintWindow** | 365-368 | `paintWindow(windowId, buf, x, y, w, h)` — dialog window render |
| postWindow | 371 | `postWindow(windowId, action, data)` — CLOSE/PASTE |
| postWindowKey/MouseEvent | 374-388 | dialog-window input |
| **sendDialogEvent** | 480-482 | `sendDialogEvent(windowId, argsJson)` — dialog action back to engine |
| setBlockedCommandList | 516-518 | disable `.uno:` commands by CSV (useful for the RL env) |

Key **Office** methods: `documentLoad` (58), `registerCallback` (85-87),
`setOptionalFeatures` (97), `setDocumentPassword` (102-104), `runLoop`
(127-130, poll/wake event loop), `sendDialogEvent` (133-135).

---

## 2. Callbacks — `include/LibreOfficeKit/LibreOfficeKitEnums.h`

72 `LOK_CALLBACK_*` values. Writer-essential ones:

| Callback | Line | Payload |
|---|---|---|
| `INVALIDATE_TILES` | 130 | `"x, y, w, h"` (TWIPs) or `"EMPTY"` → repaint |
| `INVALIDATE_VISIBLE_CURSOR` | 141 | JSON `{viewId, rectangle, misspelledWord}` |
| `TEXT_SELECTION` | 150 | `"rect; rect; ..."` selection rects |
| `TEXT_SELECTION_START/END` | 160/170 | handle positions |
| `CURSOR_VISIBLE` | 179 | `"true"/"false"` (blink) |
| `GRAPHIC_SELECTION` | 216 | `"x,y,w,h,angle,{props}"` |
| `STATE_CHANGED` | 229 | `".uno:Bold=true"` — drives ribbon button state |
| `DOCUMENT_SIZE_CHANGED` | 275 | `"w, h"` (TWIPs) |
| `CONTEXT_MENU` | 400 | JSON menu tree (text/type/command/enabled) |
| `UNO_COMMAND_RESULT` | 323 | JSON `{commandName, success}` (when notify=true) |
| `ERROR` | 378 | JSON `{classification, kind, code, message}` |
| `JSDIALOG` | 716 | full JSON dialog widget tree (see §3) |
| `DOCUMENT_PASSWORD` / `_TO_MODIFY` | 265 | password prompt |

Multi-view (collaborative, optional): `INVALIDATE_VIEW_CURSOR` (416),
`TEXT_VIEW_SELECTION` (425), `VIEW_CURSOR_VISIBLE` (478).
Calc/Impress-specific (N/A now): `CELL_CURSOR` (335), `CELL_FORMULA` (17),
`SET_PART` (282).

---

## 3. JSDialog — dialog-as-JSON (the critical, *partial* mechanism)

Files (`vcl/jsdialog/`):
- `jsdialogbuilder.cxx` — weld widgets → JSON; `JSInstanceBuilder`
- `jsdialogsender.cxx` — serialization + callback delivery
  - `generateFullUpdate()` (~83-96): `DumpAsPropertyTree(jsonWriter)` →
    `{jsontype, id, control:{...}}`; delivered via
    `libreOfficeKitViewCallback(LOK_CALLBACK_JSDIALOG, msg)` (~43)
- `executor.cxx` — routes client actions back: `ExecuteAction(windowId,
  widgetId, data)` → native weld callback
- `vcl/inc/jsdialog/enabled.hxx` — `isBuilderEnabled(uiFile, bMobile)`,
  `isBuilderEnabledForPopup/Sidebar/Menu`, **`completeWriterDialogList()`**
  (the "expected but not yet enabled" Writer dialog list)

Client→engine action: `sendDialogEvent(windowId, '{"id":"ok","cmd":"click"}')`.

Widget vocabulary (executor.cxx): pushbutton, checkbox, radiobutton,
combobox, listbox, spinbutton, formattedfield, edit, multiline, treeview,
iconview, tabcontrol, fixedtext, image, progressbar, drawingarea, expander,
separator, scrollbar, timefield, datefield.

**Coverage is SELECTIVE.** Only dialogs registered in `enabled.cxx` flow
through JSON. Mitigation: extend `enabled.cxx` per missing Writer dialog
(see ARCHITECTURE §5, DECISIONS D6). This is the one sanctioned engine patch.

---

## 4. Command catalog (our UI's command surface)

- `officecfg/registry/data/org/openoffice/Office/UI/WriterCommands.xcu`
  — **552** `.uno:` entries (`<node oor:name=".uno:`), 4489 lines
- `.../GenericCommands.xcu` — **993** `.uno:` entries (shared)

Entry shape: `Label`, `ContextLabel` (with `~` mnemonic), `TooltipLabel`,
`Properties` (int bitmask: 1=toggleable, 8=hidden, etc.), optional `Popup`.
We generate our catalog from these (W3).

---

## 5. Reference consumer code (copy patterns from here)

`libreofficekit/qa/gtktiledviewer/` (~4800 SLOC, GTK, C):
- `gtv-signal-handlers.cxx` — LOK callback dispatch; `.uno:` posting;
  `getCommandValues` (lines 143, 317, 457, 566)
- `gtv-lokdocview-signal-handlers.cxx` — cursor/selection handling
- `gtv-lok-dialog.cxx` — **dialog JSON deserialization & rendering** (the
  pattern our `src/dialogs/` mirrors, but in Qt/QML)
- `gtv-main-toolbar.cxx` — toolbar state from `STATE_CHANGED`

Tests: `libreofficekit/qa/unit/tiledrendering.cxx` (key posting loop ~62-65,
`paintTile` ~361-370, key events ~420-425); `libreofficekit/qa/tilebench/`.

No Qt-based LOK consumer exists in-tree — the C API is UI-agnostic; we wrap
it ourselves.

---

## 6. Qt backend & misc

- `vcl/qt6/`, `vcl/qt5/`, `vcl/unx/kf6/`, `kf5/` all present (Qt6 build deps
  available; LOK itself is headless so this is for build-dep awareness).
- `rllogger/` hooks at the UNO dispatcher level (no direct `LOK_CALLBACK`
  use) — consistent with retiring it and logging in our own layer.
```
