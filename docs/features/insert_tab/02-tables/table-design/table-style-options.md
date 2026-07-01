# Table Style Options — Table Design ▸ Table Style Options

> **One coupled feature surface, not 6 independent buttons:** Header Row · Total Row · Banded Rows · First Column · Last Column · Banded Columns. They all write one `w:tblLook` bitmask and behave as a unit, so this file covers all six.

## What it does (full spec)
Six checkboxes that toggle which **conditional** parts of the *applied table style* are active — they decide which style-defined formatting actually shows:
- **Header Row** → the style's first-row formatting (`firstRow`).
- **Total Row** → the style's last-row formatting (`lastRow`).
- **Banded Rows** → horizontal row banding (the style's `band1Horz`/`band2Horz`).
- **First Column** → first-column formatting (`firstColumn`).
- **Last Column** → last-column formatting (`lastColumn`).
- **Banded Columns** → vertical column banding.
Default for a freshly inserted table: **Header Row + First Column + Banded Rows ON** (verified in real Word this session).

## Connections (critical — this is why it can't be specced in isolation)
- **↔ Table Styles (tight, bidirectional preview coupling).** These toggles format *nothing on their own* — they choose which conditional parts of the **currently-/about-to-be-applied** table style take effect. Toggling any one of them **live-re-renders every thumbnail in the Table Styles gallery** so each style previews *with the current options*; clicking a style then applies it with those options baked in. (Captured live this session: toggling **Banded Rows** restripes the gallery previews.) The option state **persists** across style changes and across selection.
- **↔ Table Styles ▸ banding definitions.** Banded Rows/Columns are no-ops on a style with no band definition; on a banded style they show/hide the stripes. So this control's visible effect is a *function of the applied style*.
- **↔ Borders & Shading (indirect).** The conditional style parts (firstRow, etc.) carry their own borders + shading from the **style definition**, so these toggles change which borders/shading the user sees — but they never write per-cell borders/shading themselves (that's the Borders group's job). Important for our model: this writes a table-level property, the Borders group writes per-edge cell properties; they must not clobber each other.

## OOXML
A single `<w:tblPr><w:tblLook>` bitmask on the table: `w:firstRow` `w:lastRow` `w:firstColumn` `w:lastColumn` `w:noHBand` `w:noVBand`. ⚠️ The band flags are **inverted** — checked "Banded Rows" ⇒ `w:noHBand="0"`. It modifies how the table's `w:tblStyle` renders; it emits **no** per-cell formatting.

## Canvas interaction
**None.** A table-style property — it selects nothing, moves nothing, floats nothing, and imposes **no requirement on the floating canvas.** (Recorded for completeness: most Table *Design* controls are canvas-inert; the canvas-relevant table controls live in Table Layout — the move/resize handles and Draw/Eraser.)

## Current clone state
**MISSING.** The clone's Table Design tab (`src/renderer/public/js/table-tools-pm.js`, `designTab()` ~:63) renders **no** Table Style Options group. The fork round-trips the `tblLook` attr (`extensions/table/table.js:112,1652`) but **no bridge verb writes it** (no `setTableLook` anywhere).

## Feasibility
🟡 **Additive (small), except the live preview.** The attr already round-trips, so:
- (a) add `WC.PM.tableSetLook({firstRow,lastRow,firstColumn,lastColumn,noHBand,noVBand})` — **S**;
- (b) render the 6-checkbox group in the contextual tab + read current state — **S**;
- (c) the **live gallery-preview coupling** (re-render the Table Styles thumbnails with the current `tblLook`) — depends on a real Table Styles gallery existing (see `table-styles-gallery.md`) — **M**.
No fork edit (the attr is supported); this is bridge-verb + UI.

## What the floating canvas must support for this
**Nothing — canvas-inert.** Its only cross-feature requirement is on the **Table Styles gallery** (the live-preview coupling), not on the canvas.

## Open questions for our discussion
- Ship (a)+(b) now (toggles apply immediately), and defer (c) the live thumbnail preview until we build the real Table Styles gallery? (decouples the S work from the M preview)
- Match Word's default `tblLook` for new tables (firstRow + firstColumn + bandedRows)?

## Decision
**TBD — to be decided together.**
