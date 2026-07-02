# Word table cnfStyle/tblLook stamping rules (locked build 16.0, oracle-derived)

> Derived 2026-07-02 from direct COM apply-and-save probes + the 8 rw style fixtures; every rule
> below is differ-verified against real Word output (zero cnf/tblLook mismatches across the 8
> pilot style tasks after implementation). Implementation:
> `src/renderer/bridge/table-conditional-formats.ts`. Method note: probes are ONE Word instance,
> many docs, run INLINE in the session shell (nested `powershell -File` hangs — the archive's
> "bulk extraction hangs" lesson was that launch artifact).

## tblLook

`<w:tblLook w:val="XXXX" w:firstRow w:lastRow w:firstColumn w:lastColumn w:noHBand w:noVBand>`
— always all 6 flags + val. val = OR of: firstRow 0x20 · lastRow 0x40 · firstColumn 0x80 ·
lastColumn 0x100 · noHBand 0x200 · noVBand 0x400. Defaults 04A0 (firstRow+firstColumn+noVBand).
Verified transitions: totalRow on → 04E0 · headerRow off → 0480 · bandedCols on → 00A0.

## cnfStyle 12-char val positions

`[0]firstRow [1]lastRow [2]firstColumn [3]lastColumn [4]oddVBand(band1Vert) [5]evenVBand
[6]oddHBand(band1Horz) [7]evenHBand [8]neCell(firstRowLastColumn) [9]nwCell(firstRowFirstColumn)
[10]seCell(lastRowLastColumn) [11]swCell(lastRowFirstColumn)` — positions 0-7 pinned by the
styleopt fixtures; position 9 pinned by List Table 3 / LT7 Colorful (`001000000100` on cell 0,0);
8/10/11 ride the ECMA order (untested — no measured style stamps them with default look).
Elements carry the val AND all 12 explicit 0/1 named attributes.

## Stamping algorithm (per styled table; plain/TableGrid tables get NO cnfStyle)

- **Row (trPr):** firstRow bit on row0 iff look.firstRow; lastRow bit on last row iff
  look.lastRow; else horizontal banding iff !noHBand — band index = rowIdx − (firstRow?1:0),
  bands run to R−2 when lastRow else R−1, EVEN index → `oddHBand` stamped, ODD index → NO element.
- **Cell (tcPr):**
  - If the table has NO column roles (firstColumn/lastColumn off AND noVBand) → cells carry NO
    cnfStyle at all (even when rows carry firstRow/band stamps) — fixture-verified
    (styleopt-firstcol-off).
  - Else: col0 → firstColumn bit iff look.firstColumn; last col → lastColumn iff look.lastColumn;
    else vertical banding iff !noVBand (index after col0 when firstColumn on; EVEN → oddVBand);
    else inherit the ROW role bit; else an explicit ALL-ZEROS element (`000000000000`) —
    fixture-verified (styleopt-bandedcols-on row cells).
- **Corners:** stamped ONLY when the active STYLE DEFINES the corner tblStylePr type
  (nwCell/neCell/seCell/swCell — List Table 3/7 families do; Grid Table 4 does not) AND both edge
  conditions are look-enabled + geometric: the corner bit is ADDED to the cell's edge bit
  (cell(0,0) = firstColumn + nwCell → `001000000100`). Only nw is empirically exercised (default
  look has lastRow/lastColumn off); ne/se/sw are the symmetric construction.
- Word does NOT emit band2 (even) bits or corner bits for styles lacking those tblStylePr types.
- Refuted hypotheses (recorded so nobody re-tests them): stamping does NOT differ between direct
  apply and style-switch (TableGrid→X identical to X); the exhaustive-per-cell pattern initially
  "observed" on List Table 3 was a regex artifact (trPr/tcPr mixed), not real.

## Interplay

- setTableStyle does not clear/re-derive stamps → the bridge restamps after style apply and after
  structural edits (add/delete row/col, merge, split); a checkbox toggle = look flip + full
  restamp in ONE transaction (one undo step).
- The paged renderer reads cnfStyle additively (position×tblLook already drives paint) — stamping
  is export-fidelity-first and paint-safe.
