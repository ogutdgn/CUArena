# Visual Ledger — clone vs real Word, side-by-side (D5)

Judge question (FIXED): *same screen of the same program? would a Word user notice
a difference at a glance? list the differences.* Verdicts recorded via
`visual_verify.py --record`; refused until the GOLDEN trust gate passes (D5.3).

**Golden gate:** PASSED

| Pair | What | Verdict | Reason |
|---|---|---|---|
| g-identical | GOLDEN: the same Word capture twice — the judge MUST pass it | pass | pixel-identical (same capture twice) |
| g-different | GOLDEN: Word Home vs clone Home — known-different; the judge MUST fail it and list differences | fail | styles gallery previews differ (real styled names vs aBbCcDd cards); Editing group labeled vs icon-only; search box position; ribbon height/padding |
| home | Home ribbon | fail | Word user notices at a glance: styles gallery (Word shows real styled previews incl Title/Subtitle, clone shows aBbCcDd cards w/ Heading 1-3), Editing group labels missing, File tab styling, search box placement, overall ribbon height |
| tabledesign | Table Design ribbon | fail | clone tab nearly empty vs Word's full tab (style options checkboxes, 15+ style thumbnails, pen controls, Border Painter) — the honest v2 baseline after the tables archive |
