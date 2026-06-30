# Tasks: Close the remaining T0/T1 OOXML gaps

**Feature**: `023-t0t1-ooxml-fidelity` · **Plan**: [plan.md](./plan.md)

Batched (4 fixes, one build cycle).

- **T001 RED** — add 4 regression tests to `scripts/test-suite-pm.js`: list pStyle+order (bullets/numbering) + toggle-off
  guard; align-left emits no jc; setFontFamily Arial = ascii+hAnsi only; setFontSizePt = sz only.
- **T002 GREEN (no-fork ×2)** — `bridge/lists.ts` toggle wrappers (pStyle first + numPr order; guard numId!=null) + rewire
  `commands.js` H.bullets/H.numbering + repoint the bullets/numbering parity probes; `bridge/commands.ts` remap
  setTextAlign('left')→unsetTextAlign.
- **T003 GREEN (fork ×2, authorized, NOTICE'd)** — `styles.js` fontFamily → {ascii,hAnsi}; `styles.js` drop fontSizeCs sync
  + remove 'fontSizeCs' from RUN_PROPERTIES_DERIVED_FROM_MARKS.
- **T004 Gates** — one `npm run build` → `test:pm` / `test:smoke` / `test:roundtrip` green.
- **T005 Parity acceptance** — re-capture clone T0 (`run.py --tier T0 --capture-clone` + `--only numbering --capture-clone`)
  → `run.py --only {bullets,numbering,alignleft,fontface,fontsize}` body semantic-pass.
- **T006 Review + commit** — adversarial review of the fork edits + bridge wrapper; fix findings; commit; checkpoint.
