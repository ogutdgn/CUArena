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
| table-styles-gallery | OPEN Table Styles gallery — the 2/247 gap side-by-side (level 2; Word via UIA Expand) | fail | Word: full gallery with Plain/Grid/List Tables sections, 100+ color thumbnails, Modify/Clear/New Table Style footer; clone: 2-item text flyout (Table Grid, Grid Table 4 Accent 1) - the 2/247 gap on screen |
| doc-styled-table | LEVEL 4 document render — Grid Table 4 Accent 1 styled 3x3 on the page | fail | same 3x3 GT4A1 table, banding order matches, BUT header fill differs: Word dark teal (current Office theme accent1 on locked build) vs clone royal blue (legacy 4472C4 palette); border tint likewise; minor width/position offset |
