# Spec Seeds — parity gaps → /speckit-specify input

Auto-generated from the parity ledger. Each block is a feature whose clone output diverges from real Word. Feed a block to `/speckit-specify`; the **ground-truth fixture** is the definition of correct behavior and the **acceptance** command is the regression gate.

## Align Left  (Home · T0)

**Goal:** make the clone's `Align Left` output match real Microsoft Word.
**Sub-tasks covered:** `alignleft`
**Ground truth:** `parity/fixtures/rw-alignleft.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only alignleft   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Bold  (Home · T0)

**Goal:** make the clone's `Bold` output match real Microsoft Word.
**Sub-tasks covered:** `bold`
**Ground truth:** `parity/fixtures/rw-bold.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only bold   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Bullets  (Home · T0)

**Goal:** make the clone's `Bullets` output match real Microsoft Word.
**Sub-tasks covered:** `bullets`
**Ground truth:** `parity/fixtures/rw-bullets.docx`
**Current parity:** GAP — 3 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (bullets): emit `numbering:lvlText[('val', '\uf0a7')]`
- FR (bullets): emit `numbering:lvlText[('val', '\uf0b7')]`
- FR (bullets): emit `numbering:lvlText[('val', 'o')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', '•')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', '▪')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', '◦')]`

### Structural requirements
- STR (bullets): `numbering` parts — Word=1, clone=0

### Acceptance (regression gate)
```
python parity/engines/run.py --only bullets   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Center  (Home · T0)

**Goal:** make the clone's `Center` output match real Microsoft Word.
**Sub-tasks covered:** `center`
**Ground truth:** `parity/fixtures/rw-center.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only center   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font  (Home · T0)

**Goal:** make the clone's `Font` output match real Microsoft Word.
**Sub-tasks covered:** `fontface`
**Ground truth:** `parity/fixtures/rw-fontface.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fontface   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font Size  (Home · T0)

**Goal:** make the clone's `Font Size` output match real Microsoft Word.
**Sub-tasks covered:** `fontsize`
**Ground truth:** `parity/fixtures/rw-fontsize.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fontsize   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Italic  (Home · T0)

**Goal:** make the clone's `Italic` output match real Microsoft Word.
**Sub-tasks covered:** `italic`
**Ground truth:** `parity/fixtures/rw-italic.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only italic   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Underline  (Home · T0)

**Goal:** make the clone's `Underline` output match real Microsoft Word.
**Sub-tasks covered:** `underline`
**Ground truth:** `parity/fixtures/rw-underline.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only underline   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font Color  (Home · T1)

**Goal:** make the clone's `Font Color` output match real Microsoft Word.
**Sub-tasks covered:** `fontcolor`
**Ground truth:** `parity/fixtures/rw-fontcolor.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fontcolor   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Insert Table  (Insert · T1)

**Goal:** make the clone's `Insert Table` output match real Microsoft Word.
**Sub-tasks covered:** `table`
**Ground truth:** `parity/fixtures/rw-table.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (table): emit `body:gridCol[('w', '3116')]`
- FR (table): emit `body:gridCol[('w', '3117')]`
- FR (table): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (table): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (table): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (table): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (table): emit `styles:TableGrid:pPr[]`
- FR (table): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (table): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (table): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (table): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only table   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Justify  (Home · T1)

**Goal:** make the clone's `Justify` output match real Microsoft Word.
**Sub-tasks covered:** `justify`
**Ground truth:** `parity/fixtures/rw-justify.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only justify   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Line & Paragraph Spacing  (Home · T1)

**Goal:** make the clone's `Line & Paragraph Spacing` output match real Microsoft Word.
**Sub-tasks covered:** `linespacing`
**Ground truth:** `parity/fixtures/rw-linespacing.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only linespacing   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Numbering  (Home · T1)

**Goal:** make the clone's `Numbering` output match real Microsoft Word.
**Sub-tasks covered:** `numbering`
**Ground truth:** `parity/fixtures/rw-numbering.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Structural requirements
- STR (numbering): `numbering` parts — Word=1, clone=0

### Acceptance (regression gate)
```
python parity/engines/run.py --only numbering   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Page Number  (Insert · T1)

**Goal:** make the clone's `Page Number` output match real Microsoft Word.
**Sub-tasks covered:** `pagenum`
**Ground truth:** `parity/fixtures/rw-pagenum.docx`
**Current parity:** GAP — 16 missing node(s), 2 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (pagenum): emit `body:footerReference[('id', 'rId#'), ('type', 'even')]`
- FR (pagenum): emit `body:footerReference[('id', 'rId#'), ('type', 'first')]`
- FR (pagenum): emit `body:headerReference[('id', 'rId#'), ('type', 'default')]`
- FR (pagenum): emit `body:headerReference[('id', 'rId#'), ('type', 'even')]`
- FR (pagenum): emit `body:headerReference[('id', 'rId#'), ('type', 'first')]`
- FR (pagenum): emit `footer:instrText[('space', 'preserve')]|text=PAGE \* MERGEFORMAT`
- FR (pagenum): emit `footer:noProof[]`
- FR (pagenum): emit `footer:pPr[]`
- FR (pagenum): emit `footer:pStyle[('val', 'Footer')]`
- FR (pagenum): emit `footer:p[]`
- FR (pagenum): emit `footer:r[]`
- FR (pagenum): emit `footer:t[]|text=1`
- FR (pagenum): emit `footer:textOrder|text=1`
- FR (pagenum): emit `header:pPr[]`
- FR (pagenum): emit `header:pStyle[('val', 'Header')]`
- FR (pagenum): emit `header:p[]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (pagenum): stop emitting (or justify) `footer:instrText[('space', 'preserve')]|text=PAGE`
- FID (pagenum): stop emitting (or justify) `footer:rPr[]`

### Structural requirements
- STR (pagenum): `header` parts — Word=3, clone=0
- STR (pagenum): `footer` parts — Word=3, clone=1

### Acceptance (regression gate)
```
python parity/engines/run.py --only pagenum   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Text Highlight Color  (Home · T1)

**Goal:** make the clone's `Text Highlight Color` output match real Microsoft Word.
**Sub-tasks covered:** `highlight`
**Ground truth:** `parity/fixtures/rw-highlight.docx`
**Current parity:** GAP — 3 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (highlight): emit `body:highlight[('val', 'yellow')]`
- FR (highlight): emit `body:pPr[]`
- FR (highlight): emit `body:rPr[]`

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only highlight   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Alignment: Align Bottom Right (caret cell)  (Tables · TB)

**Goal:** make the clone's `Alignment: Align Bottom Right (caret cell)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-cellalign-bottomright`
**Ground truth:** `parity/fixtures/rw-tb-cellalign-bottomright.docx`
**Current parity:** GAP — 10 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-cellalign-bottomright): emit `body:gridCol[('w', '3116')]`
- FR (tb-cellalign-bottomright): emit `body:gridCol[('w', '3117')]`
- FR (tb-cellalign-bottomright): emit `body:jc[('val', 'right')]`
- FR (tb-cellalign-bottomright): emit `body:pPr[]`
- FR (tb-cellalign-bottomright): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-cellalign-bottomright): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-cellalign-bottomright): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-cellalign-bottomright): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-cellalign-bottomright): emit `styles:TableGrid:pPr[]`
- FR (tb-cellalign-bottomright): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-cellalign-bottomright): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-cellalign-bottomright): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-cellalign-bottomright): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-cellalign-bottomright   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## AutoFit: AutoFit Contents  (Tables · TB)

**Goal:** make the clone's `AutoFit: AutoFit Contents` output match real Microsoft Word.
**Sub-tasks covered:** `tb-autofit-contents`
**Ground truth:** `parity/fixtures/rw-tb-autofit-contents.docx`
**Current parity:** GAP — 6 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-autofit-contents): emit `body:gridCol[('w', '222')]`
- FR (tb-autofit-contents): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-autofit-contents): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-autofit-contents): emit `body:tcW[('type', 'auto'), ('w', '0')]`
- FR (tb-autofit-contents): emit `styles:TableGrid:pPr[]`
- FR (tb-autofit-contents): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-autofit-contents): stop emitting (or justify) `body:gridCol[('w', '240')]`
- FID (tb-autofit-contents): stop emitting (or justify) `body:tblLayout[('type', 'autofit')]`
- FID (tb-autofit-contents): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-autofit-contents): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '240')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-autofit-contents   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## AutoFit: AutoFit Window  (Tables · TB)

**Goal:** make the clone's `AutoFit: AutoFit Window` output match real Microsoft Word.
**Sub-tasks covered:** `tb-autofit-window`
**Ground truth:** `parity/fixtures/rw-tb-autofit-window.docx`
**Current parity:** GAP — 7 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-autofit-window): emit `body:gridCol[('w', '3116')]`
- FR (tb-autofit-window): emit `body:gridCol[('w', '3117')]`
- FR (tb-autofit-window): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-autofit-window): emit `body:tcW[('type', 'pct'), ('w', '1666')]`
- FR (tb-autofit-window): emit `body:tcW[('type', 'pct'), ('w', '1667')]`
- FR (tb-autofit-window): emit `styles:TableGrid:pPr[]`
- FR (tb-autofit-window): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-autofit-window): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-autofit-window): stop emitting (or justify) `body:tblLayout[('type', 'autofit')]`
- FID (tb-autofit-window): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-autofit-window): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-autofit-window   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## AutoFit: Fixed Column Width  (Tables · TB)

**Goal:** make the clone's `AutoFit: Fixed Column Width` output match real Microsoft Word.
**Sub-tasks covered:** `tb-autofit-fixed`
**Ground truth:** `parity/fixtures/rw-tb-autofit-fixed.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-autofit-fixed): emit `body:gridCol[('w', '3116')]`
- FR (tb-autofit-fixed): emit `body:gridCol[('w', '3117')]`
- FR (tb-autofit-fixed): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-autofit-fixed): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-autofit-fixed): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-autofit-fixed): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-autofit-fixed): emit `styles:TableGrid:pPr[]`
- FR (tb-autofit-fixed): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-autofit-fixed): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-autofit-fixed): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-autofit-fixed): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-autofit-fixed   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Border pen color red (top edge)  (Tables · TB)

**Goal:** make the clone's `Border pen color red (top edge)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-border-color-red`
**Ground truth:** `parity/fixtures/rw-tb-border-color-red.docx`
**Current parity:** GAP — 10 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-border-color-red): emit `body:gridCol[('w', '3116')]`
- FR (tb-border-color-red): emit `body:gridCol[('w', '3117')]`
- FR (tb-border-color-red): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-border-color-red): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-border-color-red): emit `body:tcBorders[]`
- FR (tb-border-color-red): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-border-color-red): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-border-color-red): emit `body:top[('color', 'FF0000'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FR (tb-border-color-red): emit `styles:TableGrid:pPr[]`
- FR (tb-border-color-red): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-border-color-red): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-border-color-red): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-border-color-red): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-border-color-red   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Border pen weight 3pt (top edge)  (Tables · TB)

**Goal:** make the clone's `Border pen weight 3pt (top edge)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-border-weight-3pt`
**Ground truth:** `parity/fixtures/rw-tb-border-weight-3pt.docx`
**Current parity:** GAP — 10 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-border-weight-3pt): emit `body:gridCol[('w', '3116')]`
- FR (tb-border-weight-3pt): emit `body:gridCol[('w', '3117')]`
- FR (tb-border-weight-3pt): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-border-weight-3pt): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-border-weight-3pt): emit `body:tcBorders[]`
- FR (tb-border-weight-3pt): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-border-weight-3pt): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-border-weight-3pt): emit `body:top[('color', 'auto'), ('space', '0'), ('sz', '24'), ('val', 'single')]`
- FR (tb-border-weight-3pt): emit `styles:TableGrid:pPr[]`
- FR (tb-border-weight-3pt): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-border-weight-3pt): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-border-weight-3pt): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-border-weight-3pt): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-border-weight-3pt   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Borders: All Borders on caret cell  (Tables · TB)

**Goal:** make the clone's `Borders: All Borders on caret cell` output match real Microsoft Word.
**Sub-tasks covered:** `tb-borders-all-cell`
**Ground truth:** `parity/fixtures/rw-tb-borders-all-cell.docx`
**Current parity:** GAP — 8 missing node(s), 8 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-borders-all-cell): emit `body:gridCol[('w', '3116')]`
- FR (tb-borders-all-cell): emit `body:gridCol[('w', '3117')]`
- FR (tb-borders-all-cell): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-borders-all-cell): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-borders-all-cell): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-borders-all-cell): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-borders-all-cell): emit `styles:TableGrid:pPr[]`
- FR (tb-borders-all-cell): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-borders-all-cell): stop emitting (or justify) `body:bottom[('color', '000000'), ('space', '0'), ('sz', '24'), ('val', 'single')]`
- FID (tb-borders-all-cell): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-borders-all-cell): stop emitting (or justify) `body:left[('color', '000000'), ('space', '0'), ('sz', '24'), ('val', 'single')]`
- FID (tb-borders-all-cell): stop emitting (or justify) `body:right[('color', '000000'), ('space', '0'), ('sz', '24'), ('val', 'single')]`
- FID (tb-borders-all-cell): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-borders-all-cell): stop emitting (or justify) `body:tcBorders[]`
- FID (tb-borders-all-cell): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-borders-all-cell): stop emitting (or justify) `body:top[('color', '000000'), ('space', '0'), ('sz', '24'), ('val', 'single')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-borders-all-cell   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Borders: Diagonal Down (cell 2,2)  (Tables · TB)

**Goal:** make the clone's `Borders: Diagonal Down (cell 2,2)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-border-diagdown-cell`
**Ground truth:** `parity/fixtures/rw-tb-border-diagdown-cell.docx`
**Current parity:** GAP — 11 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-border-diagdown-cell): emit `body:bottom[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FR (tb-border-diagdown-cell): emit `body:gridCol[('w', '3116')]`
- FR (tb-border-diagdown-cell): emit `body:gridCol[('w', '3117')]`
- FR (tb-border-diagdown-cell): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-border-diagdown-cell): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-border-diagdown-cell): emit `body:tcBorders[]`
- FR (tb-border-diagdown-cell): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-border-diagdown-cell): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-border-diagdown-cell): emit `body:tl2br[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FR (tb-border-diagdown-cell): emit `styles:TableGrid:pPr[]`
- FR (tb-border-diagdown-cell): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-border-diagdown-cell): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-border-diagdown-cell): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-border-diagdown-cell): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-border-diagdown-cell   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Borders: No Border on caret cell  (Tables · TB)

**Goal:** make the clone's `Borders: No Border on caret cell` output match real Microsoft Word.
**Sub-tasks covered:** `tb-borders-none-cell`
**Ground truth:** `parity/fixtures/rw-tb-borders-none-cell.docx`
**Current parity:** GAP — 13 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-borders-none-cell): emit `body:bottom[('val', 'nil')]`
- FR (tb-borders-none-cell): emit `body:gridCol[('w', '3116')]`
- FR (tb-borders-none-cell): emit `body:gridCol[('w', '3117')]`
- FR (tb-borders-none-cell): emit `body:left[('val', 'nil')]`
- FR (tb-borders-none-cell): emit `body:right[('val', 'nil')]`
- FR (tb-borders-none-cell): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-borders-none-cell): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-borders-none-cell): emit `body:tcBorders[]`
- FR (tb-borders-none-cell): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-borders-none-cell): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-borders-none-cell): emit `body:top[('val', 'nil')]`
- FR (tb-borders-none-cell): emit `styles:TableGrid:pPr[]`
- FR (tb-borders-none-cell): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-borders-none-cell): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-borders-none-cell): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-borders-none-cell): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-borders-none-cell   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Borders: Top Border only (caret cell)  (Tables · TB)

**Goal:** make the clone's `Borders: Top Border only (caret cell)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-border-top-cell`
**Ground truth:** `parity/fixtures/rw-tb-border-top-cell.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-border-top-cell): emit `body:gridCol[('w', '3116')]`
- FR (tb-border-top-cell): emit `body:gridCol[('w', '3117')]`
- FR (tb-border-top-cell): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-border-top-cell): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-border-top-cell): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-border-top-cell): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-border-top-cell): emit `styles:TableGrid:pPr[]`
- FR (tb-border-top-cell): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-border-top-cell): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-border-top-cell): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-border-top-cell): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-border-top-cell   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## COMBO: diagonal border on a merged cell  (Tables · TB)

**Goal:** make the clone's `COMBO: diagonal border on a merged cell` output match real Microsoft Word.
**Sub-tasks covered:** `tb-combo-diag-merged`
**Ground truth:** `parity/fixtures/rw-tb-combo-diag-merged.docx`
**Current parity:** GAP — 11 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-combo-diag-merged): emit `body:gridCol[('w', '3116')]`
- FR (tb-combo-diag-merged): emit `body:gridCol[('w', '3117')]`
- FR (tb-combo-diag-merged): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-combo-diag-merged): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-combo-diag-merged): emit `body:tcBorders[]`
- FR (tb-combo-diag-merged): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-combo-diag-merged): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-combo-diag-merged): emit `body:tcW[('type', 'dxa'), ('w', '6233')]`
- FR (tb-combo-diag-merged): emit `body:tl2br[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FR (tb-combo-diag-merged): emit `styles:TableGrid:pPr[]`
- FR (tb-combo-diag-merged): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-combo-diag-merged): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-combo-diag-merged): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-combo-diag-merged): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-combo-diag-merged): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '6240')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-combo-diag-merged   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Cell Margins 0.25in all sides  (Tables · TB)

**Goal:** make the clone's `Cell Margins 0.25in all sides` output match real Microsoft Word.
**Sub-tasks covered:** `tb-cellmargins`
**Ground truth:** `parity/fixtures/rw-tb-cellmargins.docx`
**Current parity:** GAP — 9 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-cellmargins): emit `body:gridCol[('w', '3116')]`
- FR (tb-cellmargins): emit `body:gridCol[('w', '3117')]`
- FR (tb-cellmargins): emit `body:tblCellMar[]`
- FR (tb-cellmargins): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-cellmargins): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-cellmargins): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-cellmargins): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-cellmargins): emit `styles:TableGrid:pPr[]`
- FR (tb-cellmargins): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-cellmargins): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-cellmargins): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-cellmargins): stop emitting (or justify) `body:tcMar[]`
- FID (tb-cellmargins): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-cellmargins   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Column Width 1.5 inch (caret column)  (Tables · TB)

**Goal:** make the clone's `Column Width 1.5 inch (caret column)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-colwidth-15in`
**Ground truth:** `parity/fixtures/rw-tb-colwidth-15in.docx`
**Current parity:** GAP — 6 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-colwidth-15in): emit `body:gridCol[('w', '3117')]`
- FR (tb-colwidth-15in): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-colwidth-15in): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-colwidth-15in): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-colwidth-15in): emit `styles:TableGrid:pPr[]`
- FR (tb-colwidth-15in): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-colwidth-15in): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-colwidth-15in): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-colwidth-15in): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-colwidth-15in   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Convert Text to Table (commas)  (Tables · TB)

**Goal:** make the clone's `Convert Text to Table (commas)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-convert-text-table`
**Ground truth:** `parity/fixtures/rw-tb-convert-text-table.docx`
**Current parity:** GAP — 8 missing node(s), 14 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-convert-text-table): emit `body:bottom[('type', 'dxa'), ('w', '0')]`
- FR (tb-convert-text-table): emit `body:p[]`
- FR (tb-convert-text-table): emit `body:tblCellMar[]`
- FR (tb-convert-text-table): emit `body:tblLayout[('type', 'fixed')]`
- FR (tb-convert-text-table): emit `body:tblLook[('firstColumn', '0'), ('firstRow', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '0'), ('val', '0000')]`
- FR (tb-convert-text-table): emit `body:tblPrEx[]`
- FR (tb-convert-text-table): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-convert-text-table): emit `body:top[('type', 'dxa'), ('w', '0')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-convert-text-table): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-convert-text-table): stop emitting (or justify) `body:tblStyle[('val', 'TableGrid')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:@type=table`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:basedOn[('val', 'TableNormal')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:bottom[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:insideH[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:insideV[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:left[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:name[('val', 'Table Grid')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:right[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:tblBorders[]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:tblPr[]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:top[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-convert-text-table): stop emitting (or justify) `styles:TableGrid:uiPriority[('val', '39')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-convert-text-table   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Convert to Text (commas)  (Tables · TB)

**Goal:** make the clone's `Convert to Text (commas)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-totext-comma`
**Ground truth:** `parity/fixtures/rw-tb-totext-comma.docx`
**Current parity:** GAP — 3 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-totext-comma): emit `body:t[('space', 'preserve')]|text=, ,`
- FR (tb-totext-comma): emit `body:t[('space', 'preserve')]|text=a, b,`
- FR (tb-totext-comma): emit `body:textOrder|text=a, b,↵, ,↵, ,`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-totext-comma): stop emitting (or justify) `body:t[('space', 'preserve')]|text=`
- FID (tb-totext-comma): stop emitting (or justify) `body:t[('space', 'preserve')]|text=a b`
- FID (tb-totext-comma): stop emitting (or justify) `body:textOrder|text=a b`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-totext-comma   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Convert to Text (tabs)  (Tables · TB)

**Goal:** make the clone's `Convert to Text (tabs)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-totext-tab`
**Ground truth:** `parity/fixtures/rw-tb-totext-tab.docx`
**Current parity:** GAP — 10 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-totext-tab): emit `body:ind[('left', '113')]`
- FR (tb-totext-tab): emit `body:pPr[]`
- FR (tb-totext-tab): emit `body:r[]`
- FR (tb-totext-tab): emit `body:t[]|text=a`
- FR (tb-totext-tab): emit `body:t[]|text=b`
- FR (tb-totext-tab): emit `body:tab[('pos', '3229'), ('val', 'left')]`
- FR (tb-totext-tab): emit `body:tab[('pos', '6346'), ('val', 'left')]`
- FR (tb-totext-tab): emit `body:tab[]`
- FR (tb-totext-tab): emit `body:tabs[]`
- FR (tb-totext-tab): emit `body:textOrder|text=a↵b`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-totext-tab): stop emitting (or justify) `body:t[('space', 'preserve')]|text=`
- FID (tb-totext-tab): stop emitting (or justify) `body:t[('space', 'preserve')]|text=a b`
- FID (tb-totext-tab): stop emitting (or justify) `body:textOrder|text=a b`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-totext-tab   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Delete Cells: shift cells up (cell 2,2)  (Tables · TB)

**Goal:** make the clone's `Delete Cells: shift cells up (cell 2,2)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-delete-cells-up`
**Ground truth:** `parity/fixtures/rw-tb-delete-cells-up.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-delete-cells-up): emit `body:gridCol[('w', '3116')]`
- FR (tb-delete-cells-up): emit `body:gridCol[('w', '3117')]`
- FR (tb-delete-cells-up): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-delete-cells-up): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-delete-cells-up): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-delete-cells-up): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-delete-cells-up): emit `styles:TableGrid:pPr[]`
- FR (tb-delete-cells-up): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-delete-cells-up): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-delete-cells-up): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-delete-cells-up): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-delete-cells-up   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Delete Column (col 1)  (Tables · TB)

**Goal:** make the clone's `Delete Column (col 1)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-delete-col`
**Ground truth:** `parity/fixtures/rw-tb-delete-col.docx`
**Current parity:** GAP — 6 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-delete-col): emit `body:gridCol[('w', '3117')]`
- FR (tb-delete-col): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-delete-col): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-delete-col): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-delete-col): emit `styles:TableGrid:pPr[]`
- FR (tb-delete-col): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-delete-col): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-delete-col): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-delete-col): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-delete-col   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Delete Row (row 1)  (Tables · TB)

**Goal:** make the clone's `Delete Row (row 1)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-delete-row`
**Ground truth:** `parity/fixtures/rw-tb-delete-row.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-delete-row): emit `body:gridCol[('w', '3116')]`
- FR (tb-delete-row): emit `body:gridCol[('w', '3117')]`
- FR (tb-delete-row): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-delete-row): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-delete-row): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-delete-row): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-delete-row): emit `styles:TableGrid:pPr[]`
- FR (tb-delete-row): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-delete-row): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-delete-row): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-delete-row): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-delete-row   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Delete Table  (Tables · TB)

**Goal:** make the clone's `Delete Table` output match real Microsoft Word.
**Sub-tasks covered:** `tb-delete-table`
**Ground truth:** `parity/fixtures/rw-tb-delete-table.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-delete-table   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Distribute Columns  (Tables · TB)

**Goal:** make the clone's `Distribute Columns` output match real Microsoft Word.
**Sub-tasks covered:** `tb-dist-cols`
**Ground truth:** `parity/fixtures/rw-tb-dist-cols.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-dist-cols): emit `body:gridCol[('w', '3116')]`
- FR (tb-dist-cols): emit `body:gridCol[('w', '3117')]`
- FR (tb-dist-cols): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-dist-cols): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-dist-cols): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-dist-cols): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-dist-cols): emit `styles:TableGrid:pPr[]`
- FR (tb-dist-cols): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-dist-cols): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-dist-cols): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-dist-cols): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-dist-cols   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Distribute Rows  (Tables · TB)

**Goal:** make the clone's `Distribute Rows` output match real Microsoft Word.
**Sub-tasks covered:** `tb-dist-rows`
**Ground truth:** `parity/fixtures/rw-tb-dist-rows.docx`
**Current parity:** GAP — 9 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-dist-rows): emit `body:gridCol[('w', '3116')]`
- FR (tb-dist-rows): emit `body:gridCol[('w', '3117')]`
- FR (tb-dist-rows): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-dist-rows): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-dist-rows): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-dist-rows): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-dist-rows): emit `body:trHeight[('val', '293')]`
- FR (tb-dist-rows): emit `styles:TableGrid:pPr[]`
- FR (tb-dist-rows): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-dist-rows): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-dist-rows): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-dist-rows): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-dist-rows): stop emitting (or justify) `body:trHeight[('hRule', 'atLeast'), ('val', '360')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-dist-rows   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Find/Replace: Replace All (Revenue->Income)  (Home · RD)

**Goal:** make the clone's `Find/Replace: Replace All (Revenue->Income)` output match real Microsoft Word.
**Sub-tasks covered:** `fd-replace-all`
**Ground truth:** `parity/fixtures/rw-fd-replace-all.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-replace-all   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Floating table: text wrapping Around  (Tables · TB)

**Goal:** make the clone's `Floating table: text wrapping Around` output match real Microsoft Word.
**Sub-tasks covered:** `tb-float-around`
**Ground truth:** `parity/fixtures/rw-tb-float-around.docx`
**Current parity:** GAP — 10 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-float-around): emit `body:gridCol[('w', '3116')]`
- FR (tb-float-around): emit `body:gridCol[('w', '3117')]`
- FR (tb-float-around): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-float-around): emit `body:tblOverlap[('val', 'never')]`
- FR (tb-float-around): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-float-around): emit `body:tblpPr[('leftFromText', '180'), ('rightFromText', '180'), ('tblpY', '1'), ('vertAnchor', 'text')]`
- FR (tb-float-around): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-float-around): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-float-around): emit `styles:TableGrid:pPr[]`
- FR (tb-float-around): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-float-around): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-float-around): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-float-around): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-float-around   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font color: THEME color (Accent 1)  (Home · CD)

**Goal:** make the clone's `Font color: THEME color (Accent 1)` output match real Microsoft Word.
**Sub-tasks covered:** `fd-fontcolor-theme`
**Ground truth:** `parity/fixtures/rw-fd-fontcolor-theme.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-fontcolor-theme   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font color: custom RGB (More Colors)  (Home · CD)

**Goal:** make the clone's `Font color: custom RGB (More Colors)` output match real Microsoft Word.
**Sub-tasks covered:** `fd-fontcolor-custom`
**Ground truth:** `parity/fixtures/rw-fd-fontcolor-custom.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-fontcolor-custom   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog (Advanced): Character position  (Home · FD)

**Goal:** make the clone's `Font dialog (Advanced): Character position` output match real Microsoft Word.
**Sub-tasks covered:** `fd-position`
**Ground truth:** `parity/fixtures/rw-fd-position.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-position   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog (Advanced): Character scale  (Home · FD)

**Goal:** make the clone's `Font dialog (Advanced): Character scale` output match real Microsoft Word.
**Sub-tasks covered:** `fd-scale`
**Ground truth:** `parity/fixtures/rw-fd-scale.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-scale   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog (Advanced): Character spacing  (Home · FD)

**Goal:** make the clone's `Font dialog (Advanced): Character spacing` output match real Microsoft Word.
**Sub-tasks covered:** `fd-spacing`
**Ground truth:** `parity/fixtures/rw-fd-spacing.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-spacing   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog (Advanced): Kerning >= 8pt  (Home · G3)

**Goal:** make the clone's `Font dialog (Advanced): Kerning >= 8pt` output match real Microsoft Word.
**Sub-tasks covered:** `fd-kerning`
**Ground truth:** `parity/fixtures/rw-fd-kerning.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-kerning   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog (Advanced): Ligatures (OpenType)  (Home · FD)

**Goal:** make the clone's `Font dialog (Advanced): Ligatures (OpenType)` output match real Microsoft Word.
**Sub-tasks covered:** `fd-ligatures`
**Ground truth:** `parity/fixtures/rw-fd-ligatures.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-ligatures   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: All caps  (Home · FD)

**Goal:** make the clone's `Font dialog: All caps` output match real Microsoft Word.
**Sub-tasks covered:** `fd-allcaps`
**Ground truth:** `parity/fixtures/rw-fd-allcaps.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-allcaps   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: Double strikethrough  (Home · G3)

**Goal:** make the clone's `Font dialog: Double strikethrough` output match real Microsoft Word.
**Sub-tasks covered:** `fd-double-strike`
**Ground truth:** `parity/fixtures/rw-fd-double-strike.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-double-strike   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: Hidden  (Home · G3)

**Goal:** make the clone's `Font dialog: Hidden` output match real Microsoft Word.
**Sub-tasks covered:** `fd-hidden`
**Ground truth:** `parity/fixtures/rw-fd-hidden.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-hidden   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: Small caps  (Home · FD)

**Goal:** make the clone's `Font dialog: Small caps` output match real Microsoft Word.
**Sub-tasks covered:** `fd-smallcaps`
**Ground truth:** `parity/fixtures/rw-fd-smallcaps.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-smallcaps   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: Strikethrough  (Home · FD)

**Goal:** make the clone's `Font dialog: Strikethrough` output match real Microsoft Word.
**Sub-tasks covered:** `fd-strike`
**Ground truth:** `parity/fixtures/rw-fd-strike.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-strike   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: Subscript  (Home · FD)

**Goal:** make the clone's `Font dialog: Subscript` output match real Microsoft Word.
**Sub-tasks covered:** `fd-subscript`
**Ground truth:** `parity/fixtures/rw-fd-subscript.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-subscript   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: Superscript  (Home · FD)

**Goal:** make the clone's `Font dialog: Superscript` output match real Microsoft Word.
**Sub-tasks covered:** `fd-superscript`
**Ground truth:** `parity/fixtures/rw-fd-superscript.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-superscript   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font dialog: Underline color  (Home · FD)

**Goal:** make the clone's `Font dialog: Underline color` output match real Microsoft Word.
**Sub-tasks covered:** `fd-underline-color`
**Ground truth:** `parity/fixtures/rw-fd-underline-color.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-underline-color   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font size 10.5  (Home · TV)

**Goal:** make the clone's `Font size 10.5` output match real Microsoft Word.
**Sub-tasks covered:** `sz-10p5`
**Ground truth:** `parity/fixtures/rw-sz-10p5.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only sz-10p5   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font size 72  (Home · TV)

**Goal:** make the clone's `Font size 72` output match real Microsoft Word.
**Sub-tasks covered:** `sz-72`
**Ground truth:** `parity/fixtures/rw-sz-72.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only sz-72   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Font size 8  (Home · TV)

**Goal:** make the clone's `Font size 8` output match real Microsoft Word.
**Sub-tasks covered:** `sz-8`
**Ground truth:** `parity/fixtures/rw-sz-8.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only sz-8   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Insert Cells: shift cells right  (Tables · TB)

**Goal:** make the clone's `Insert Cells: shift cells right` output match real Microsoft Word.
**Sub-tasks covered:** `tb-insert-cells-right`
**Ground truth:** `parity/fixtures/rw-tb-insert-cells-right.docx`
**Current parity:** GAP — 14 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-insert-cells-right): emit `body:gridAfter[('val', '1')]`
- FR (tb-insert-cells-right): emit `body:gridCol[('w', '3115')]`
- FR (tb-insert-cells-right): emit `body:gridCol[('w', '3117')]`
- FR (tb-insert-cells-right): emit `body:p[]`
- FR (tb-insert-cells-right): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-insert-cells-right): emit `body:tblW[('type', 'dxa'), ('w', '12466')]`
- FR (tb-insert-cells-right): emit `body:tcPr[]`
- FR (tb-insert-cells-right): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-insert-cells-right): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-insert-cells-right): emit `body:tc[]`
- FR (tb-insert-cells-right): emit `body:trPr[]`
- FR (tb-insert-cells-right): emit `body:wAfter[('type', 'dxa'), ('w', '3116')]`
- FR (tb-insert-cells-right): emit `styles:TableGrid:pPr[]`
- FR (tb-insert-cells-right): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-insert-cells-right): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-insert-cells-right): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-insert-cells-right): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-insert-cells-right   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Insert Hyperlink (text + address)  (Insert · ID)

**Goal:** make the clone's `Insert Hyperlink (text + address)` output match real Microsoft Word.
**Sub-tasks covered:** `fd-link`
**Ground truth:** `parity/fixtures/rw-fd-link.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-link   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Insert Table dialog: 3x4, fixed width  (Tables · TB)

**Goal:** make the clone's `Insert Table dialog: 3x4, fixed width` output match real Microsoft Word.
**Sub-tasks covered:** `tb-insert-dialog`
**Ground truth:** `parity/fixtures/rw-tb-insert-dialog.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-insert-dialog): emit `body:gridCol[('w', '2337')]`
- FR (tb-insert-dialog): emit `body:gridCol[('w', '2338')]`
- FR (tb-insert-dialog): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-insert-dialog): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-insert-dialog): emit `body:tcW[('type', 'dxa'), ('w', '2337')]`
- FR (tb-insert-dialog): emit `body:tcW[('type', 'dxa'), ('w', '2338')]`
- FR (tb-insert-dialog): emit `styles:TableGrid:pPr[]`
- FR (tb-insert-dialog): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-insert-dialog): stop emitting (or justify) `body:gridCol[('w', '2340')]`
- FID (tb-insert-dialog): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-insert-dialog): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '2340')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-insert-dialog   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Line spacing 1.0  (Home · TV)

**Goal:** make the clone's `Line spacing 1.0` output match real Microsoft Word.
**Sub-tasks covered:** `ls-1p0`
**Ground truth:** `parity/fixtures/rw-ls-1p0.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ls-1p0   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Line spacing 1.5  (Home · TV)

**Goal:** make the clone's `Line spacing 1.5` output match real Microsoft Word.
**Sub-tasks covered:** `ls-1p5`
**Ground truth:** `parity/fixtures/rw-ls-1p5.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ls-1p5   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Merge Cells: first two cells of row 1  (Tables · TB)

**Goal:** make the clone's `Merge Cells: first two cells of row 1` output match real Microsoft Word.
**Sub-tasks covered:** `tb-merge-firstrow2`
**Ground truth:** `parity/fixtures/rw-tb-merge-firstrow2.docx`
**Current parity:** GAP — 9 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-merge-firstrow2): emit `body:gridCol[('w', '3116')]`
- FR (tb-merge-firstrow2): emit `body:gridCol[('w', '3117')]`
- FR (tb-merge-firstrow2): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-merge-firstrow2): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-merge-firstrow2): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-merge-firstrow2): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-merge-firstrow2): emit `body:tcW[('type', 'dxa'), ('w', '6233')]`
- FR (tb-merge-firstrow2): emit `styles:TableGrid:pPr[]`
- FR (tb-merge-firstrow2): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-merge-firstrow2): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-merge-firstrow2): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-merge-firstrow2): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-merge-firstrow2): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '6240')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-merge-firstrow2   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Page Setup: Left margin 1.5in  (Insert · ID)

**Goal:** make the clone's `Page Setup: Left margin 1.5in` output match real Microsoft Word.
**Sub-tasks covered:** `fd-margin-left`
**Ground truth:** `parity/fixtures/rw-fd-margin-left.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-margin-left   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Page Setup: Top margin 1.25in  (Insert · ID)

**Goal:** make the clone's `Page Setup: Top margin 1.25in` output match real Microsoft Word.
**Sub-tasks covered:** `fd-margin-top`
**Ground truth:** `parity/fixtures/rw-fd-margin-top.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-margin-top   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: First-line indent  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: First-line indent` output match real Microsoft Word.
**Sub-tasks covered:** `fd-indent-firstline`
**Ground truth:** `parity/fixtures/rw-fd-indent-firstline.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-indent-firstline   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Hanging indent  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Hanging indent` output match real Microsoft Word.
**Sub-tasks covered:** `fd-indent-hanging`
**Ground truth:** `parity/fixtures/rw-fd-indent-hanging.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-indent-hanging   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Indent left  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Indent left` output match real Microsoft Word.
**Sub-tasks covered:** `fd-indent-left`
**Ground truth:** `parity/fixtures/rw-fd-indent-left.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-indent-left   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Indent right  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Indent right` output match real Microsoft Word.
**Sub-tasks covered:** `fd-indent-right`
**Ground truth:** `parity/fixtures/rw-fd-indent-right.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-indent-right   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Keep lines together  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Keep lines together` output match real Microsoft Word.
**Sub-tasks covered:** `fd-pag-keeplines`
**Ground truth:** `parity/fixtures/rw-fd-pag-keeplines.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-pag-keeplines   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Keep with next  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Keep with next` output match real Microsoft Word.
**Sub-tasks covered:** `fd-pag-keepnext`
**Ground truth:** `parity/fixtures/rw-fd-pag-keepnext.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-pag-keepnext   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Line spacing At least  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Line spacing At least` output match real Microsoft Word.
**Sub-tasks covered:** `fd-ls-atleast`
**Ground truth:** `parity/fixtures/rw-fd-ls-atleast.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-ls-atleast   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Line spacing Exactly  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Line spacing Exactly` output match real Microsoft Word.
**Sub-tasks covered:** `fd-ls-exactly`
**Ground truth:** `parity/fixtures/rw-fd-ls-exactly.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-ls-exactly   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Line spacing Multiple  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Line spacing Multiple` output match real Microsoft Word.
**Sub-tasks covered:** `fd-ls-multiple`
**Ground truth:** `parity/fixtures/rw-fd-ls-multiple.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-ls-multiple   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Page break before  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Page break before` output match real Microsoft Word.
**Sub-tasks covered:** `fd-pag-pagebreak`
**Ground truth:** `parity/fixtures/rw-fd-pag-pagebreak.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-pag-pagebreak   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Spacing after  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Spacing after` output match real Microsoft Word.
**Sub-tasks covered:** `fd-spacing-after`
**Ground truth:** `parity/fixtures/rw-fd-spacing-after.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 2 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- FID (fd-spacing-after): stop emitting (or justify) `body:pPr[]`
- FID (fd-spacing-after): stop emitting (or justify) `body:spacing[('after', '160')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-spacing-after   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Spacing before  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Spacing before` output match real Microsoft Word.
**Sub-tasks covered:** `fd-spacing-before`
**Ground truth:** `parity/fixtures/rw-fd-spacing-before.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-spacing-before   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Paragraph dialog: Widow/Orphan control off  (Home · PD)

**Goal:** make the clone's `Paragraph dialog: Widow/Orphan control off` output match real Microsoft Word.
**Sub-tasks covered:** `fd-pag-widow`
**Ground truth:** `parity/fixtures/rw-fd-pag-widow.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only fd-pag-widow   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Quick Tables: Calendar  (Tables · TB)

**Goal:** make the clone's `Quick Tables: Calendar` output match real Microsoft Word.
**Sub-tasks covered:** `tb-quicktable-calendar`
**Ground truth:** `parity/fixtures/rw-tb-quicktable-calendar.docx`
**Current parity:** GAP — 98 missing node(s), 16 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-quicktable-calendar): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-quicktable-calendar): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-quicktable-calendar): emit `body:cnfStyle[('evenHBand', '1'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000000010000')]`
- FR (tb-quicktable-calendar): emit `body:gridCol[('w', '720')]`
- FR (tb-quicktable-calendar): emit `body:gridSpan[('val', '7')]`
- FR (tb-quicktable-calendar): emit `body:p[]`
- FR (tb-quicktable-calendar): emit `body:r[]`
- FR (tb-quicktable-calendar): emit `body:t[]|text=1`
- FR (tb-quicktable-calendar): emit `body:t[]|text=10`
- FR (tb-quicktable-calendar): emit `body:t[]|text=11`
- FR (tb-quicktable-calendar): emit `body:t[]|text=12`
- FR (tb-quicktable-calendar): emit `body:t[]|text=13`
- FR (tb-quicktable-calendar): emit `body:t[]|text=14`
- FR (tb-quicktable-calendar): emit `body:t[]|text=15`
- FR (tb-quicktable-calendar): emit `body:t[]|text=16`
- FR (tb-quicktable-calendar): emit `body:t[]|text=17`
- FR (tb-quicktable-calendar): emit `body:t[]|text=18`
- FR (tb-quicktable-calendar): emit `body:t[]|text=19`
- FR (tb-quicktable-calendar): emit `body:t[]|text=2`
- FR (tb-quicktable-calendar): emit `body:t[]|text=20`
- FR (tb-quicktable-calendar): emit `body:t[]|text=21`
- FR (tb-quicktable-calendar): emit `body:t[]|text=22`
- FR (tb-quicktable-calendar): emit `body:t[]|text=23`
- FR (tb-quicktable-calendar): emit `body:t[]|text=24`
- FR (tb-quicktable-calendar): emit `body:t[]|text=25`
- FR (tb-quicktable-calendar): emit `body:t[]|text=26`
- FR (tb-quicktable-calendar): emit `body:t[]|text=27`
- FR (tb-quicktable-calendar): emit `body:t[]|text=28`
- FR (tb-quicktable-calendar): emit `body:t[]|text=29`
- FR (tb-quicktable-calendar): emit `body:t[]|text=3`
- FR (tb-quicktable-calendar): emit `body:t[]|text=30`
- FR (tb-quicktable-calendar): emit `body:t[]|text=31`
- FR (tb-quicktable-calendar): emit `body:t[]|text=4`
- FR (tb-quicktable-calendar): emit `body:t[]|text=5`
- FR (tb-quicktable-calendar): emit `body:t[]|text=6`
- FR (tb-quicktable-calendar): emit `body:t[]|text=7`
- FR (tb-quicktable-calendar): emit `body:t[]|text=8`
- FR (tb-quicktable-calendar): emit `body:t[]|text=9`
- FR (tb-quicktable-calendar): emit `body:t[]|text=December`
- FR (tb-quicktable-calendar): emit `body:t[]|text=F`
- FR (tb-quicktable-calendar): emit `body:t[]|text=M`
- FR (tb-quicktable-calendar): emit `body:t[]|text=S`
- FR (tb-quicktable-calendar): emit `body:t[]|text=T`
- FR (tb-quicktable-calendar): emit `body:t[]|text=W`
- FR (tb-quicktable-calendar): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-quicktable-calendar): emit `body:tblStyle[('val', 'Calendar1')]`
- FR (tb-quicktable-calendar): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-quicktable-calendar): emit `body:tcPr[]`
- FR (tb-quicktable-calendar): emit `body:tcW[('type', 'dxa'), ('w', '5040')]`
- FR (tb-quicktable-calendar): emit `body:tcW[('type', 'dxa'), ('w', '720')]`
- FR (tb-quicktable-calendar): emit `body:tc[]`
- FR (tb-quicktable-calendar): emit `body:textOrder|text=December↵M↵T↵W↵T↵F↵S↵S↵1↵2↵3↵4↵5↵6↵7↵8↵9↵10↵11↵12↵13↵14↵15↵16↵17↵18↵19↵20↵21↵22↵23↵24↵25↵26↵27↵28↵29↵30↵31`
- FR (tb-quicktable-calendar): emit `body:trHeight[('val', '630')]`
- FR (tb-quicktable-calendar): emit `body:trHeight[('val', '720')]`
- FR (tb-quicktable-calendar): emit `body:trPr[]`
- FR (tb-quicktable-calendar): emit `body:tr[]`
- FR (tb-quicktable-calendar): emit `body:vAlign[('val', 'bottom')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:@type=table`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:b[]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:basedOn[('val', 'TableNormal')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:bottom[('color', '000000'), ('space', '0'), ('sz', '24'), ('themeColor', 'text1'), ('val', 'single')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:bottom[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:color[('val', 'auto')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:i[('val', '0')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:insideH[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:insideV[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:kern[('val', '0')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:left[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:ligatures[('val', 'none')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:name[('val', 'Calendar 1')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:pPr[]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:qFormat[]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:rFonts[('asciiTheme', 'minorHAnsi'), ('hAnsiTheme', 'minorHAnsi')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:rFonts[('eastAsiaTheme', 'minorEastAsia')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:rPr[]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:right[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:shd[('color', 'auto'), ('fill', 'auto'), ('val', 'clear')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:spacing[('afterAutospacing', '0'), ('afterLines', '0'), ('beforeAutospacing', '0'), ('beforeLines', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:szCs[('val', '22')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:sz[('val', '22')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:sz[('val', '44')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tblPr[]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tblStyleColBandSize[('val', '1')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tblStylePr[('type', 'band1Horz')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tblStylePr[('type', 'band2Horz')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tblStylePr[('type', 'firstRow')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tblStylePr[('type', 'lastRow')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tblStyleRowBandSize[('val', '1')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tcBorders[]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tcPr[]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tl2br[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:top[('color', '000000'), ('space', '0'), ('sz', '24'), ('themeColor', 'text1'), ('val', 'single')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:top[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:tr2bl[('val', 'nil')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:uiPriority[('val', '99')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:vAlign[('val', 'bottom')]`
- FR (tb-quicktable-calendar): emit `styles:Calendar1:wordWrap[]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-quicktable-calendar): stop emitting (or justify) `body:gridCol[('w', '1335')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `body:tblStyle[('val', 'TableGrid')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '1335')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:@type=table`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:basedOn[('val', 'TableNormal')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:bottom[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:insideH[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:insideV[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:left[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:name[('val', 'Table Grid')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:right[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:tblBorders[]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:tblPr[]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:top[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (tb-quicktable-calendar): stop emitting (or justify) `styles:TableGrid:uiPriority[('val', '39')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-quicktable-calendar   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Repeat Header Rows (row 1)  (Tables · TB)

**Goal:** make the clone's `Repeat Header Rows (row 1)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-repeatheader`
**Ground truth:** `parity/fixtures/rw-tb-repeatheader.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-repeatheader): emit `body:gridCol[('w', '3116')]`
- FR (tb-repeatheader): emit `body:gridCol[('w', '3117')]`
- FR (tb-repeatheader): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-repeatheader): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-repeatheader): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-repeatheader): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-repeatheader): emit `styles:TableGrid:pPr[]`
- FR (tb-repeatheader): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-repeatheader): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-repeatheader): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-repeatheader): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-repeatheader   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Row Height 0.5 inch (caret row)  (Tables · TB)

**Goal:** make the clone's `Row Height 0.5 inch (caret row)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-rowheight-05in`
**Ground truth:** `parity/fixtures/rw-tb-rowheight-05in.docx`
**Current parity:** GAP — 9 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-rowheight-05in): emit `body:gridCol[('w', '3116')]`
- FR (tb-rowheight-05in): emit `body:gridCol[('w', '3117')]`
- FR (tb-rowheight-05in): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-rowheight-05in): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-rowheight-05in): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-rowheight-05in): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-rowheight-05in): emit `body:trHeight[('val', '720')]`
- FR (tb-rowheight-05in): emit `styles:TableGrid:pPr[]`
- FR (tb-rowheight-05in): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-rowheight-05in): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-rowheight-05in): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-rowheight-05in): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-rowheight-05in): stop emitting (or justify) `body:trHeight[('hRule', 'atLeast'), ('val', '720')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-rowheight-05in   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Rows & Columns: Insert Above  (Tables · TB)

**Goal:** make the clone's `Rows & Columns: Insert Above` output match real Microsoft Word.
**Sub-tasks covered:** `tb-insert-above`
**Ground truth:** `parity/fixtures/rw-tb-insert-above.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-insert-above): emit `body:gridCol[('w', '3116')]`
- FR (tb-insert-above): emit `body:gridCol[('w', '3117')]`
- FR (tb-insert-above): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-insert-above): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-insert-above): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-insert-above): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-insert-above): emit `styles:TableGrid:pPr[]`
- FR (tb-insert-above): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-insert-above): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-insert-above): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-insert-above): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-insert-above   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Rows & Columns: Insert Below  (Tables · TB)

**Goal:** make the clone's `Rows & Columns: Insert Below` output match real Microsoft Word.
**Sub-tasks covered:** `tb-insert-below`
**Ground truth:** `parity/fixtures/rw-tb-insert-below.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-insert-below): emit `body:gridCol[('w', '3116')]`
- FR (tb-insert-below): emit `body:gridCol[('w', '3117')]`
- FR (tb-insert-below): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-insert-below): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-insert-below): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-insert-below): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-insert-below): emit `styles:TableGrid:pPr[]`
- FR (tb-insert-below): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-insert-below): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-insert-below): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-insert-below): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-insert-below   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Rows & Columns: Insert Left  (Tables · TB)

**Goal:** make the clone's `Rows & Columns: Insert Left` output match real Microsoft Word.
**Sub-tasks covered:** `tb-insert-left`
**Ground truth:** `parity/fixtures/rw-tb-insert-left.docx`
**Current parity:** GAP — 8 missing node(s), 5 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-insert-left): emit `body:gridCol[('w', '2337')]`
- FR (tb-insert-left): emit `body:gridCol[('w', '2338')]`
- FR (tb-insert-left): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-insert-left): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-insert-left): emit `body:tcW[('type', 'dxa'), ('w', '2337')]`
- FR (tb-insert-left): emit `body:tcW[('type', 'dxa'), ('w', '2338')]`
- FR (tb-insert-left): emit `styles:TableGrid:pPr[]`
- FR (tb-insert-left): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-insert-left): stop emitting (or justify) `body:gridCol[('w', '1500')]`
- FID (tb-insert-left): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-insert-left): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-insert-left): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '1500')]`
- FID (tb-insert-left): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-insert-left   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Rows & Columns: Insert Right  (Tables · TB)

**Goal:** make the clone's `Rows & Columns: Insert Right` output match real Microsoft Word.
**Sub-tasks covered:** `tb-insert-right`
**Ground truth:** `parity/fixtures/rw-tb-insert-right.docx`
**Current parity:** GAP — 8 missing node(s), 5 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-insert-right): emit `body:gridCol[('w', '2336')]`
- FR (tb-insert-right): emit `body:gridCol[('w', '2338')]`
- FR (tb-insert-right): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-insert-right): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-insert-right): emit `body:tcW[('type', 'dxa'), ('w', '2336')]`
- FR (tb-insert-right): emit `body:tcW[('type', 'dxa'), ('w', '2338')]`
- FR (tb-insert-right): emit `styles:TableGrid:pPr[]`
- FR (tb-insert-right): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-insert-right): stop emitting (or justify) `body:gridCol[('w', '1500')]`
- FID (tb-insert-right): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-insert-right): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-insert-right): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '1500')]`
- FID (tb-insert-right): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-insert-right   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Shading: fill caret cell #FFF2CC  (Tables · TB)

**Goal:** make the clone's `Shading: fill caret cell #FFF2CC` output match real Microsoft Word.
**Sub-tasks covered:** `tb-shading-cell`
**Ground truth:** `parity/fixtures/rw-tb-shading-cell.docx`
**Current parity:** GAP — 9 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-shading-cell): emit `body:gridCol[('w', '3116')]`
- FR (tb-shading-cell): emit `body:gridCol[('w', '3117')]`
- FR (tb-shading-cell): emit `body:shd[('color', 'auto'), ('fill', 'FFF2CC'), ('val', 'clear')]`
- FR (tb-shading-cell): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-shading-cell): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-shading-cell): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-shading-cell): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-shading-cell): emit `styles:TableGrid:pPr[]`
- FR (tb-shading-cell): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-shading-cell): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-shading-cell): stop emitting (or justify) `body:shd[('fill', 'FFF2CC')]`
- FID (tb-shading-cell): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-shading-cell): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-shading-cell   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Sort: table rows by column 1 ascending  (Tables · TB)

**Goal:** make the clone's `Sort: table rows by column 1 ascending` output match real Microsoft Word.
**Sub-tasks covered:** `tb-sort-col1`
**Ground truth:** `parity/fixtures/rw-tb-sort-col1.docx`
**Current parity:** GAP — 9 missing node(s), 4 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-sort-col1): emit `body:gridCol[('w', '3116')]`
- FR (tb-sort-col1): emit `body:gridCol[('w', '3117')]`
- FR (tb-sort-col1): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-sort-col1): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-sort-col1): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-sort-col1): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-sort-col1): emit `body:textOrder|text=c↵a↵b`
- FR (tb-sort-col1): emit `styles:TableGrid:pPr[]`
- FR (tb-sort-col1): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-sort-col1): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-sort-col1): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-sort-col1): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-sort-col1): stop emitting (or justify) `body:textOrder|text=c↵b↵a`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-sort-col1   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Split Cells: 1 unmerged cell into 2 columns  (Tables · TB)

**Goal:** make the clone's `Split Cells: 1 unmerged cell into 2 columns` output match real Microsoft Word.
**Sub-tasks covered:** `tb-split-cell`
**Ground truth:** `parity/fixtures/rw-tb-split-cell.docx`
**Current parity:** GAP — 9 missing node(s), 5 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-split-cell): emit `body:gridCol[('w', '1558')]`
- FR (tb-split-cell): emit `body:gridCol[('w', '3117')]`
- FR (tb-split-cell): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-split-cell): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-split-cell): emit `body:tcW[('type', 'dxa'), ('w', '1558')]`
- FR (tb-split-cell): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-split-cell): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-split-cell): emit `styles:TableGrid:pPr[]`
- FR (tb-split-cell): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-split-cell): stop emitting (or justify) `body:gridCol[('w', '1560')]`
- FID (tb-split-cell): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-split-cell): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-split-cell): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '1560')]`
- FID (tb-split-cell): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-split-cell   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Split Table at row 2  (Tables · TB)

**Goal:** make the clone's `Split Table at row 2` output match real Microsoft Word.
**Sub-tasks covered:** `tb-split-table`
**Ground truth:** `parity/fixtures/rw-tb-split-table.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-split-table): emit `body:gridCol[('w', '3116')]`
- FR (tb-split-table): emit `body:gridCol[('w', '3117')]`
- FR (tb-split-table): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-split-table): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-split-table): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-split-table): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-split-table): emit `styles:TableGrid:pPr[]`
- FR (tb-split-table): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-split-table): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-split-table): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-split-table): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-split-table   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Style Options: Banded Columns ON  (Tables · TB)

**Goal:** make the clone's `Table Style Options: Banded Columns ON` output match real Microsoft Word.
**Sub-tasks covered:** `tb-styleopt-bandedcols-on`
**Ground truth:** `parity/fixtures/rw-tb-styleopt-bandedcols-on.docx`
**Current parity:** GAP — 28 missing node(s), 16 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-styleopt-bandedcols-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000000000000')]`
- FR (tb-styleopt-bandedcols-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '1'), ('val', '000010000000')]`
- FR (tb-styleopt-bandedcols-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-styleopt-bandedcols-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-styleopt-bandedcols-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000000')]`
- FR (tb-styleopt-bandedcols-on): emit `body:gridCol[('w', '3116')]`
- FR (tb-styleopt-bandedcols-on): emit `body:gridCol[('w', '3117')]`
- FR (tb-styleopt-bandedcols-on): emit `body:pPr[]`
- FR (tb-styleopt-bandedcols-on): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '0'), ('val', '00A0')]`
- FR (tb-styleopt-bandedcols-on): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-styleopt-bandedcols-on): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-styleopt-bandedcols-on): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-styleopt-bandedcols-on): emit `body:trPr[]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:bottom[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:bottom[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:insideH[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:insideV[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:left[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:left[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:pPr[]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:right[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:right[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '156082'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'C1E4F5'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedcols-on): emit `styles:GridTable4-Accent1:top[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:insideH[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:insideV[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '4472C4'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'D9E2F3'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedcols-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-styleopt-bandedcols-on   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Style Options: Banded Rows OFF  (Tables · TB)

**Goal:** make the clone's `Table Style Options: Banded Rows OFF` output match real Microsoft Word.
**Sub-tasks covered:** `tb-styleopt-bandedrows-off`
**Ground truth:** `parity/fixtures/rw-tb-styleopt-bandedrows-off.docx`
**Current parity:** GAP — 26 missing node(s), 16 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-styleopt-bandedrows-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000000000000')]`
- FR (tb-styleopt-bandedrows-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-styleopt-bandedrows-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000000')]`
- FR (tb-styleopt-bandedrows-off): emit `body:gridCol[('w', '3116')]`
- FR (tb-styleopt-bandedrows-off): emit `body:gridCol[('w', '3117')]`
- FR (tb-styleopt-bandedrows-off): emit `body:pPr[]`
- FR (tb-styleopt-bandedrows-off): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '1'), ('noVBand', '1'), ('val', '06A0')]`
- FR (tb-styleopt-bandedrows-off): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-styleopt-bandedrows-off): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-styleopt-bandedrows-off): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-styleopt-bandedrows-off): emit `body:trPr[]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:bottom[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:bottom[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:insideH[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:insideV[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:left[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:left[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:pPr[]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:right[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:right[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '156082'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'C1E4F5'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-bandedrows-off): emit `styles:GridTable4-Accent1:top[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:insideH[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:insideV[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '4472C4'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'D9E2F3'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-bandedrows-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-styleopt-bandedrows-off   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Style Options: First Column OFF  (Tables · TB)

**Goal:** make the clone's `Table Style Options: First Column OFF` output match real Microsoft Word.
**Sub-tasks covered:** `tb-styleopt-firstcol-off`
**Ground truth:** `parity/fixtures/rw-tb-styleopt-firstcol-off.docx`
**Current parity:** GAP — 24 missing node(s), 16 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-styleopt-firstcol-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-styleopt-firstcol-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-styleopt-firstcol-off): emit `body:gridCol[('w', '3116')]`
- FR (tb-styleopt-firstcol-off): emit `body:gridCol[('w', '3117')]`
- FR (tb-styleopt-firstcol-off): emit `body:tblLook[('firstColumn', '0'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '0420')]`
- FR (tb-styleopt-firstcol-off): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-styleopt-firstcol-off): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-styleopt-firstcol-off): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-styleopt-firstcol-off): emit `body:trPr[]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:bottom[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:bottom[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:insideH[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:insideV[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:left[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:left[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:pPr[]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:right[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:right[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '156082'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'C1E4F5'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-firstcol-off): emit `styles:GridTable4-Accent1:top[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:insideH[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:insideV[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '4472C4'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'D9E2F3'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-firstcol-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-styleopt-firstcol-off   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Style Options: Header Row OFF  (Tables · TB)

**Goal:** make the clone's `Table Style Options: Header Row OFF` output match real Microsoft Word.
**Sub-tasks covered:** `tb-styleopt-headerrow-off`
**Ground truth:** `parity/fixtures/rw-tb-styleopt-headerrow-off.docx`
**Current parity:** GAP — 26 missing node(s), 16 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-styleopt-headerrow-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000000000000')]`
- FR (tb-styleopt-headerrow-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-styleopt-headerrow-off): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000000')]`
- FR (tb-styleopt-headerrow-off): emit `body:gridCol[('w', '3116')]`
- FR (tb-styleopt-headerrow-off): emit `body:gridCol[('w', '3117')]`
- FR (tb-styleopt-headerrow-off): emit `body:pPr[]`
- FR (tb-styleopt-headerrow-off): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '0480')]`
- FR (tb-styleopt-headerrow-off): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-styleopt-headerrow-off): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-styleopt-headerrow-off): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-styleopt-headerrow-off): emit `body:trPr[]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:bottom[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:bottom[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:insideH[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:insideV[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:left[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:left[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:pPr[]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:right[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:right[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '156082'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'C1E4F5'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-headerrow-off): emit `styles:GridTable4-Accent1:top[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:insideH[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:insideV[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '4472C4'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'D9E2F3'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-headerrow-off): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-styleopt-headerrow-off   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Style Options: Last Column ON  (Tables · TB)

**Goal:** make the clone's `Table Style Options: Last Column ON` output match real Microsoft Word.
**Sub-tasks covered:** `tb-styleopt-lastcol-on`
**Ground truth:** `parity/fixtures/rw-tb-styleopt-lastcol-on.docx`
**Current parity:** GAP — 28 missing node(s), 16 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-styleopt-lastcol-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000000000000')]`
- FR (tb-styleopt-lastcol-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-styleopt-lastcol-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '1'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000100000000')]`
- FR (tb-styleopt-lastcol-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-styleopt-lastcol-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000000')]`
- FR (tb-styleopt-lastcol-on): emit `body:gridCol[('w', '3116')]`
- FR (tb-styleopt-lastcol-on): emit `body:gridCol[('w', '3117')]`
- FR (tb-styleopt-lastcol-on): emit `body:pPr[]`
- FR (tb-styleopt-lastcol-on): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '1'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '05A0')]`
- FR (tb-styleopt-lastcol-on): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-styleopt-lastcol-on): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-styleopt-lastcol-on): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-styleopt-lastcol-on): emit `body:trPr[]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:bottom[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:bottom[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:insideH[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:insideV[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:left[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:left[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:pPr[]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:right[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:right[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '156082'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'C1E4F5'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-lastcol-on): emit `styles:GridTable4-Accent1:top[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:insideH[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:insideV[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '4472C4'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'D9E2F3'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-lastcol-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-styleopt-lastcol-on   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Style Options: Total Row ON  (Tables · TB)

**Goal:** make the clone's `Table Style Options: Total Row ON` output match real Microsoft Word.
**Sub-tasks covered:** `tb-styleopt-totalrow-on`
**Ground truth:** `parity/fixtures/rw-tb-styleopt-totalrow-on.docx`
**Current parity:** GAP — 27 missing node(s), 16 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-styleopt-totalrow-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-styleopt-totalrow-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '1'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '010000000000')]`
- FR (tb-styleopt-totalrow-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-styleopt-totalrow-on): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000000')]`
- FR (tb-styleopt-totalrow-on): emit `body:gridCol[('w', '3116')]`
- FR (tb-styleopt-totalrow-on): emit `body:gridCol[('w', '3117')]`
- FR (tb-styleopt-totalrow-on): emit `body:pPr[]`
- FR (tb-styleopt-totalrow-on): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '1'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04E0')]`
- FR (tb-styleopt-totalrow-on): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-styleopt-totalrow-on): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-styleopt-totalrow-on): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-styleopt-totalrow-on): emit `body:trPr[]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:bottom[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:bottom[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:insideH[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:insideV[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:left[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:left[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:pPr[]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:right[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:right[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '156082'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'C1E4F5'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:top[('color', '156082'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FR (tb-styleopt-totalrow-on): emit `styles:GridTable4-Accent1:top[('color', '45B0E1'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:bottom[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:insideH[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:insideV[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:left[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:right[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', '4472C4'), ('themeFill', 'accent1'), ('val', 'clear')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:shd[('color', 'auto'), ('fill', 'D9E2F3'), ('themeFill', 'accent1'), ('themeFillTint', '33'), ('val', 'clear')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'double')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '4472C4'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('val', 'single')]`
- FID (tb-styleopt-totalrow-on): stop emitting (or justify) `styles:GridTable4-Accent1:top[('color', '8EAADB'), ('space', '0'), ('sz', '4'), ('themeColor', 'accent1'), ('themeTint', '99'), ('val', 'single')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-styleopt-totalrow-on   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Styles gallery: apply Grid Table 4 Accent 1  (Tables · TB)

**Goal:** make the clone's `Table Styles gallery: apply Grid Table 4 Accent 1` output match real Microsoft Word.
**Sub-tasks covered:** `tb-style-grid4a1`
**Ground truth:** `parity/fixtures/rw-tb-style-grid4a1.docx`
**Current parity:** GAP — 12 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-style-grid4a1): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000000000000')]`
- FR (tb-style-grid4a1): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-style-grid4a1): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-style-grid4a1): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000000')]`
- FR (tb-style-grid4a1): emit `body:gridCol[('w', '3116')]`
- FR (tb-style-grid4a1): emit `body:gridCol[('w', '3117')]`
- FR (tb-style-grid4a1): emit `body:pPr[]`
- FR (tb-style-grid4a1): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-style-grid4a1): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-style-grid4a1): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-style-grid4a1): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-style-grid4a1): emit `body:trPr[]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-style-grid4a1): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-style-grid4a1): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-style-grid4a1): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-style-grid4a1   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table Styles gallery: apply List Table 3  (Tables · TB)

**Goal:** make the clone's `Table Styles gallery: apply List Table 3` output match real Microsoft Word.
**Sub-tasks covered:** `tb-style-listtable3`
**Ground truth:** `parity/fixtures/rw-tb-style-listtable3.docx`
**Current parity:** GAP — 13 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-style-listtable3): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '000000000000')]`
- FR (tb-style-listtable3): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '1'), ('oddVBand', '0'), ('val', '000000100000')]`
- FR (tb-style-listtable3): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '0'), ('firstRow', '1'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '100000000000')]`
- FR (tb-style-listtable3): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '0'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000000')]`
- FR (tb-style-listtable3): emit `body:cnfStyle[('evenHBand', '0'), ('evenVBand', '0'), ('firstColumn', '1'), ('firstRow', '0'), ('firstRowFirstColumn', '1'), ('firstRowLastColumn', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('lastRowFirstColumn', '0'), ('lastRowLastColumn', '0'), ('oddHBand', '0'), ('oddVBand', '0'), ('val', '001000000100')]`
- FR (tb-style-listtable3): emit `body:gridCol[('w', '3116')]`
- FR (tb-style-listtable3): emit `body:gridCol[('w', '3117')]`
- FR (tb-style-listtable3): emit `body:pPr[]`
- FR (tb-style-listtable3): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-style-listtable3): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-style-listtable3): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-style-listtable3): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-style-listtable3): emit `body:trPr[]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-style-listtable3): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-style-listtable3): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-style-listtable3): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-style-listtable3   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table alignment: center  (Tables · TB)

**Goal:** make the clone's `Table alignment: center` output match real Microsoft Word.
**Sub-tasks covered:** `tb-align-center`
**Ground truth:** `parity/fixtures/rw-tb-align-center.docx`
**Current parity:** GAP — 10 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-align-center): emit `body:gridCol[('w', '3116')]`
- FR (tb-align-center): emit `body:gridCol[('w', '3117')]`
- FR (tb-align-center): emit `body:jc[('val', 'center')]`
- FR (tb-align-center): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-align-center): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-align-center): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-align-center): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-align-center): emit `body:trPr[]`
- FR (tb-align-center): emit `styles:TableGrid:pPr[]`
- FR (tb-align-center): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-align-center): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-align-center): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-align-center): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-align-center   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Table indent from left: 0.5 inch  (Tables · TB)

**Goal:** make the clone's `Table indent from left: 0.5 inch` output match real Microsoft Word.
**Sub-tasks covered:** `tb-indent-05in`
**Ground truth:** `parity/fixtures/rw-tb-indent-05in.docx`
**Current parity:** GAP — 8 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-indent-05in): emit `body:gridCol[('w', '3116')]`
- FR (tb-indent-05in): emit `body:gridCol[('w', '3117')]`
- FR (tb-indent-05in): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-indent-05in): emit `body:tblW[('type', 'dxa'), ('w', '9350')]`
- FR (tb-indent-05in): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-indent-05in): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-indent-05in): emit `styles:TableGrid:pPr[]`
- FR (tb-indent-05in): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-indent-05in): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-indent-05in): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-indent-05in): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-indent-05in   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Text Direction: first click (caret cell)  (Tables · TB)

**Goal:** make the clone's `Text Direction: first click (caret cell)` output match real Microsoft Word.
**Sub-tasks covered:** `tb-textdir`
**Ground truth:** `parity/fixtures/rw-tb-textdir.docx`
**Current parity:** GAP — 13 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (tb-textdir): emit `body:cantSplit[]`
- FR (tb-textdir): emit `body:gridCol[('w', '3116')]`
- FR (tb-textdir): emit `body:gridCol[('w', '3117')]`
- FR (tb-textdir): emit `body:ind[('left', '113'), ('right', '113')]`
- FR (tb-textdir): emit `body:pPr[]`
- FR (tb-textdir): emit `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1'), ('val', '04A0')]`
- FR (tb-textdir): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (tb-textdir): emit `body:tcW[('type', 'dxa'), ('w', '3116')]`
- FR (tb-textdir): emit `body:tcW[('type', 'dxa'), ('w', '3117')]`
- FR (tb-textdir): emit `body:trHeight[('val', '1134')]`
- FR (tb-textdir): emit `body:trPr[]`
- FR (tb-textdir): emit `styles:TableGrid:pPr[]`
- FR (tb-textdir): emit `styles:TableGrid:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (tb-textdir): stop emitting (or justify) `body:gridCol[('w', '3120')]`
- FID (tb-textdir): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (tb-textdir): stop emitting (or justify) `body:tcW[('type', 'dxa'), ('w', '3120')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only tb-textdir   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Underline dashed  (Home · TV)

**Goal:** make the clone's `Underline dashed` output match real Microsoft Word.
**Sub-tasks covered:** `ul-dashed`
**Ground truth:** `parity/fixtures/rw-ul-dashed.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ul-dashed   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Underline dotted  (Home · TV)

**Goal:** make the clone's `Underline dotted` output match real Microsoft Word.
**Sub-tasks covered:** `ul-dotted`
**Ground truth:** `parity/fixtures/rw-ul-dotted.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ul-dotted   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Underline double  (Home · TV)

**Goal:** make the clone's `Underline double` output match real Microsoft Word.
**Sub-tasks covered:** `ul-double`
**Ground truth:** `parity/fixtures/rw-ul-double.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ul-double   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Underline single  (Home · TV)

**Goal:** make the clone's `Underline single` output match real Microsoft Word.
**Sub-tasks covered:** `ul-single`
**Ground truth:** `parity/fixtures/rw-ul-single.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ul-single   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Underline wavy  (Home · TV)

**Goal:** make the clone's `Underline wavy` output match real Microsoft Word.
**Sub-tasks covered:** `ul-wavy`
**Ground truth:** `parity/fixtures/rw-ul-wavy.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ul-wavy   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Underline words-only  (Home · TV)

**Goal:** make the clone's `Underline words-only` output match real Microsoft Word.
**Sub-tasks covered:** `ul-words`
**Ground truth:** `parity/fixtures/rw-ul-words.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 0 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- _(none)_

### Acceptance (regression gate)
```
python parity/engines/run.py --only ul-words   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---
