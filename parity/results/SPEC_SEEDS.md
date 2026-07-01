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
**Current parity:** GAP — 7 missing node(s), 14 fidelity warning(s)

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
- FID (table): stop emitting (or justify) `styles:TableGrid:@type=table`
- FID (table): stop emitting (or justify) `styles:TableGrid:basedOn[('val', 'TableNormal')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:bottom[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:insideH[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:insideV[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:left[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:name[('val', 'Table Grid')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:right[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:tblBorders[]`
- FID (table): stop emitting (or justify) `styles:TableGrid:tblPr[]`
- FID (table): stop emitting (or justify) `styles:TableGrid:top[('color', 'auto'), ('space', '0'), ('sz', '4'), ('val', 'single')]`
- FID (table): stop emitting (or justify) `styles:TableGrid:uiPriority[('val', '39')]`

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
