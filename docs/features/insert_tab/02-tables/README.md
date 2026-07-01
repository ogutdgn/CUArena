# Insert > Tables — feasibility index

The Insert > Tables group is one split button (**Table**) whose dropdown holds the grid
picker plus five command items. All six flows are documented in
**[table.md](table.md)** (they share the `w:tbl` engine seam).

Shared engine facts (grounded in the fork):
- **Node:** `extensions/table/table.js` — real PM `table`/`table-row`/`table-cell`; `insertTable` + `convertTextToTable` are genuine fork commands.
- **Converter:** `core/super-converter/v3/handlers/w/tbl/tbl-translator.js` — full `w:tbl` import/export (style, grid, `gridSpan`/`vMerge` merges, borders, shading).
- **Bridge:** `bridge/table.ts` — `insertTable`, `textToTable`, `tableAutoFit`, `tableSetStyle`, full Design/Layout verb set.
- **Missing:** NO OLE handler anywhere (`o:OLEObject` / `w:object` → zero matches under `superdoc-fork/`).

| Button / flow | Verdict | Size | Required structure (one line) |
|---|---|---|---|
| [Grid picker](table.md#flow-1--grid-picker) | ✅ Already works | S | reuse `table` node + `tbl-translator.js`; only row/col orientation + default `TableGrid` stamp |
| [Insert Table… dialog](table.md#flow-2--insert-table-dialog) | ✅ Buildable NO-FORK | S | add AutoFit radios → existing `tableAutoFit` verb; no new node/handler |
| [Draw Table](table.md#flow-3--draw-table) | ✅ Buildable NO-FORK | L (S to keep current) | true pen+eraser on existing merge/split/border verbs + PE grid hit-test |
| [Convert Text to Table…](table.md#flow-4--convert-text-to-table) | ✅ Already works | S | `convertTextToTable` fork cmd + `textToTable` bridge verb, both wired |
| [Excel Spreadsheet](table.md#flow-5--excel-spreadsheet) | ⛔ External runtime (🔴 new subsystem if static) | XL (L static) | NEW `oleObject` node + NEW `w:object`/`o:OLEObject` handler + embeddings part — none exist |
| [Quick Tables](table.md#flow-6--quick-tables) | ✅ Buildable NO-FORK | M | hard-coded styled+populated templates via `insertTable`+`tableSetStyle`; gallery-save is a separate deferrable L |

**Headline:** five of six flows are NO-FORK (two already work). The only hard gap is
**Excel Spreadsheet**, which needs an OLE subsystem the fork lacks entirely (and a live
runtime Electron does not have).
