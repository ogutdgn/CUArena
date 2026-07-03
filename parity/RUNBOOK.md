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
whether **baseline subtraction** is ON (delta-vs-empty-doc) or OFF (v1 full-doc). `--only <id>` **merges**
its result into the aggregate ledger (it does NOT clobber the other tasks' rows), so the develop-phase
acceptance gate can re-run one task repeatedly without wiping the ledger.

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
  any leak is, by definition, noise to add to `NOISE_ATTRS`). Capture pairs into `selftest/rw-<id>-a/b.docx`.
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
- ✅ **Relationship-id (rId) normalization (DONE):** rId VALUES (`r:id="rId9"`, `r:embed="rId4"`…) are
  per-doc relationship pointers assigned arbitrarily per save — Word emits `rId9` where the clone emits
  `rId7` for the SAME semantic reference. `meaningful_attrs` canonicalizes any `^rId\d+$` value to `rId#`
  (kept as an attribute, not dropped — so a clone that DROPS the relationship entirely still surfaces), so
  references match on their real discriminator (e.g. footerReference `w:type`). Removed the pagenum artifact
  where the default footer ref read as BOTH `missing` (Word rId9) and `extra` (clone rId7); pagenum 18/4 → 17/3.
  Locked by golden cases `rid_canon` (same ref, different rId → 0 diff) + `rid_type_differs` (different `type`
  → still surfaces).
- ✅ **Numbering-index (numId) canonicalization (DONE):** `<w:numId w:val>` / `<w:abstractNumId w:val>` are
  per-doc numbering indices assigned arbitrarily (Word's fresh list = numId 1; the clone's = numId 4 because
  its template predefines a few) — the same opaque-pointer class as rId. `meaningful_attrs` folds the VALUE to
  `#` (but NOT `w:ilvl`, the list level, which is meaningful). Removed the bullets phantom (`missing numId[1]` /
  `extra numId[4]`); bullets 2/4 → 1/3, leaving the real gap `missing pStyle[ListParagraph]`. Locked by golden
  `numid_canon` (numId 1-vs-4 → 0 diff) + `ilvl_not_canon` (level 0-vs-1 → still surfaces). **Limitation:** this
  is a document.xml-only view — it does NOT resolve numId → abstractNum → numFmt, so it cannot tell a bullet from
  a numbered list (needs numbering.xml resolution — see below).
- 🔜 **rFonts attribute-subset matching:** node signatures key on the FULL sorted attribute-tuple, so when the
  clone emits `rFonts[ascii,hAnsi,cs,eastAsia]` and Word emits `rFonts[ascii,hAnsi]`, the differ fabricates a
  PHANTOM `missing rFonts[ascii,hAnsi]` alongside the real `extra` (the clone already emits ascii+hAnsi). The real
  delta is the cs/eastAsia over-spec. Candidate: attribute-level/subset matching for multi-attr property elements
  (rFonts, ind, spacing…) so an attribute-set superset reads as "extra attrs", not a missing+extra pair.
- ✅ **numbering.xml + styles.xml now DIFFED (part-scope extension, DONE):** `part_kind` adds `word/numbering.xml`
  → `numbering` and `word/styles.xml` → `styles`, so list/bullet definitions (Define New Bullet/Number Format) and
  style definitions (Create/Modify a Style) are caught. Per-save `<w:rsids>`/`<w:rsid>` bookkeeping is stripped via
  `NOISE_ELEMENTS` (the leak the reviewer's "add `val` to NOISE_ATTRS" would have over-stripped). The baseline-
  divergence guard EXCLUDES `styles:`/`numbering:` (the clone's default templates legitimately differ from Word's;
  per-task deltas still cancel them). Locked by golden `numbering_part`/`styles_part` + Word-vs-self on the new parts.
  **CONSEQUENCE:** bullets/numbering now show a large `numbering.xml` delta that is a COM-method ARTIFACT — COM
  `ApplyBulletDefault`/`ApplyNumberDefault` writes a singleLevel abstractNum, the ribbon (and the clone) write a
  MULTIlevel one, so the clone reads as "extra" while being MORE ribbon-faithful than the COM ground truth. A true
  numbering.xml comparison for these needs the **vsto/UIA ribbon ground-truth** (deferred).
- 🔜 **numId → numFmt RESOLUTION:** even with numbering.xml diffed, the differ compares definitions structurally, not
  by list KIND. Resolving `numId` → its abstractNum `numFmt` (bullet vs decimal vs …) would let same-KIND lists match
  regardless of definition shape — the principled successor to the current numId-value canonicalization.
- 🔜 **Sibling-order sensitivity:** node signatures are multiset counts keyed on tag+attrs, so a WRONG CHILD
  ORDER is invisible. The T1 numbering task surfaced the clone emitting `<w:numPr>` children as `numId` then
  `ilvl` (OOXML/Word use `ilvl` then `numId`) — a real clone bug the differ does NOT flag. Candidate: an
  order-aware check for ordered-content elements (numPr, rPr, pPr) where OOXML mandates a child sequence.
- 🔜 **Flow verifier** (separate): DOM-introspect the clone (dropdown/dialog/contextual-tab/items) and
  diff against the `ribbon-data.js` declared `type`/`items[]` — UI-flow fidelity, not OOXML.

### T1 develop backlog (from the parity ledger)
- **Lists miss `pStyle=ListParagraph`** — both `bullets` AND `numbering` clone paragraphs omit the `ListParagraph`
  paragraph style real Word attaches to every list item. One clone fix closes both. (+ the numPr child-order bug above.)
- **`highlight` ground truth = COM artifact (vsto-pending)** — COM `HighlightColorIndex` stamps the highlight on the
  paragraph mark; the ribbon doesn't. The clone is faithful (real parity 0/0). Recapture via vsto/UIA when the
  contextual-tab UIA inventory is built (joins `table` + `bullets`/`numbering` as the COM≠ribbon set).
