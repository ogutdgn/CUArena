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
**Current parity:** GAP — 7 missing node(s), 35 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (bullets): emit `numbering:abstractNum[('abstractNumId', '0'), ('restartNumberingAfterBreak', '0')]`
- FR (bullets): emit `numbering:lvl[('ilvl', '0')]`
- FR (bullets): emit `numbering:multiLevelType[('val', 'singleLevel')]`
- FR (bullets): emit `numbering:nsid[('val', '1314181C')]`
- FR (bullets): emit `numbering:num[('durableId', '1735197339'), ('numId', '1')]`
- FR (bullets): emit `numbering:numbering[('Ignorable', 'w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14')]`
- FR (bullets): emit `numbering:tmpl[('val', '04090001')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (bullets): stop emitting (or justify) `numbering:abstractNum[('abstractNumId', '3'), ('restartNumberingAfterBreak', '0')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '1440')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '2160')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '2880')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '3600')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '4320')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '5040')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '5760')]`
- FID (bullets): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '6480')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlJc[('val', 'left')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', '\uf0a7')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', 'o')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', '•')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', '▪')]`
- FID (bullets): stop emitting (or justify) `numbering:lvlText[('val', '◦')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '0'), ('tplc', '04090001')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '1'), ('tentative', '1'), ('tplc', '04090003')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '2'), ('tentative', '1'), ('tplc', '04090005')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '3'), ('tentative', '1'), ('tplc', '04090001')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '4'), ('tentative', '1'), ('tplc', '04090003')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '5'), ('tentative', '1'), ('tplc', '04090005')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '6'), ('tentative', '1'), ('tplc', '04090001')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '7'), ('tentative', '1'), ('tplc', '04090003')]`
- FID (bullets): stop emitting (or justify) `numbering:lvl[('ilvl', '8'), ('tentative', '1'), ('tplc', '04090005')]`
- FID (bullets): stop emitting (or justify) `numbering:multiLevelType[('val', 'hybridMultilevel')]`
- FID (bullets): stop emitting (or justify) `numbering:nsid[('val', '49CAEF44')]`
- FID (bullets): stop emitting (or justify) `numbering:numFmt[('val', 'bullet')]`
- FID (bullets): stop emitting (or justify) `numbering:num[('numId', '4')]`
- FID (bullets): stop emitting (or justify) `numbering:pPr[]`
- FID (bullets): stop emitting (or justify) `numbering:rFonts[('ascii', 'Courier New'), ('cs', 'Courier New'), ('hAnsi', 'Courier New'), ('hint', 'default')]`
- FID (bullets): stop emitting (or justify) `numbering:rFonts[('ascii', 'Symbol'), ('hAnsi', 'Symbol'), ('hint', 'default')]`
- FID (bullets): stop emitting (or justify) `numbering:rFonts[('ascii', 'Wingdings'), ('hAnsi', 'Wingdings'), ('hint', 'default')]`
- FID (bullets): stop emitting (or justify) `numbering:rPr[]`
- FID (bullets): stop emitting (or justify) `numbering:start[('val', '1')]`
- FID (bullets): stop emitting (or justify) `numbering:tmpl[('val', '39C5705B')]`

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
**Current parity:** GAP — 7 missing node(s), 36 fidelity warning(s)

### Functional requirements — clone MUST emit (from `missing`)
- FR (numbering): emit `numbering:abstractNum[('abstractNumId', '0'), ('restartNumberingAfterBreak', '0')]`
- FR (numbering): emit `numbering:lvl[('ilvl', '0')]`
- FR (numbering): emit `numbering:multiLevelType[('val', 'singleLevel')]`
- FR (numbering): emit `numbering:nsid[('val', '4FDF52CB')]`
- FR (numbering): emit `numbering:num[('durableId', '1646547401'), ('numId', '1')]`
- FR (numbering): emit `numbering:numbering[('Ignorable', 'w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14')]`
- FR (numbering): emit `numbering:tmpl[('val', '0409000F')]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (numbering): stop emitting (or justify) `numbering:abstractNum[('abstractNumId', '3'), ('restartNumberingAfterBreak', '0')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '180'), ('left', '2160')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '180'), ('left', '4320')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '180'), ('left', '6480')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '1440')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '2880')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '3600')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '5040')]`
- FID (numbering): stop emitting (or justify) `numbering:ind[('hanging', '360'), ('left', '5760')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlJc[('val', 'left')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlJc[('val', 'right')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%2.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%3.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%4.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%5.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%6.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%7.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%8.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvlText[('val', '%9.')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '0'), ('tplc', '0409000F')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '1'), ('tentative', '1'), ('tplc', '04090019')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '2'), ('tentative', '1'), ('tplc', '0409001B')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '3'), ('tentative', '1'), ('tplc', '0409000F')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '4'), ('tentative', '1'), ('tplc', '04090019')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '5'), ('tentative', '1'), ('tplc', '0409001B')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '6'), ('tentative', '1'), ('tplc', '0409000F')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '7'), ('tentative', '1'), ('tplc', '04090019')]`
- FID (numbering): stop emitting (or justify) `numbering:lvl[('ilvl', '8'), ('tentative', '1'), ('tplc', '0409001B')]`
- FID (numbering): stop emitting (or justify) `numbering:multiLevelType[('val', 'hybridMultilevel')]`
- FID (numbering): stop emitting (or justify) `numbering:numFmt[('val', 'decimal')]`
- FID (numbering): stop emitting (or justify) `numbering:numFmt[('val', 'lowerLetter')]`
- FID (numbering): stop emitting (or justify) `numbering:numFmt[('val', 'lowerRoman')]`
- FID (numbering): stop emitting (or justify) `numbering:num[('numId', '4')]`
- FID (numbering): stop emitting (or justify) `numbering:pPr[]`
- FID (numbering): stop emitting (or justify) `numbering:start[('val', '1')]`
- FID (numbering): stop emitting (or justify) `numbering:tmpl[('val', '85888E32')]`

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
**Current parity:** GAP — 38 missing node(s), 3 fidelity warning(s)

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
- FR (pagenum): emit `styles:basedOn[('val', 'DefaultParagraphFont')]`
- FR (pagenum): emit `styles:basedOn[('val', 'Normal')]`
- FR (pagenum): emit `styles:link[('val', 'Footer')]`
- FR (pagenum): emit `styles:link[('val', 'FooterChar')]`
- FR (pagenum): emit `styles:link[('val', 'Header')]`
- FR (pagenum): emit `styles:link[('val', 'HeaderChar')]`
- FR (pagenum): emit `styles:name[('val', 'Footer Char')]`
- FR (pagenum): emit `styles:name[('val', 'Header Char')]`
- FR (pagenum): emit `styles:name[('val', 'footer')]`
- FR (pagenum): emit `styles:name[('val', 'header')]`
- FR (pagenum): emit `styles:pPr[]`
- FR (pagenum): emit `styles:spacing[('after', '0'), ('line', '240'), ('lineRule', 'auto')]`
- FR (pagenum): emit `styles:style[('customStyle', '1'), ('styleId', 'FooterChar'), ('type', 'character')]`
- FR (pagenum): emit `styles:style[('customStyle', '1'), ('styleId', 'HeaderChar'), ('type', 'character')]`
- FR (pagenum): emit `styles:style[('styleId', 'Footer'), ('type', 'paragraph')]`
- FR (pagenum): emit `styles:style[('styleId', 'Header'), ('type', 'paragraph')]`
- FR (pagenum): emit `styles:tab[('pos', '4680'), ('val', 'center')]`
- FR (pagenum): emit `styles:tab[('pos', '9360'), ('val', 'right')]`
- FR (pagenum): emit `styles:tabs[]`
- FR (pagenum): emit `styles:uiPriority[('val', '99')]`
- FR (pagenum): emit `styles:unhideWhenUsed[]`

### Fidelity requirements — clone over-emits (from `extra`)
- FID (pagenum): stop emitting (or justify) `footer:ftr[]`
- FID (pagenum): stop emitting (or justify) `footer:instrText[('space', 'preserve')]|text=PAGE`
- FID (pagenum): stop emitting (or justify) `footer:rPr[]`

### Structural requirements
- STR (pagenum): `footer` parts — Word=3, clone=1
- STR (pagenum): `header` parts — Word=3, clone=0

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
