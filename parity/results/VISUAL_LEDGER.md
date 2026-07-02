# Visual Ledger — clone vs real Word, side-by-side (D5)

Judge question (FIXED): *same screen of the same program? would a Word user notice
a difference at a glance? list the differences.* Verdicts recorded via
`visual_verify.py --record`; refused until the GOLDEN trust gate passes (D5.3).

**Golden gate:** PASSED

| Pair | What | Verdict | Reason |
|---|---|---|---|
| g-identical | GOLDEN: the same Word capture twice — the judge MUST pass it | pass | golden: identical Word captures - no differences |
| g-different | GOLDEN: Word Home vs clone Home — known-different; the judge MUST fail it and list differences | fail | golden: clone Home differs (Draw tab, Styles gallery thumbnails, missing Dictate/Add-ins, File button styling) |
| home | Home ribbon | fail | Styles gallery thumbnails differ; Format Painter/Dictate/Editor/Add-ins chrome missing or restyled; extra Draw tab; Search box placement |
| tabledesign | Table Design ribbon | fail | clone lacks Table Style Options group (6 checkboxes), visual style-tile gallery (icon-only dropdown instead), Border Styles/Pen/Border Painter group, Borders&Shading launcher; shows non-Word Alignment group; icon-only unlabeled rendering |
| tablelayout | Table Layout contextual ribbon (level 1) | fail | clone lacks Table group (Select/Gridlines/Properties), Draw group (Draw Table/Eraser), Delete menu, Insert Cells launcher, Sort/Repeat Header Rows/Formula in Data; 9-way alignment reduced to 3 vAlign; Height/Width steppers are dropdowns; tab NAME differs: Word 'Table Layout' vs clone 'Layout'; icon-only unlabeled rendering |
| insert-table-menu | OPEN Insert > Table dropdown — grid picker + items (level 2; Word via UIA Expand) | fail | item set/labels match (5 items) but: Word items carry icons + Quick Tables submenu arrow, clone plain text; Word grid live-label above grid ('1x1 Table'), clone header 'Insert Table'; Word disables Convert Text to Table with caret in table, clone does not gray it |
| table-styles-gallery | OPEN Table Styles gallery — the 2/247 gap side-by-side (level 2; Word via UIA Expand) | fail | TRANSFORMED by 030 (was: 2-item text flyout): clone now shows the full sectioned tile gallery (Plain/Grid/List Tables + 113 color tiles + Modify/Clear/New footer) - same CLASS as Word's. Residual cosmetic: simplified 4x5 thumbs vs Word's detailed row-glyph tiles, larger tile spacing/flyout geometry. |
| doc-styled-table | LEVEL 4 document render — Grid Table 4 Accent 1 styled 3x3 on the page | pass | PALETTE FIXED (030): both tables render the locked-build teal (#156082 header, teal band + tinted borders, same banding order) - a Word user glancing at the two documents sees the same table. Minor residual: slight table width/position offset (page metrics, not style). |
