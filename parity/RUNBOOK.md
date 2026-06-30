# RUNBOOK — running the full parity operation (for a future session)

Goal: go through **every locked feature** (and its sub-features), capture clone vs. real-Word output,
diff them, and record all differences in `parity/results/LEDGER.md`. The pipeline is built and proven on
3 pilots; this runbook is how a later session scales it to the full scope.

> **North star:** when this whole effort is done, **every feature in the locked scope — every sub-feature,
> every functionality, and every UI flow (dropdowns, dialogs, contextual tabs) — must be identical to real
> Microsoft Word.** OOXML output identical (this pipeline) AND interaction flow identical (the flow verifier).
> The ledger reaching zero `missing` across the scope, plus flow parity, IS that goal made measurable.

## Prerequisites
- Windows, real MS Word installed, **Word fully closed** before COM capture (the COM scripts abort if WINWORD is running).
- Clone built: `npm run build` (the `out/` dir must exist; Electron probes load it).
- On branch `parity-pipeline`.

## The 3 commands the runner chains
```
1. clone:      electron --shot-evalfile=parity/probes/<id>-pilot-probe.js   -> parity/fixtures/wc-<id>.docx
2. real Word:  parity/ground-truth/realword_<id>.ps1 -Out parity/fixtures/rw-<id>.docx
3. diff+ledger: python parity/engines/run.py
```

## Run it
```bash
# diff existing fixtures only (no capture); subtracts rw-blank/wc-blank if present:
python parity/engines/run.py

# capture the empty-doc BASELINES once (needed for clean deltas; Word closed):
python parity/engines/run.py --capture-baseline

# capture both sides THEN diff (Electron + Word must be available, Word closed):
python parity/engines/run.py --capture            # also (re)captures the baselines first
python parity/engines/run.py --only <id> --capture    # single task
python parity/engines/run.py --no-baseline        # v1 full-doc diff (debug / no baselines)
```
Output: `parity/results/LEDGER.md` (+ `ledger.json` + per-task `<id>.json`). The ledger header states
whether **baseline subtraction** is ON (delta-vs-empty-doc) or OFF (v1 full-doc).

## How to ADD a feature/sub-task (this is the bulk of the full operation)
For each control / sub-feature in `docs/SCOPE_LOCKED.md` (the 111 locked features, expanded into sub-tasks):

1. **Pick a minimal, isolated action** (one thing only — keeps the delta clean).
2. **Write the clone probe** `parity/probes/<id>-pilot-probe.js`:
   - wait for `window.__WC_READY`, perform the action via `window.WC.PM.*` / `window.WC.editor`,
     `await PM.exportDocxBytes()`, save to `parity/fixtures/wc-<id>.docx`. (Copy an existing probe.)
3. **Provide real-Word ground truth** — pick the method:
   - `realword_method: "com"` → write `parity/ground-truth/realword_<id>.ps1` driving Word via COM
     (copy `realword_bold.ps1`). USE COM ONLY where COM == ribbon (marks, plain fields).
   - `realword_method: "vsto"` → for **gallery/style/building-block** actions where COM ≠ ribbon
     (Insert Table style, Page-Number gallery, Cover Page, Themes, cell borders…). Capture via a real
     Word UI session (see ms-word-vsto: start_session → do the action → end_session → snapshot delta),
     then reconstruct the `.docx` into `parity/fixtures/rw-<id>.docx`.
4. **Add a row to `parity/tasks.json`** with id, control_id, feature, tab, usage_tier, realword_method.
5. `python parity/engines/run.py --only <id> --capture` and read the ledger entry.

## Enumerating the sub-tasks (what to write tasks for)
Each menu item / contextual-tab button / dialog option = one task. Work in usage-tier order
(T0 → T1 → T2 → locked T3). Expect ~hundreds of tasks at full sub-feature depth.

**Enumeration SOURCE matters — do not enumerate only from the clone, or you miss what the clone lacks:**
- **Main ribbon tabs** → `src/renderer/public/js/ribbon-data.js` (a research-backed FAITHFUL MAP OF REAL WORD,
  including controls the clone only stubs). Safe to enumerate from — it surfaces missing features too.
- **Contextual tabs (Table Design/Layout, Picture Tools, Header/Footer Tools…)** → these are NOT in
  ribbon-data.js. Our only structured source today is `table-tools-pm.js` etc. = **the CLONE's implementation,
  a SUBSET.** Enumerating from it MISSES buttons real Word has but the clone lacks (e.g. Table Design →
  Border Painter, Border Styles/Weight/Color, Table Style Options checkboxes; Table Layout → Select,
  View Gridlines, Properties, Draw Table, Eraser, Sort, Repeat Header Rows, Formula).
  → **First build an AUTHORITATIVE real-Word inventory via UI Automation (UIA):** with a table selected,
  walk real Word's contextual tabs and dump every button (label, type button/dropdown/dialog/gallery, group)
  + the flow each starts. Enumerate contextual-tab tasks from THAT, then diff against the clone's buttons
  (the missing buttons are themselves findings). UIA is also the ground truth for the flow verifier.
- **Dialog options** → `dialogs.js` (the deep L4 tail); enumerate the option sets per dialog.

## Reading the result
- **missing_nodes** = clone must ADD (real gap / missing hidden default) → develop/fix list.
- **extra_nodes** = clone over-emits (fidelity warning) → polish list.
- **part-count divergence** = structural (e.g. Word makes 3 footers, clone 1).

## Develop phase: ledger → speckit → fix → re-verify
Once the ledger is populated, drive fixes through the clone's existing spec-kit flow:
1. `parity/results/SPEC_SEEDS.md` has one spec-ready block per feature (FR from `missing`, fidelity from
   `extra`, structural, ground-truth fixture, acceptance command). It is auto-generated with the ledger.
2. Paste a block into **`/speckit-specify`** → `/speckit-plan` → `/speckit-tasks` → implement the fix in the clone.
3. The spec's **acceptance gate = the parity task**: `python parity/engines/run.py --only <id>` must reach
   `semantic-pass`, `missing = 0`. This is also the regression test.
> Note: spec-seed quality depends on the v2 differ (baseline subtraction) — now LANDED, so seeds no longer
> over-list blank-document boilerplate (the ListParagraph/`numId` cluster is gone). Capture the baselines once
> (`run.py --capture` or `--capture-baseline`) so every task is diffed as a clean delta.

## Validating the engine (run BEFORE scaling to hundreds of tasks)
`python parity/engines/review_differ.py` — objective self-validation of the differ. Three suites:
- **GOLDEN** — hand-labeled synthetic docx pairs with known expected diffs (logic correctness).
- **WORD-VS-SELF** — same real-Word action captured twice; diff MUST be 0 (proves the noise list is complete;
  any leak is, by definition, noise to add to `NOISE_ATTRS`). Capture pairs into `fixtures/selftest/rw-<id>-a/b.docx`.
- **CLONE-VS-SELF** — same clone action exported twice; diff MUST be 0 (clone export determinism).
Exit 0 iff all pass. **Re-run whenever you add a new action category** (date fields, drawings, etc. may bring
action-specific noise — Word-vs-self auto-surfaces it). Baseline state: all suites pass on bold/pagenum/table.

## Engine refinements — status
- ✅ **Baseline subtraction (v2 — DONE):** `diff()` compares each side's **signed** delta-vs-its-empty-doc
  baseline (`rw-blank.docx`/`wc-blank.docx`) before bucketing, so blank-document boilerplate cancels and only
  the feature delta is compared. **Signed (not Counter `-`) deltas** so a feature that REMOVES a node present
  in the baseline still surfaces (Counter `-` floors negatives → would hide reductions). The two baselines
  come from different engines (Word COM vs the clone); if they DIVERGE, `diff()` reports it in
  `baseline_divergence` and `run.py`/the ledger surface it loudly — the divergence is net into every task's
  delta, so it must be fixed or recorded as a blank-doc finding, never silent. `run.py --capture` captures the
  baselines; `--capture-baseline` refreshes just them; `--no-baseline` falls back to the v1 full-doc diff.
  Proven on the 3 pilots: pagenum `extra` 18→4 (the ListParagraph/numId/numPr demo cluster dropped),
  bold/table findings unchanged; the shipped baselines are signature-identical (divergence empty). Self-validated
  by `review_differ.py`'s GOLDEN-BASELINE suite (5 cases: boilerplate cancels, real `missing`/`extra`/reduction
  survive, divergent baselines flagged). **Probes must start from the SAME clean state as the blank baseline**
  (`selectAll` + insertContent `<p></p>`) so the shared boilerplate cancels exactly — the pagenum probe +
  ground-truth were normalized for this.
- **Noise list:** proven COMPLETE by Word-vs-self (do NOT add `Ignorable` to `NOISE_ATTRS` — a `<w:ftr>`
  WITHOUT `mc:Ignorable` is a real clone fidelity gap, surfaced in the pagenum ledger, not noise).
- 🔜 **Relationship-id (rId) normalization:** node signatures include the `id`/rId attribute, so Word's
  default footer ref (`rId9`) reads as `missing` while the clone's (`rId7`) reads as `extra` even though
  both are the same semantic `type="default"` ref. Word-vs-self is clean (Word reuses rIds deterministically),
  so this only bites cross-tool. Candidate next refinement: canonicalize rId VALUES (like rsid) before
  comparison, keying header/footer refs on `type` not `id`.
- 🔜 **Flow verifier** (separate): DOM-introspect the clone (dropdown/dialog/contextual-tab/items) and
  diff against the `ribbon-data.js` declared `type`/`items[]` — UI-flow fidelity, not OOXML.
