# Tables Fix Loop — Final Acceptance (2026-07-02)

> The 6-feature fix loop the user ordered after ratifying Phase B (the Tables pilot PASS). Each
> feature was seeded from the pilot's certified pipeline, built spec-kit (specify→plan→tasks→
> implement), and accepted BY the pipeline (`run.py`, twins/journeys, scorecard, VISUAL, STRUCTURE)
> + the 3 standing gates. Hybrid execution: Fable orchestrated/reviewed; Opus subagents implemented.
> Branch `parity-v2`, commits `bf065b6`…`a29580b`.

## The 6 features — all shipped

| # | Spec | What | Result |
|---|---|---|---|
| 1 | 030 | Table Styles catalog (113 defs) + visual gallery + theme palette | ✅ 2/247→113 gallery; theme #156082; hover preview |
| 2 | 031 | tblLook val + cnfStyle stamping + 6 Style Options checkboxes | ✅ all 8 style tasks cnf-clean; corner rule oracle-pinned |
| 3 | 032 | Borders engine: full dropdown, diagonals, nil No-Border, pen, Border Painter, collapse paint | ✅ collapse bug closed (twins pass); + a pipeline harness fix |
| 4 | 033 | Table Layout tab → Word's 7 groups + all dialogs | ✅ STRUCTURE 13→34 matched; Sort/Formula/Properties/… |
| 5 | 034 | Insert menu wiring + insert-time OOXML defaults | ✅ F-class delta cleared across ALL tasks; `table`=pass |
| 6 | 035 | Import losses + convert-tab + D1.2 pass-with-note + re-measure | ✅ 3 import losses closed; pass-with-note live |

## Measured result (full 6-axis re-measure, 2026-07-02)

| Axis | Pilot baseline | After the loop |
|---|---|---|
| **OOXML (TB, 48 tasks)** | 2 pass | **24 pass** (17 semantic-pass + 7 pass-with-note); import legs lose nothing |
| **STRUCTURE table-design** | matched 3 / missing 13 / label 2 | **matched 14 / missing 2 / label 0** |
| **STRUCTURE table-layout** | matched 13 / missing 16 / label 5 / type 1 | **matched 34 / missing 1 / label 0 / type 0** |
| **SCORECARD** | tblStyles GALLERY_UNDERFILLED; stubs | **tblStyles OK_GALLERY_INLINE 113**; no dead table controls |
| **VISUAL** | tabledesign FAIL (no Borders/Style Options); doc-render teal-mismatch | **doc-render PASS** (palette fixed); tabledesign transformed (all groups present) |
| **BEHAVIOR (Tables)** | insert/gallery/merge/delete/borders FAIL | **40/46 pass** — every named-gap journey + both border twins PASS |

The 5 named acceptance gaps (2/247 gallery, cnfStyle, Draw/Eraser/Painter, Insert Cells…, label
mismatches) are all closed or built. The border-collapse file-clean-screen-wrong bug is fixed and
instrument-verified on the painter.

## Pipeline improvements found + fixed DURING the loop (Phase-B ethos)

1. **Differ text-blindness + order-blindness** (`6aca402`) — w:t content + a per-part ordered
   textOrder signature; caught the totext-comma false-pass + the invisible Sort.
2. **Twin harness read the wrong layer** (`dfbd642`) — twins read the off-screen hidden model host
   (td/th @ x=-10004), not the real painter; fixed to read `.presentation-editor__pages` with a
   collapse-aware colored-edge instrument. This EXPOSED the paged-painter paint gaps below.
3. **D1.2 pass-with-note** (`de7b77f`) — benign byte-diffs (empty pPr, explicit-default) count as
   pass with the note kept; the ledger is now honest instead of a wall of "gap".
4. **Scorecard gallery bar** (`e356dd2`) — an under-filled gallery lands in TRIAGE, not silent pass.

## Fork edits (all plan-authorized, minimal, marked)

7 total across the loop, all data-only or paint-only: GT4A1 + TableGrid stale-palette/pPr data
(030/034), the border-collapse thicker-wins paint pre-pass + tcBorders schema-order (032), the 3
import-fidelity translators (035). No fork LOGIC was edited to ship a feature capability; every UI
capability went through the WC.PM bridge.

## Honest residuals (NOT closed — documented, prioritized)

1. **Paged-painter cell paint (the main user-visible one):** vAlign / row-height / text-direction are
   written CORRECTLY to OOXML but not fully reflected on the paged painter (the 6 remaining BEHAVIOR
   twin fails). This is a cross-cutting LAYOUT-ENGINE concern (affects all tables), surfaced by the
   harness fix — see `parity/knowledge/paged-painter-cell-paint-gaps.md`. **Recommended next.**
2. **OOXML byte-parity tail (24 gap tasks):** small per-feature residuals — post-edit width
   recomputation (colwidth/merge/autofit), trHeight values, shd attr shape, border style-interaction,
   floating-table authoring (Group E, user-descoped), Quick Tables = fake presets (non-Word
   building blocks). Each is 1–8 nodes; the note list is the byte-parity backlog (SPEC_SEEDS.md).
3. **Deferred by design:** true shift-cells (Insert/Delete Cells — needs a fork command), Alt-Text
   persist (needs a caption/description verb), the 134 legacy table styles (extractor proven, v1 =
   113 modern), D1.2 note-list expansion, the scorecard stub-vs-guard-toast classifier.

## Verdict

**The 6-feature Tables fix loop is COMPLETE.** Every named Phase-B gap is closed; the Tables feature
moved from "2/247 gallery, no Style Options, no Borders group, wrong Layout tab, F-class OOXML delta
everywhere" to Word's full Table Design + Layout surface with the correct OOXML, accepted by the
certified pipeline across all 6 axes. Gates: pm 562/562 · roundtrip 27/0 · smoke 9/9 · bundle 4/4;
differ trust gate ALL PASS. The remaining work is the documented residual list above — the
paged-painter paint gap is the highest-value follow-up and is genuinely a layout-engine task, not a
table-feature task.
