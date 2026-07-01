# Table — Insert > Tables

The Insert > Tables group is a single split button labelled **Table**. Its dropdown
has the live grid picker at the top and five command items below it: **Insert Table…**,
**Draw Table**, **Convert Text to Table…**, **Excel Spreadsheet**, and **Quick Tables**.
This file gives a feasibility verdict for each of the six flows, because they share one
engine seam — the fork's `w:tbl` node + the `WC.PM` table bridge — but diverge sharply
in fidelity (one flow, Excel Spreadsheet, needs a subsystem the fork does not have).

Shared facts grounded in the fork:
- **Node:** `extensions/table/table.js` (+ `table-row`, `table-cell`) is a real ProseMirror
  table node. `insertTable` (`table.js:851`) and `convertTextToTable` (`table.js:2061`) are
  genuine fork commands.
- **Converter:** `core/super-converter/v3/handlers/w/tbl/tbl-translator.js` is a full
  `w:tbl` import/export translator (composes `tblPr`, `tblGrid`, `tr` → `tc`; merges via
  `gridSpan`/`vMerge`; borders, shading, `tblStyle`). Every table here round-trips real OOXML.
- **Bridge:** `bridge/table.ts` — `insertTable` (`:34`), `textToTable` (`:233`),
  `tableAutoFit` fixed/contents/window (`:302`), `tableSetStyle`/`getTableStyles`
  (`:140`/`:371`), plus the full Design/Layout verb set.

---

## Flow 1 — Grid picker

### What real Word does
Top of the dropdown is a live 10×8 selection grid ("Insert Table"). Hover highlights an
M×N block, the caption reads "4×3 Table", and the document shows a live preview. Click
commits an evenly-distributed table at the default **Table Grid** style (`w:tblStyle val="TableGrid"`)
with a `w:tblLook`. OOXML: `w:tbl > w:tblPr (w:tblStyle, w:tblW, w:tblBorders, w:tblLook),
w:tblGrid > w:gridCol×N, w:tr×M > w:tc > w:tcPr + w:p`. Access key Alt, N, T.

### Current clone state
**working** — `insert-features.js:77` `Insert.tableMenu` paints an 8×10 grid; cell click →
`Insert.buildTable` (`insert-features.js:40`) → `WC.PM.insertTable({rows,cols})` (`bridge/table.ts:34`),
a real `editor.chain().insertTable().run()`. Serializes through `tbl-translator.js`.

### Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** The `insertTable` fork command and the `w:tbl` translator both exist and are wired.
Only cosmetic gaps: the grid is 8 rows × 10 cols vs Word's 10×8 orientation, and the inserted
table does not stamp the explicit `TableGrid` style id by default (it relies on default borders).

### Required structures to build it
- **PM node/extension:** reuse `table` / `table-row` / `table-cell`
- **Converter handler:** exists at `v3/handlers/w/tbl/tbl-translator.js`
- **OOXML target:** `w:tbl` (+ `w:tblGrid`/`w:tr`/`w:tc`)
- **Bridge verb(s):** `WC.PM.insertTable` (exists)
- **Fork edit?** none
- **Rough size:** S (only the row/col orientation + optional default `TableGrid` style stamp) • **Dependencies:** none

---

## Flow 2 — Insert Table… dialog

### What real Word does
Opens the **Insert Table** dialog for precise/large tables beyond the 10×8 grid:
columns (default 5) + rows (default 2) spinners; an **AutoFit behavior** radio group
(Fixed column width [Auto or a measurement] / AutoFit to contents / AutoFit to window);
and a "Remember dimensions for new tables" checkbox. AutoFit maps to `w:tblW` type +
`w:tblLayout w:type="autofit"|"fixed"`. Access key Alt, N, T, I.

### Current clone state
**working** — `dialogs.js:11` `D.insertTable`: a grid plus numeric Columns/Rows inputs
(validated 1–1000) → `WC.PM.insertTable({rows,cols})`. Geometry only; the AutoFit radios
and "Remember dimensions" checkbox are absent.

### Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK
**Why:** Geometry already works. The missing AutoFit behavior is also already in the engine —
`bridge/table.ts:302` `tableAutoFit('fixed'|'contents'|'window')` calls the real fork
`autoFitTable` command and writes `w:tblLayout`/`w:tblW`. Completing the dialog is pure UI:
add the three radios + a measurement field and call `insertTable` then `tableAutoFit` (and
persist "Remember dimensions" in renderer state). No new node or converter handler.

### Required structures to build it
- **PM node/extension:** reuse `table`
- **Converter handler:** exists — `tbl-translator.js` (+ `tblPr` for `tblLayout`/`tblW`)
- **OOXML target:** `w:tbl`, `w:tblLayout w:type`, `w:tblW w:type`
- **Bridge verb(s):** `WC.PM.insertTable` + `WC.PM.tableAutoFit` (both exist)
- **Fork edit?** none
- **Rough size:** S • **Dependencies:** rides the existing `tableAutoFit` verb

---

## Flow 3 — Draw Table

### What real Word does
Pointer becomes a pen; the user drags the outer boundary, then draws internal
row/column/cell dividers freehand (cells need not be uniform). Raises the table
contextual tabs + the Border Style/Weight/Pen Color pens; the Eraser removes
borders / merges cells. Produces a normal `w:tbl` with whatever spans/merges were drawn
(horizontal → `w:gridSpan`, vertical → `w:vMerge`). Access key Alt, N, T, D.

### Current clone state
**shallow** — `insert-features.js:94` `Insert.drawTableMode`: a real crosshair rubber-band
drag; on mouseup it derives `cols=round(w/90)`, `rows=round(h/36)` and calls
`Insert.buildTable` → a real **uniform** table. It cannot draw individual dividers or
irregular cells. (Distinct from the Home/Borders "Draw Table" at `commands.js:2237`, which is
`WC.notImplemented` — do not conflate.)

### Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK (for a meaningful but not pixel-perfect pen)
**Why:** The `w:tbl` translator already round-trips arbitrary `gridSpan`/`vMerge` merges, and
`bridge/table.ts` already exposes `tableMerge`/`tableSplitCell`/cell-border verbs. A true
freehand pen (hit-test each drawn segment against painted cell edges, then merge/split/add
borders accordingly) is buildable on those verbs without touching the fork — it is a renderer
interaction layer, not an engine gap. It is moderate work because draw-mode geometry (snap to
the painted PE grid, eraser, live pen overlay) is non-trivial. If the user is happy with the
current "drag a rectangle → uniform grid" behaviour, this is already working at a basic level.

### Required structures to build it
- **PM node/extension:** reuse `table` + existing merge/split commands
- **Converter handler:** exists — `tbl-translator.js` (`gridSpan`/`vMerge` round-trip)
- **OOXML target:** `w:tbl`, `w:gridSpan`, `w:vMerge`, `w:tcBorders`
- **Bridge verb(s):** reuse `insertTable` + `tableMerge` + `tableSplitCell` + cell-border verbs; possibly add a `drawTableSegment`/eraser helper
- **Fork edit?** none
- **Rough size:** L (true pen + eraser + PE grid hit-testing) / S (keep current uniform behaviour) • **Dependencies:** rides the existing merge/split/border verbs and the paged PE coordinate seam

---

## Flow 4 — Convert Text to Table…

### What real Word does
Enabled when text is selected. Opens the **Convert Text to Table** dialog: column count
(pre-filled from the detected delimiter), row count (derived), AutoFit radios, and a
**Separate text at** group (Paragraphs / Tabs / Commas / Other [char box]). Splits the
selected paragraphs into rows and delimited fields into columns → a `w:tbl`
(one `w:tr` per source paragraph, one `w:tc` per field). Access key Alt, N, T, V.

### Current clone state
**working** — Despite the grounding's `state: "stub"` (from an earlier snapshot),
the current `insert-features.js:48` `Insert.convertTextToTable` is **fully wired**: with no
argument it opens a real "Convert Text to Table" dialog with the four "Separate text at"
radios (Paragraphs/Tabs/Commas/Other), auto-selecting Tabs→Commas→Paragraphs the way Word
does; OK → `WC.PM.textToTable(delim)` (`bridge/table.ts:233`) → the real fork
`convertTextToTable` command (`table.js:2061`), which builds a genuine `w:tbl`.

### Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** The fork command `convertTextToTable` (`table.js:2061`) splits each selected
paragraph on the delimiter, computes column widths, builds real `tableRow`/`tableCell` nodes,
and replaces the range; it exports through `tbl-translator.js`. The bridge verb and the dialog
are both present. Remaining polish vs Word: no AutoFit radios in this dialog and the column
count is implicit (max-cols across rows) rather than shown/editable.

### Required structures to build it
- **PM node/extension:** reuse `table` (via `convertTextToTable` command)
- **Converter handler:** exists — `tbl-translator.js`
- **OOXML target:** `w:tbl` / `w:tr` / `w:tc`
- **Bridge verb(s):** `WC.PM.textToTable` (exists, wired)
- **Fork edit?** none
- **Rough size:** S (only the AutoFit radios + explicit column field for full parity) • **Dependencies:** none

---

## Flow 5 — Excel Spreadsheet

### What real Word does
Inserts a **live embedded Excel worksheet as an OLE object**. Word enters in-place
activation (Excel's grid/ribbon hosted inside Word); clicking out deactivates to a static
EMF/PNG preview; double-click re-activates. This is **not** a `w:tbl` — it is
`w:p > w:r > w:object > o:OLEObject` (ProgID `Excel.Sheet.12`, `Type="Embed"`,
`r:id` → `/word/embeddings/oleObjectN.xlsx`) plus a `v:shape`/`w:drawing` preview image; the
embedding part is a full `.xlsx` package in `word/embeddings/`. No Word-side contextual tab.

### Current clone state
**stub** — `insert-features.js:113` `Insert.insertExcelSheet` = `WC.toast('Embedding an Excel
spreadsheet needs a host runtime — not available on the new engine yet.')`. No mutation, no
bridge call. An honest degrade.

### Can we build it in our engine?
**Verdict:** ⛔ Needs an external runtime we don't have (faithful) / 🔴 Needs a new subsystem (approximation)
**Why:** A **faithful** Excel Spreadsheet means a live OLE in-place activation host — a real
Excel runtime — which Electron does not have. More fundamentally, the fork has **no OLE
handler at all**: a repo-wide search for `o:OLEObject` / `w:object` / `Excel.Sheet` /
`progId` returns **zero** matches anywhere under `superdoc-fork/` (no node, no
`v3/handlers/.../object` translator, no `word/embeddings` writer). So even a *static* embed
(store an `.xlsx` part + paint its EMF/PNG preview, no live editing) is a NEW subsystem:
a new `object`/`oleObject` node, a new `w:object`/`o:OLEObject` import+export handler,
embeddings-part plumbing, and a preview-image pipeline. The pragmatic alternative is to drop
the live-OLE pretense and offer "insert a plain table" (reuse `insertTable`) or keep the
honest stub.

### Required structures to build it
- **PM node/extension:** add a new `oleObject` (embedded-object) node under `extensions/` — none exists
- **Converter handler:** add an import/export handler for `w:object` / `o:OLEObject` under `v3/handlers/w/object/` — **none exists** (must also write the `word/embeddings/*.xlsx` part + its relationship)
- **OOXML target:** `w:object` > `o:OLEObject` (ProgID `Excel.Sheet.12`) + preview `w:drawing`/`v:shape`
- **Bridge verb(s):** add `WC.PM.insertOleObject` / `insertEmbeddedSheet`
- **Fork edit?** additive (a whole new node + handler subsystem) — large surface
- **Rough size:** XL (faithful, with a runtime) / L (static-only approximation) • **Dependencies:** an EMF/PNG preview-render pipeline; an out-of-process spreadsheet engine for live editing (not present)

**➡️ DECISION (locked, this session): REMOVE the Excel Spreadsheet item from the Table dropdown.** Electron has no OLE/Excel runtime and the fork has zero OLE support; a static-OLE subsystem isn't worth it. Drop the menu item entirely (don't keep a stub). Implementation later = remove the flyItem in `insert-features.js` Table menu + drop it from the ribbon-data generator.

---

## Flow 6 — Quick Tables

### What real Word does
A submenu of pre-built **building-block** tables stored in `Building Blocks.dotx`
(gallery "Tables", category "Built-In"): Calendar 1–4, Double Table, Matrix, Tabular List,
With Subheads 1–2, plus "Save Selection to Quick Tables Gallery…" (Create New Building Block
dialog). Each built-in is a fully formatted+populated `w:tbl` (often a table style + sample
content); the gallery entries live as `w:docPart` (`docPartBody`) entries in the glossary
document. Access key Alt, N, T, T.

### Current clone state
**shallow** — `insert-features.js:118` `Insert.quickTablesMenu`: 4 entries
(Calendar 6×7 / Tabular List 4×2 / Matrix 4×4 / Double Table 5×3) each → `Insert.buildTable`
→ a real but **empty, unstyled, plain** grid of the right dimensions. No styling, no sample
content, no "Save Selection to Gallery".

### Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK
**Why:** Quick Tables are just pre-formatted `w:tbl` content, and the engine already inserts
real tables (`insertTable`), applies table styles (`bridge/table.ts:140` `tableSetStyle` +
`resolveTableStyleVisuals.js`), and round-trips them via `tbl-translator.js`. We can ship
faithful-looking templates by inserting a table then populating cells (via the normal text
verbs) and stamping a `tblStyle`/shading — no fork edit. We do **not** need Word's
building-block/glossary subsystem to *insert* a template; that subsystem (`docPart` / the
`document-part-object.js` extension exists for sdt docPartObj, but there is no
`Building Blocks.dotx` store) would only be needed for "Save Selection to Quick Tables
Gallery" persistence, which can stay deferred. Honest scope: build the gallery as a set of
hard-coded styled+populated templates.

### Required structures to build it
- **PM node/extension:** reuse `table` (+ existing style application)
- **Converter handler:** exists — `tbl-translator.js` (+ `tblStylePr` for styled bands)
- **OOXML target:** `w:tbl` with `w:tblStyle` + sample `w:p` content
- **Bridge verb(s):** reuse `insertTable` + `tableSetStyle` + text-insert verbs; a small `insertQuickTable(templateId)` helper
- **Fork edit?** none
- **Rough size:** M (author the styled/populated templates) • **Dependencies:** rides `insertTable` + `tableSetStyle`; "Save to Gallery" persistence (building-block store) is a separate, deferrable L

---

## Open questions for our discussion
- **Excel Spreadsheet:** keep the honest stub, build a *static* OLE-embed subsystem (L — new node + `w:object` handler + embeddings part, no live editing), or remove the item from the ribbon? A *live* Excel is ⛔ (no runtime); is a non-editable embedded preview acceptable, or is that worse than a plain table?
- **Quick Tables fidelity:** are hard-coded styled+populated templates (calendar with day headers, etc.) enough, or do we want true `Building Blocks.dotx`/glossary round-trip and "Save Selection to Gallery"? The latter is a separate building-block subsystem.
- **Draw Table:** ship a true freehand pen + eraser (L, PE grid hit-testing), or keep the current "drag a rectangle → uniform grid" and just relabel it honestly?
- **Insert Table dialog AutoFit:** worth wiring the AutoFit radios now (the `tableAutoFit` verb already exists, so it is cheap S), or defer?

## Decisions (locked as we go)
- **Grid picker** — ✅ DONE (works). Optional later: 10×8 orientation + stamp the default `TableGrid` style.
- **Insert Table… dialog** — TBD (add the AutoFit radios; the `tableAutoFit` verb already exists → S).
- **Draw Table** — TBD → **target = real drag-to-define-table**: drag the outer boundary on the page, then pen internal row/column dividers; Eraser removes a divider. Our current clone only drags a rectangle → uniform grid. (Pen + Eraser detail lives in `table-layout-tab.md` ▸ Draw.)
- **Convert Text to Table** — ✅ DONE (works; optional AutoFit radios later).
- **Excel Spreadsheet** — ❌ **REMOVE from the dropdown** (user call). See the inline DECISION in Flow 5.
- **Quick Tables** — TBD (ship styled + populated templates → M).
- **On-canvas table handles** (top-left move + bottom-right proportional resize) — TBD; analyzed in `table-layout-tab.md`. The clone has neither today.
