# Table Design (contextual tab) — Insert > Tables

> Feasibility doc for the **Table Design** contextual tab (one of the two tabs real Word
> raises when the caret/selection is inside a `w:tbl`). Companion: `table-layout-tab.md`.
> Parity reference: **Word for Windows 16.0** (ADR-0006).
>
> **Button-by-button** analysis: every individual control on Word's Table Design tab gets
> its own subsection (What real Word does · Current clone state · Verdict · Required structure
> · Decision). The clone's current `designTab()` barely resembles Word's tab — it renders only
> two groups (a flat "Table Styles" trio + a clone-invented "Alignment" group) and is missing
> the entire **Table Style Options** group, the previewed style gallery + **More**, the full
> **Shading** palette, and almost all of the **Borders** group.
>
> Clone code touchpoints (all state claims below cite file:line):
> - Tab definition (what renders): `src/renderer/public/js/table-tools-pm.js:63-79` (`designTab()`).
> - Handlers (`H.tbl*`): `src/renderer/public/js/commands.js:110-244`.
> - Bridge verbs (`WC.PM.*`): `src/renderer/bridge/table.ts`.
> - Fork commands/attrs: `src/renderer/core/superdoc-fork/extensions/table/table.js`,
>   `.../extensions/table-cell/table-cell.js`, `.../extensions/shared/renderCellBorderStyle.js`.
> - Known-gaps ledger: `docs/bug-hunt/INSERT-COMPLETENESS.md`.

---

## Decisions (locked as we go)

_None yet — every verdict below is **Decision: TBD**._

---

## Verdict legend

- ✅ **already-works** — control exists in the clone and behaves like Word (modulo cosmetics).
- ✅ **NO-FORK** — buildable with existing bridge/fork verbs; only UI (and maybe a dialog) is missing.
- 🟡 **additive-fork** — needs a new *owned* command/attr added to the vendored fork (additive, same
  pattern as the existing `setTableStyle`/`setCellBorders`); not a risky core edit.
- 🔴 **new-subsystem** — needs a whole new interaction layer or style-authoring subsystem.
- ⛔ **external** — depends on something outside the app (cloud/Office.js/etc.). _(none on this tab)_

---

# Group 1 — Table Style Options (6 checkboxes → `w:tblLook`)

All six share **one mechanism**: each toggles a bit of `w:tblPr/w:tblLook`, which tells the
*applied table style* which bands/edges to emphasize. The clone has **none** of them and no verb
that *sets* `tblLook` — so they're treated as one subsection, but each box is listed.

**What real Word does (all six):** each is an independent checkbox. Checking/unchecking flips a
`tblLook` flag and Word repaints the table's banding/emphasis live (it does **not** change cell
content, only which style-defined band formatting is shown).

- **Header Row** → `tblLook.firstRow` — emphasize the first (header) row.
- **Total Row** → `tblLook.lastRow` — emphasize the last (total) row.
- **Banded Rows** → `tblLook.noHBand` **inverted** (checked = `noHBand:false` = horizontal bands on).
- **First Column** → `tblLook.firstColumn` — emphasize the first column.
- **Last Column** → `tblLook.lastColumn` — emphasize the last column.
- **Banded Columns** → `tblLook.noVBand` **inverted** (checked = `noVBand:false` = vertical bands on).

**Current clone state:** entirely **absent**. `designTab()` (`table-tools-pm.js:65-77`) renders no
Table Style Options group and no checkboxes. There is **no** `tableSetLook`/`setTableLook` verb
anywhere (`bridge/table.ts` has no such function; a repo-wide search for `setTableLook`/`tableSetLook`
finds nothing). The fork *does* model the attr — `tblLook` is a documented `TableProperties` field
(`table/table.js:112`) and `setTableStyle` *reads* `nextProps.tblLook` to decide first-row emphasis
(`table/table.js:1652-1653`) — but **nothing writes it from the UI**; `setTableStyle` explicitly
"Does NOT modify `tblLook.firstRow`" (`table/table.js:1346`).

**Verdict:** 🟡 **additive-fork** — NO-FORK in *spirit* but needs one new owned command. This is the
single highest-fidelity gap on the tab and the only control that genuinely needs a new verb.

**Required structure:**
- New owned fork command `setTableLook({firstRow,lastRow,firstColumn,lastColumn,noHBand,noVBand})`
  in `table/table.js` that writes the bits into `tableProperties.tblLook` on the table node (same
  additive pattern as `setTableStyle`/`setTableIndent`; the importer/exporter already round-trip
  `tblLook`, so no converter work).
- Bridge verb `WC.PM.tableSetLook(...)` in `bridge/table.ts` wrapping it.
- New `td-styleopts` group of 6 checkbox controls in `designTab()` + 6 `H.tblLook*` toggle handlers.
- State reflection: on caret entry read the table node's current `tblLook` to set each checkbox
  (parallel to how `tableInfo()` already reads `styleId`/`alignment` at `table.ts:391-412`).

**Decision: TBD.**

---

# Group 2 — Table Styles

## 2.1 — Table Styles gallery (built-in styles)

**What real Word does:** a large, *live-previewed* gallery — Plain Table 1–5, Grid Table 1–7
(Light + Accent 1–6 variants), List Table 1–7 (Accent variants), etc. Hovering previews the style
on the table; clicking applies it (`w:tblPr/w:tblStyle`).

**Current clone state:** a flat **text list**, not a gallery. `tblStyles` dropdown
(`table-tools-pm.js:67`) → `H.tblStyles` (`commands.js:187-196`) builds the flyout **dynamically**
from `WC.PM.getTableStyles()` (`table.ts:371-387`), which reads the runtime
`word/styles.xml` `w:type="table"` entries (excludes `semiHidden`, e.g. TableNormal). Clicking
applies `WC.PM.tableSetStyle(id)` (`table.ts:140-144`) → `editor.commands.setTableStyle`
(`table/table.js:1617`). The apply path and the `w:tblStyle` write are **real and correct** — it's
just a flat list (no thumbnails, no hover preview) and the catalog is only as rich as what the doc's
`styles.xml` actually defines.

**Verdict:** ✅ **already-works** (apply is real) — gallery polish is ✅ **NO-FORK** cosmetic.

**Required structure:** keep the `setTableStyle`/`getTableStyles` apply path verbatim; upgrade the
flyout to a thumbnail/swatch grid with hover preview. Pure renderer work; no new verb.

**Decision: TBD.**

## 2.2 — Gallery More ▸ New Table Style…

**What real Word does:** opens the Create New Style from Formatting dialog scoped to a *table*
style — name, base style, per-band (whole-table/header-row/banded-rows/first-column/…) font,
borders, shading — and writes a `w:style w:type="table"` (with `w:tblStylePr` band definitions)
into `styles.xml`, then makes it selectable in the gallery.

**Current clone state:** **absent.** The `tblStyles` flyout (`commands.js:187-196`) has no More
menu and no New/Modify/Clear entries.

**Verdict:** 🟡 **additive-fork** (UI-heavy NO-FORK; needs a **new dialog** + an owned styles-write).

**Required structure:** a style-editor dialog that composes a `w:style w:type="table"` element
(+ `w:tblStylePr` band parts) and upserts it into the runtime
`editor.converter.convertedXml['word/styles.xml']` (the owned-styles-write pattern already used
elsewhere, e.g. hyphenation's settings.xml upsert). Then `getTableStyles()` surfaces it for free.
Medium effort; no core-fork edit required if we reuse the converter's styles part.

**Decision: TBD.**

## 2.3 — Gallery More ▸ Modify Table Style…

**What real Word does:** same dialog as New, pre-filled with the *currently applied* style's
definition; saving rewrites that `w:style` and repaints every table using it.

**Current clone state:** **absent** (same as 2.2 — no More menu).

**Verdict:** 🟡 **additive-fork** — shares the New Table Style dialog; adds read-back/pre-fill of an
existing `w:style` definition + an in-place rewrite.

**Required structure:** the 2.2 dialog plus: read the applied style's `w:style` from `styles.xml`,
pre-fill, and rewrite the same element in place. Repaint via re-applying the style id.

**Decision: TBD.**

## 2.4 — Gallery More ▸ Clear

**What real Word does:** removes the table style (reverts to the default/`TableNormal`) — clears
`w:tblStyle` and the table-style-driven banding.

**Current clone state:** **absent** as a menu entry, but the underlying capability exists —
`setTableStyle` is the same verb that would apply an empty/`TableNormal` id.

**Verdict:** ✅ **NO-FORK** (verb exists; just needs a menu entry).

**Required structure:** a "Clear" flyout item that calls `WC.PM.tableSetStyle('')` (or
`'TableNormal'`) via the existing `setTableStyle` path (`table.ts:140`). No new verb. Confirm the
fork's `setTableStyle` accepts an empty id as a clear (it reads `id ? resolve… : null` at
`table/table.js:1628`, which suggests an empty id is handled — verify).

**Decision: TBD.**

## 2.5 — Shading (cell fill split-button)

**What real Word does:** a split-button — the gallery half is the full color picker (theme-color
columns with tints/shades, the standard-colors row, **No Color**, **More Colors…** → custom RGB).
Applies cell fill `w:tc/w:tcPr/w:shd` to the selected cell(s); No Color clears it.

**Current clone state:** a fixed **6-swatch** grid. `tblShading` dropdown (`table-tools-pm.js:68`)
→ `H.tblShading` (`commands.js:197-206`) renders 6 hard-coded swatches
(`#FFF2CC,#DEEAF6,#E2EFDA,#FCE4D6,#D9D9D9,transparent`) and applies via
`WC.PM.tableSetCellShading(color)` (`table.ts:107-115`) → `editor.commands.setCellBackground`
(`table/table.js:1461`). The `w:shd` apply path is **real and correct** (and caret-cell-safe via the
`setCellAttr` fallback noted at `table.ts:108-114`); only the palette is impoverished — no theme
columns, no standard row, no "No Color" label, no More Colors… (the transparent swatch *is* the
clear path: it passes `''`).

**Verdict:** ✅ **NO-FORK** — apply path is done; replace the 6-swatch grid with the shared palette UI.

**Required structure:** swap the hard-coded swatch grid for the shared color-palette picker (theme +
standard rows + No Color + More Colors…). Same `setCellBackground` apply; `''` clears (already wired
at `commands.js:202`). No new verb, no fork edit.

**Decision: TBD.**

---

# Group 3 — Borders

> Key fork fact threaded through every Borders control: **`setCellBorders(b)`**
> (`table.ts:203-207` → `table/table.js:1858-1863`) already accepts a per-edge map
> `{top|bottom|left|right: {val,color,size}}` and writes it as the cell `borders` attr. So the
> *apply* mechanism for most of this group exists — the gap is almost entirely **UI** (the clone
> hard-codes one preset). **Caveat:** at the **cell** level only `top/right/bottom/left` actually
> *render* — `renderCellBorderStyle` (`shared/renderCellBorderStyle.js:15`) paints only those four
> sides. `insideH`/`insideV` render only on the **table-level** `borders` attr (via the
> `--wc-inside-h/v` CSS custom props, `table/table.js:626-630`), and **diagonal** edges
> (`tl2br`/`tr2bl`) have **no render path anywhere** in the fork (a search finds no diagonal
> handling). This bounds how far "per-edge Borders" can faithfully go without fork work.

## 3.1 — Borders dropdown (per-edge presets)

**What real Word does:** a 12-ish-entry menu — Bottom / Top / Left / Right / No Border / All
Borders / Outside Borders / Inside Borders / Inside Horizontal / Inside Vertical / Diagonal-Down /
Diagonal-Up, plus the **Borders and Shading…** launcher (see 3.7). Each toggles the corresponding
edge(s) on the selection using the active pen (line style/weight/color).

**Current clone state:** only **All Borders** and **No Border**. `tblBorders` dropdown
(`table-tools-pm.js:69`) → `H.tblBorders` (`commands.js:207-212`) offers exactly two items:
"All Borders" calls `tableSetCellBorders({top,bottom,left,right: B()})` and "No Border" calls
`tableSetCellBorders({})`, where `B()` is hard-coded `{val:'single',color:'000000',size:4}`
(`commands.js:209`). The remaining 8+ presets (Top/Bottom/Left/Right/Outside/Inside/Inside-H/
Inside-V/Diagonal) are absent.

**Verdict:** ✅ **NO-FORK** for the four sides + All/No/Outside; 🟡 **additive-fork** for
Inside-H/Inside-V (cell-level rendering missing) and Diagonal-Down/Up (no render path at all).

**Required structure:**
- Top/Bottom/Left/Right/Outside/All/No: expand the flyout to emit the right per-edge subset of the
  existing `{top,bottom,left,right}` map → `tableSetCellBorders`. UI-only.
- Inside-H/Inside-V: applied across a multi-cell `CellSelection` they could be expressed as
  per-cell edge writes, but the cell renderer won't paint dedicated interior keys — needs either a
  table-level `borders` write (table.js already paints `--wc-inside-h/v`) or a fork addition to
  `renderCellBorderStyle`. Verify before promising.
- Diagonal-Down/Up: **no render path** — needs new fork attr + CSS (e.g. a diagonal overlay). Defer
  or scope as additive-fork.

**Decision: TBD.**

## 3.2 — Line Style dropdown

**What real Word does:** the pen's line *style* — single / double / dashed / dotted / thick-thin /
… (OOXML `w:val`). Sets the active pen used by the Borders dropdown and Border Painter.

**Current clone state:** **absent.** The `val` is hard-coded to `'single'` inside `B()`
(`commands.js:209`); there is no control to choose it.

**Verdict:** ✅ **NO-FORK** — the value already flows through `setCellBorders` ({val,...}); only the
picker UI + pen state are missing.

**Required structure:** a dropdown that sets the active pen's `val`; thread that state into the
`{val,color,size}` object passed to `tableSetCellBorders` instead of the literal `'single'`. No new
verb. (Render fidelity is bounded: `renderCellBorderStyle` emits `solid` regardless of `val`
(`shared/renderCellBorderStyle.js:22`), so non-single styles export correctly but paint as solid
in-app until the renderer honors `val`.)

**Decision: TBD.**

## 3.3 — Line Weight dropdown

**What real Word does:** the pen *weight* — ¼ / ½ / ¾ / 1 / 1½ / 2¼ / 3 / 4½ / 6 pt (OOXML `w:sz`
in eighths of a point).

**Current clone state:** **absent.** `size` is hard-coded to `4` (= ½ pt) in `B()`
(`commands.js:209`); no weight picker.

**Verdict:** ✅ **NO-FORK** — `size` already flows through `setCellBorders`; only the picker + pen
state are missing.

**Required structure:** a weight dropdown that sets the active pen's `size` (¼ pt → `sz:2`, … 6 pt →
`sz:48`); thread into the pen state. No new verb. The cell renderer honors size as px
(`renderCellBorderStyle.js:22`), so weight paints correctly.

**Decision: TBD.**

## 3.4 — Pen Color

**What real Word does:** the pen *color* picker (theme/standard/No Color/More Colors…) → OOXML
`w:color` on the border.

**Current clone state:** **absent.** `color` is hard-coded to `'000000'` in `B()`
(`commands.js:209`); no color picker.

**Verdict:** ✅ **NO-FORK** — `color` already flows through `setCellBorders`; only the picker + pen
state are missing.

**Required structure:** reuse the shared color-palette picker to set the active pen's `color`; thread
into the pen state. No new verb. (`renderCellBorderStyle` honors color, `auto`→black.)

**Decision: TBD.**

## 3.5 — Border Styles gallery (preset pens)

**What real Word does:** a gallery of canned pen presets (theme-aware `{val,size,color}` combos) —
clicking one sets the active pen in one shot.

**Current clone state:** **absent.**

**Verdict:** ✅ **NO-FORK** — composes the three pen pickers above; no new verb.

**Required structure:** a flyout of canned `{val,size,color}` presets that set the active pen state
(the same state feeding 3.1–3.4). UI-only.

**Decision: TBD.**

## 3.6 — Border Painter

**What real Word does:** a toggle that enters a "paint with the pen" mode — the cursor becomes a pen
and each cell edge you click takes the active pen's border. Click the button again (or Esc) to exit.

**Current clone state:** **absent.**

**Verdict:** 🔴 **new-subsystem** (NO-FORK at the data layer, but needs a renderer interaction layer).

**Required structure:** a UI toggle that, while active, hit-tests the painted table to find the
nearest cell edge under the pointer and applies the active pen via `setCellBorders` to that edge
(the apply verb exists — `table.ts:203`). The new part is the edge-hit-test/overlay over the
PE-painted table + mode lifecycle. No new bridge verb.

**Decision: TBD.**

## 3.7 — Borders and Shading… dialog

**What real Word does:** the full tabbed dialog — **Borders** (setting/style/color/width + per-edge
preview diagram, "Apply to" cell/table), **Page Border**, **Shading** (fill + pattern). The
one-stop authoring surface for everything in this group.

**Current clone state:** **absent.**

**Verdict:** 🟡 **additive-fork** (mostly NO-FORK; needs a **new dialog**; the Page-Border tab
overlaps existing page-border machinery).

**Required structure:** a tabbed dialog that aggregates `setCellBorders` (`table.ts:203`) +
`setCellBackground` (`table.ts:107`) + a table-level borders write, with the interactive per-edge
preview diagram. The Page Border tab can reuse existing page-border code. Medium effort; no core-fork
edit if the per-edge writes stay within the existing `setCellBorders` map (subject to the
insideH/V/diagonal render caveats above).

**Decision: TBD.**

---

# Appendix — clone-only "Alignment" group (not a Word Table Design group)

The clone's `designTab()` renders a second group, **`td-align` "Alignment"**
(`table-tools-pm.js:71-76`), that does **not** exist on Word's Table Design tab (Word keeps table
alignment + indent under **Table Layout ▸ Table Properties**):

- **Align Left / Center / Right** — `tblAlignLeft/Center/Right` → `H.tblAlign*`
  (`commands.js:133-135`) → `WC.PM.tableSetAlignment` (`table.ts:146-150`). Real verb, works.
- **Indent** dropdown — `tblIndent` → `H.tblIndent` (`commands.js:243-244`) → `WC.PM.tableSetIndent`
  (`table.ts:152-156`). Real verb, works.

**Verdict:** ℹ️ already-works but **misplaced**. These are real, functioning verbs — the only
question is whether to keep them here for convenience or relocate them to Table Layout to match Word.

**Decision: TBD.**

---

## New bridge verbs / dialogs needed (summary)

**New fork command + bridge verb (the ONE thing that needs a fork addition):**
- `setTableLook(...)` / `WC.PM.tableSetLook(...)` — for the entire Table Style Options group (§1).
  Additive owned command (same class as `setTableStyle`); the converter already round-trips
  `tblLook`.

**No new verb — UI (and sometimes a dialog) only:**
- Per-edge Borders, Line Style, Line Weight, Pen Color, Border Styles, Border Painter (data layer) —
  all ride the existing `setCellBorders` (`table.ts:203`); the blocker is the hard-coded `B()` pen
  and the missing pen-state plumbing. *(insideH/V + diagonal have render-fidelity caveats.)*
- Full Shading palette + No Color + More Colors — rides existing `setCellBackground` (`table.ts:107`).
- Style gallery polish + Clear — ride existing `setTableStyle` (`table.ts:140`).

**New dialogs:**
- **Borders and Shading…** (§3.7) — aggregates `setCellBorders` + `setCellBackground` + table-level
  borders.
- **New / Modify Table Style…** (§2.2/§2.3) — style-editor dialogs writing
  `w:style w:type="table"` + `w:tblStylePr` into the runtime `styles.xml`.

---

## Open questions

1. **Tab restructure:** rebuild `designTab()` to Word's real 3 groups (Table Style Options / Table
   Styles / Borders) and move the clone's Alignment group to Table Layout, or keep continuity?
2. **`setTableLook` priority:** is the one fork addition worth it for v1 (highest-fidelity gap), or
   lower than fixing Borders?
3. **Borders depth:** four sides + pens (cheap, big win) only, or also Border Painter
   (interaction layer) and Borders and Shading… (new dialog)?
4. **insideH/V + diagonal:** confirm/accept the render caveats (cell renderer paints only 4 sides;
   diagonals have no render path) before promising those Borders-dropdown entries.
5. **Style-authoring (New/Modify Table Style):** in scope this pass, or defer as a separate subsystem?
6. **Gallery thumbnails:** cosmetic upgrade in scope, or keep the honest list and spend effort on
   Borders/Style-Options?

---

## Decision

**TBD — to be decided together.**
