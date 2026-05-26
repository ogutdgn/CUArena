# W4 — Dialog Coverage Audit

> Which Writer dialogs surface as a **JSDIALOG** JSON widget tree (renderable
> natively in our QML layer) vs a **WINDOW**-only tiled/native window (not
> registered in the engine's `vcl/jsdialog/enabled.cxx` → a D6 patch candidate)
> vs **NONE** (the command acts directly, opens an OS-native picker, or needs a
> selection/content that the headless probe didn't provide).
>
> Method: `tests/dialog_audit.cpp` — opens each command in a **fresh headless
> LOK process** (a modal WINDOW-only dialog like Insert Table ignores
> `.uno:Cancel` and blocks every later command, so isolation is required),
> registers the callback, and classifies the first dialog surface. Full widget
> trees captured by `tests/dialog_probe.cpp`. Generated 2026-05-26 against
> engine 26.8.0.0.alpha0.

---

## Result (ribbon dialog-target commands)

| Command | Surface | Notes |
|---|---|---|
| `.uno:SearchDialog` (Find & Replace) | **JSDIALOG** | ✅ render natively |
| `.uno:PageDialog` (Page Setup) | **JSDIALOG** | ✅ tabcontrol + many tabs |
| `.uno:FontDialog` | **JSDIALOG** | ✅ |
| `.uno:ParagraphDialog` | **JSDIALOG** | ✅ |
| `.uno:FormatColumns` | **JSDIALOG** | ✅ |
| `.uno:InsertBreak` | **JSDIALOG** | ✅ |
| `.uno:InsertSymbol` | **JSDIALOG** | ✅ |
| `.uno:WordCountDialog` | **JSDIALOG** | ✅ simplest — W4 first target |
| `.uno:InsertField` | **JSDIALOG** | ✅ |
| `.uno:InsertReferenceField` (Cross-ref) | **JSDIALOG** | ✅ |
| `.uno:InsertMultiIndex` (TOC) | **JSDIALOG** | ✅ |
| `.uno:InsertIndexesEntry` | **JSDIALOG** | ✅ |
| `.uno:InsertTable` | **WINDOW-only** | ⚠ D6: register in `enabled.cxx` |
| `.uno:InsertBookmark` | **WINDOW-only** | ⚠ D6 |
| `.uno:HyperlinkDialog` | **WINDOW-only** | ⚠ D6 (emits some JSDIALOG updates but the tree is a WINDOW) |
| `.uno:About` | **WINDOW-only** | ⚠ low priority; we may render our own About |
| `.uno:InsertGraphic` (Picture) | **NONE** | OS-native file picker → use **our own** Qt file dialog |
| `.uno:InsertObjectChart` / `.uno:InsertDraw` / `.uno:InsertTextFrame` / `.uno:InsertObjectStarMath` | **NONE** | insert object / enter edit mode directly (no modal dialog) |
| `.uno:InsertFootnote` / `.uno:InsertEndnote` | **NONE** | insert directly in default config (the *dialog* variant is `.uno:InsertFootnoteDialog`) |
| `.uno:InsertCaptionDialog` | **NONE** | needs a selected object; re-verify in GUI |
| `.uno:ThesaurusDialog` | **NONE** | needs a word + language resources; re-verify in GUI |
| `.uno:SpellingAndGrammarDialog` | **(hang)** | blocks headless (dictionary/locale) — re-verify in GUI |
| `.uno:Zoom` | **(timeout)** | re-verify in GUI; likely JSDIALOG |

---

## Takeaways for W4

1. **Most high-value formatting dialogs already flow through JSDIALOG** (Page,
   Font, Paragraph, Search, Columns, Break, Symbol, Word Count, indices). The
   native JSON→QML renderer unlocks them with **no engine patch**. Build the
   renderer against these first; **Word Count** is the simplest end-to-end
   target.
2. **WINDOW-only gap list (D6 `enabled.cxx` patches):** `InsertTable`,
   `InsertBookmark`, `HyperlinkDialog`, `About`. Each is the one sanctioned
   engine edit — register the dialog's `.ui`/SfxTabDialog in `enabled.cxx`,
   rebuild `vcl`, re-audit. Prioritise **Insert Table** (common).
3. **OS-native pickers** (`InsertGraphic`, Open/Save) are *ours* anyway — wire a
   native Qt `FileDialog`, not a JSDialog. Consistent with Boundary A.
4. **`NONE`/hang/timeout rows are headless artifacts** for several commands
   (need a selection, content, dictionaries, or a real event loop). Re-verify
   each in the live GUI before concluding it has no dialog.

## Confirmed round-trip protocol (`sendDialogEvent`)

Verified end-to-end by `tests/dialog_roundtrip.cpp` (open Page Style → cancel →
engine emits `action:"close"`):

- **windowId** = the dialog tree **root's `lokWindowId`** (not the string `id`,
  which can be a name like `"WordCountDialog"`; not the per-control ids). It is
  assigned per opened dialog (1, 2, … in a session).
- **event JSON** = `{"id":"<controlId>","type":"<widget>","cmd":"<action>","data":"<value>"}`
- **engine ack** = JSDIALOG `{"jsontype":"dialog","action":"close","id":<windowId>}`
  when a dialog closes (modal). Modeless dialogs (Word Count) may close silently
  — `DialogHost` dismisses optimistically on ok/cancel/close clicks.

Per-widget `type` / `cmd` / `data` (from `vcl/jsdialog/executor.cxx`):

| Widget | `type` | `cmd` | `data` |
|---|---|---|---|
| action button (OK/Cancel/Close/Apply) | `responsebutton` | `click` | — |
| push button | `pushbutton` | `click` | — |
| checkbox | `checkbox` | `change` | `"true"`/`"false"` |
| radio button | `radiobutton` | `change` | `"true"` |
| text edit | `edit` | `change` | the text |
| combobox/listbox | `combobox` | `selected` | `"<pos>;<text>"` (or `change` + text) |
| spin/formatted field | `spinfield` | `value` | the number |
| tab control | `tabcontrol` | `selecttab` | page index |

`DialogHost.qml` implements this; `DialogWidget.qml` emits per-widget events.

## Tooling

- `tests/dialog_probe.cpp` — dumps full JSDIALOG/WINDOW payloads (and writes
  each full widget tree to `/tmp/jsdlg_<Cmd>.json`) for schema design.
- `tests/dialog_audit.cpp` — per-command surface classifier (this table).
- `tests/dialog_roundtrip.cpp` — JSDIALOG → `sendDialogEvent` round-trip proof.

> ⚠ Run all probes with an **absolute** `instdir/program` path
> (`$(cd ../libreoffice/libreoffice-codebase && pwd)/instdir/program`) — a
> relative path triggers a `theDefaultProvider` UNO bootstrap crash.
