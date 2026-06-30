# Spec Seeds — parity gaps → /speckit-specify input

Auto-generated from the parity ledger. Each block is a feature whose clone output diverges from real Word. Feed a block to `/speckit-specify`; the **ground-truth fixture** is the definition of correct behavior and the **acceptance** command is the regression gate.

## Align Left  (Home · T0)

**Goal:** make the clone's `Align Left` output match real Microsoft Word.
**Sub-tasks covered:** `alignleft`
**Ground truth:** `parity/fixtures/rw-alignleft.docx`
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 5 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- FID (alignleft): stop emitting (or justify) `body:cntxtAlts[]`
- FID (alignleft): stop emitting (or justify) `body:jc[('val', 'left')]`
- FID (alignleft): stop emitting (or justify) `body:ligatures[('val', 'standard')]`
- FID (alignleft): stop emitting (or justify) `body:pPr[]`
- FID (alignleft): stop emitting (or justify) `body:rPr[]`

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
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 2 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- FID (bold): stop emitting (or justify) `body:cntxtAlts[]`
- FID (bold): stop emitting (or justify) `body:ligatures[('val', 'standard')]`

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
**Current parity:** GAP — 1 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (bullets): emit `body:pStyle[('val', 'ListParagraph')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (bullets): stop emitting (or justify) `body:cntxtAlts[]`
- FID (bullets): stop emitting (or justify) `body:ligatures[('val', 'standard')]`
- FID (bullets): stop emitting (or justify) `body:rPr[]`

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
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- FID (center): stop emitting (or justify) `body:cntxtAlts[]`
- FID (center): stop emitting (or justify) `body:ligatures[('val', 'standard')]`
- FID (center): stop emitting (or justify) `body:rPr[]`

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
**Current parity:** GAP — 1 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (fontface): emit `body:rFonts[('ascii', 'Arial'), ('hAnsi', 'Arial')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (fontface): stop emitting (or justify) `body:cntxtAlts[]`
- FID (fontface): stop emitting (or justify) `body:ligatures[('val', 'standard')]`
- FID (fontface): stop emitting (or justify) `body:rFonts[('ascii', 'Arial'), ('cs', 'Arial'), ('eastAsia', 'Arial'), ('hAnsi', 'Arial')]`

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
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- FID (fontsize): stop emitting (or justify) `body:cntxtAlts[]`
- FID (fontsize): stop emitting (or justify) `body:ligatures[('val', 'standard')]`
- FID (fontsize): stop emitting (or justify) `body:szCs[('val', '28')]`

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
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 2 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- FID (italic): stop emitting (or justify) `body:cntxtAlts[]`
- FID (italic): stop emitting (or justify) `body:ligatures[('val', 'standard')]`

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
**Current parity:** semantic-pass (fidelity-only) — 0 missing node(s), 2 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- _(none — clone already emits everything Word does)_

### Fidelity requirements — clone over-emits (from `extra`)
- FID (underline): stop emitting (or justify) `body:cntxtAlts[]`
- FID (underline): stop emitting (or justify) `body:ligatures[('val', 'standard')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only underline   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Insert Table  (Insert · T1)

**Goal:** make the clone's `Insert Table` output match real Microsoft Word.
**Sub-tasks covered:** `table`
**Ground truth:** `parity/fixtures/rw-table.docx`
**Current parity:** GAP — 7 missing node(s), 2 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (table): emit `body:bottom[('type', 'dxa'), ('w', '0')]`
- FR (table): emit `body:tblCellMar[]`
- FR (table): emit `body:tblLayout[('type', 'fixed')]`
- FR (table): emit `body:tblLook[('firstColumn', '0'), ('firstRow', '0'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '0'), ('val', '0000')]`
- FR (table): emit `body:tblPrEx[]`
- FR (table): emit `body:tblW[('type', 'auto'), ('w', '0')]`
- FR (table): emit `body:top[('type', 'dxa'), ('w', '0')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (table): stop emitting (or justify) `body:tblLook[('firstColumn', '1'), ('firstRow', '1'), ('lastColumn', '0'), ('lastRow', '0'), ('noHBand', '0'), ('noVBand', '1')]`
- FID (table): stop emitting (or justify) `body:tblStyle[('val', 'TableGrid')]`

### Acceptance (regression gate)
```
python parity/engines/run.py --only table   # expect: semantic-pass, missing = 0
```

### Next steps
`/speckit-specify` (paste this block) → `/speckit-plan` → `/speckit-tasks` → implement → re-run acceptance.

---

## Page Number  (Insert · T1)

**Goal:** make the clone's `Page Number` output match real Microsoft Word.
**Sub-tasks covered:** `pagenum`
**Ground truth:** `parity/fixtures/rw-pagenum.docx`
**Current parity:** GAP — 17 missing node(s), 3 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (pagenum): emit `body:footerReference[('id', 'rId#'), ('type', 'even')]`
- FR (pagenum): emit `body:footerReference[('id', 'rId#'), ('type', 'first')]`
- FR (pagenum): emit `body:headerReference[('id', 'rId#'), ('type', 'default')]`
- FR (pagenum): emit `body:headerReference[('id', 'rId#'), ('type', 'even')]`
- FR (pagenum): emit `body:headerReference[('id', 'rId#'), ('type', 'first')]`
- FR (pagenum): emit `footer:ftr[('Ignorable', 'w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14')]`
- FR (pagenum): emit `footer:instrText[('space', 'preserve')]|text=PAGE \* MERGEFORMAT`
- FR (pagenum): emit `footer:noProof[]`
- FR (pagenum): emit `footer:pPr[]`
- FR (pagenum): emit `footer:pStyle[('val', 'Footer')]`
- FR (pagenum): emit `footer:p[]`
- FR (pagenum): emit `footer:r[]`
- FR (pagenum): emit `footer:t[]`
- FR (pagenum): emit `header:hdr[('Ignorable', 'w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14')]`
- FR (pagenum): emit `header:pPr[]`
- FR (pagenum): emit `header:pStyle[('val', 'Header')]`
- FR (pagenum): emit `header:p[]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (pagenum): stop emitting (or justify) `footer:ftr[]`
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
