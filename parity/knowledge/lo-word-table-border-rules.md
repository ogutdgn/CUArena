# LO-consult rule note — MS-Word table border/shading semantics

> Produced by the first LO-consult research run (2026-07-01) against the local LibreOffice
> clone at `new-coding/core`. LibreOffice is used as a KNOWLEDGE SOURCE for Word semantics
> (rules/algorithms), NEVER as a code/architecture source (RUBRIC process rule + MPL/GPL
> licensing). Confidence labels: **doc** = a comment/spec citation states Word does X;
> **inf** = inferred from LO's logic. LO file paths are evidence pointers, relative to the
> local clone.

## (a) Border conflict on a shared edge (collapsing mode)

- **A1 [doc].** Winner = higher "Word weight" = (style rank) × (line width), per
  [MS-OI29500] §17.4.66 tcBorders (LO cites the spec). Style ranks (brcType values):
  single=1, thick=2, double=3, dotDash=8, dotDotDash=9, triple=10, thinThickSmallGap=11,
  thickThinSmallGap=12, thinThickMediumGap=14, thickThinMediumGap=15, thinThickLargeGap=17,
  thickThinLargeGap=18, wave=20, doubleWave=21, dashSmallGap=22, threeDEmboss=24,
  threeDEngrave=25, outset=26, inset=27. Special: `none` weight 0; **dotted/dashed always
  weight exactly 1.0 regardless of width**.
  → `svx/source/dialog/framelink.cxx` ~213–303 (`GetWordTableCellBorderWeight`).
- **A2 [inf].** Equal-weight tie-break (LO's fallback, NOT asserted as Word's): wider wins →
  double beats single → smaller internal gap wins → non-dotted beats dotted. LO does NOT
  implement ECMA-376's "darker color (R+B+2G) wins" tie-break — ❓ see unknowns.
  → `framelink.cxx` ~306–336 (`Style::operator<`).
- **A3 [inf].** Resolution is per overlapping SEGMENT, not per whole edge (segments split;
  each piece takes the max under A1/A2). → `sw/source/core/layout/paintfrm.cxx` ~3102–3213.
- **A4 [doc/inf].** Word-mode painting quirks (gated on the C2 flag):
  outer horizontal lines never mirrored / outer vertical always mirrored (thickness grows
  outward on vertical table edges, not on the bottom); outer segments never merge with inner
  ones; a vertically-merged cell's left/right border is truncated where covered cells have no
  border; a follow-table (page split) paints the previous last row's BOTTOM border as its top;
  bottom border not painted when cell content was cut off. → `paintfrm.cxx` ~2263, ~2858,
  ~2932, ~3050–3130, ~5713.

## (b) Layering: tblBorders vs table style vs tcBorders

- **B1 [inf].** Per-cell stack, lowest→highest: table defaults < table-style conditional
  (cnf) props < row-level `tblPrEx` < direct `tcPr`.
  → `sw/source/writerfilter/dmapper/DomainMapperTableHandler.cxx` ~817–905; `TableManager.hxx` ~112.
- **B2 [doc].** Direct `tblPr` overrides the style's `tblPr`; style `basedOn` chain resolves
  parent-first, child overrides. → `DomainMapperTableHandler.cxx` ~406–440; `StyleSheetTable.cxx` ~180.
- **B3 [inf].** Conditional-format precedence (low→high): Band2Horz < Band1Horz < Band2Vert <
  Band1Vert < LastCol < FirstCol < LastRow < FirstRow < corner cells (SW/SE/NW/NE). Banding
  weakest; columns beat bands; rows beat columns; corners beat all. Regions gated by tblLook
  bits (0x20 firstRow, 0x40 lastRow, 0x80 firstCol, 0x100 lastCol, 0x200 noHBand, 0x400
  noVBand); a `tblHeader` row is forced to first-row formatting; band counting shifts by one
  when first-row is on. → `StyleSheetTable.cxx` ~235–268; `DomainMapperTableHandler.cxx` ~765–851.
- **B4 [inf].** A conditional region's edge border ERASES the style insideH/V at that
  boundary. → `StyleSheetTable.cxx` ~198–233.
- **B5 [inf].** insideH/V → per-cell edges: cell-carried inside values beat table-level;
  insideH/V directly on a `tcPr` are meaningless and dropped (tdf#82177); table outer edges
  apply only to perimeter cells lacking own values; insideV = right of non-last + left of
  non-first cells; insideH = bottom of first row, top+bottom of middle rows, top of last row;
  no inside borders on 1×1 / single-col (V) / single-row (H).
  → `DomainMapperTableHandler.cxx` ~126–201, ~813–815, ~914–939.
- **B6 [doc] ⭐.** An explicit cell-level "none/nil" defeats the STYLE border but NOT the
  TABLE border — if table-level has a line and cell+style say none, the table border shows
  through (LO deletes the cell-level entries to match Word).
  → `DomainMapperTableHandler.cxx` ~857–895.
- **B7 [doc].** Vertical merge: bottom border comes from the LAST covered cell; Word applies
  left/right per-unmerged-row (LO can't model that — states it as Word's behavior).
  → `DomainMapperTableHandler.cxx` ~941–971.

## (c) Word compat flags / quirks

- **C1 [inf].** Collapsed borders = `RES_COLLAPSING_BORDERS`, forced true per document
  (#i29550). → `sw/source/uibase/app/docshini.cxx:300`; `tabfrm.cxx:6735`.
- **C2 [inf].** The "behave like Word" paint switch is `DocumentSettingId::TABLE_ROW_KEEP`,
  set unconditionally by both .doc and .docx importers; gates A1 + A4.
  → `ww8par.cxx:2012`; `dmapper/SettingsTable.cxx:677`.
- **C3 [doc].** compatibilityMode ≥ 15 (Word 2013+): top-level tables indented like nested
  ones; without a declared mode Word invents a version-dependent left indent; Word positions
  the table at the left EDGE of its border (Writer at the middle → +half left border width).
  → `DomainMapperTableHandler.cxx` ~618–654.
- **C4 [doc].** Cell content never overlaps borderlines: effective left padding =
  max(leftBorderWidth/2, declared margin); clamped analog on the right.
  → `DomainMapperTableHandler.cxx` ~317–349.
- **C5 [doc].** `overrideTableStyleFontSizeAndJustification`: default-para-style size of
  exactly 11/12pt, or left justification, is overridden BY the table style unless disabled.
  → `DomainMapperTableHandler.cxx` ~1305–1326.
- **C6 [inf].** Export symmetry: omit a `tcBorders` edge identical to the style's; `w:sz` in
  1/8pt clamped to [2,96]. → `docxattributeoutput.cxx` ~4708–4740.

## (d) Shading

- **D1 [inf].** Same layering as borders: style cnf shading (B3 order) < row `tblPrEx` shd <
  direct `tcPr` shd; table-level shd is the background under everything.
- **D2 [doc].** `w:shd` flattens to ONE color: pattern → per-mille foreground fraction
  (clear=0, solid=1000, pctNN→NN0, stripe/cross ≈333‰); RGB = (fore·p + fill·(1000−p))/1000;
  `fill="auto"`=white, `color="auto"`=black. → `dmapper/CellColorHandler.cxx` ~104–232.
- **D3 [inf].** Table-style paragraph fill applies only if the paragraph/its style doesn't
  set its own (C5 exception applies). → `DomainMapperTableHandler.cxx` ~1329–1337.

## ❓ Unknowns LO could not settle → resolve via OUR Word oracle (D6.3 targeted experiments)

1. Does real Word apply ECMA-376 §17.4.67's equal-weight "darker color (R+B+2G) wins"
   tie-break? (LO never implements it.)
2. Which cell wins a PERFECT tie differing only in color?
3. Word's exact left/right border rule for vertically merged cells (per-unmerged-row).
4. Does Word z-stack paragraph shading over cell shading at paint time, or flatten?
