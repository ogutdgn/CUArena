# Parity Pipeline

Measures how faithfully this Word clone reproduces **real Microsoft Word**, feature by feature,
by diffing the clone's `.docx` output against real-Word ground truth. The output is a **gap ledger**
(what's missing / to improve / to fix / to build) that drives development — and the same diff is the
RL environment's reward function.

> The clone's code-traced status (`docs/FEATURE_PARITY_AUDIT.md`) is an ESTIMATE, not validated
> against real Word. This pipeline produces the **real** numbers and gaps.

## Parity bar: 3-bucket
For each task, every OOXML node is classified:
- **match** — present in both (semantic core agrees)
- **missing** — Word emits it, clone does NOT → clone gap / missing hidden default
- **extra** — clone emits it, Word does NOT → over-emission
- **noise** — `rsid*`, `paraId`, `textId` (random per-save) → stripped before comparing

Verdict = semantic pass/fail (any `missing` → gap) **plus** a fidelity-warning list (the `extra`/structural
diffs). This gives a usable % AND records the byte-exact gap, without failing on harmless defaults.

## Layout
```
parity/
  engines/ooxml_diff.py   # generic 3-bucket OOXML differ (feature-agnostic). WORKS.
  probes/                 # clone-side: run an action in the Electron app, export .docx
  ground-truth/           # real-Word side: COM scripts that author the same action
  fixtures/               # captured docx pairs (rw-*.docx = real Word, wc-*.docx = clone)
  results/                # diff records + LEDGER
```

## How a task runs (proven on 3 pilots: bold, pagenum, table)
1. **Clone side:** `electron --shot-evalfile=parity/probes/<task>.js` performs the action, exports `wc-<task>.docx`.
2. **Real-Word side:** `parity/ground-truth/realword_<task>.ps1` drives Word via COM, saves `rw-<task>.docx`.
   - ⚠️ Ground truth must be HYBRID: COM is fine where COM == ribbon (Bold, PAGE field), but COM `Tables.Add`
     ≠ ribbon "Insert Table" (ribbon auto-applies `TableGrid`). Gallery/style actions need real UI capture (vsto).
3. **Diff:** `python parity/engines/ooxml_diff.py rw-<task>.docx wc-<task>.docx --id <task>`

## Status
- ✅ 3-bucket differ working, reproduces 3 manual pilots + finds extras (cell margins, header refs)
- ✅ ledger writer · generic task runner (`run.py`) · spec-seeds generator
- ✅ differ reviewer (`review_differ.py`): golden + Word-vs-self + clone-vs-self + golden-baseline — all green
- ✅ **v2 differ: baseline subtraction** — diff each side's delta-vs-empty-doc so blank-document boilerplate
  cancels (pagenum `extra` 18→4: the ListParagraph cluster dropped). Noise list proven complete; do NOT add
  `Ignorable` (a `<w:ftr>` without `mc:Ignorable` is a real gap, not noise).
- 🔜 task enumeration over the locked scope (main ribbon from `ribbon-data.js`; contextual tabs via UIA inventory)
- 🔜 rId-value normalization (header/footer refs keyed on `type`, not the per-doc `id`)
- 🔜 2nd verifier: UI-flow fidelity (DOM introspection vs `ribbon-data.js` spec)

See `docs/SCOPE_LOCKED.md` for the 111 locked features this pipeline targets.
