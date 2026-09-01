# Task 12 — verifier hardening summary

Run with:
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_12_extended.py`
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_12_round3.py`

## Results

| Round                          | Cases | Strict FPs (≥0.95) | Real FPs (genuine defects) |
|--------------------------------|-------|--------------------|----------------------------|
| 1 (initial 100-case)           | 100   | 65 → 27            | ~35 → ~3                   |
| 3 (novel 30-case)              | 29    | 4                  | 0 (all sub-tolerance)      |

## What was fixed

### New primitives added
- `LayersHaveConsistentGap(layer_type, axis, min_gap, variance_tolerance)` → geometry_checks.py
  - Catches overlapping piles (zero/negative gaps) AND inconsistent spacing.
  - Distinct from `LayersStacked` (exact gap_px) and `LayersDistributed`
    (variance only — passes when all gaps are 0).

### Critical-flag changes — task_12 critical checks now catch
- A overlapping pile / column-shaped layout: `LayersHaveConsistentGap`
- D34, D38, D39, F51, F52: all gap-related defects → `LayersHaveConsistentGap`
- C26, C30: tiny/degenerate rects → `LayerSizeAtLeast(min_w=15, min_h=15)`
- C21, C26: way-too-big rects → `AllLayerWidthFraction(rectangle, frame, ≤0.40)`
- D31, D32, D35: row-of-y-staircase → `LayersAllShareEdge(top/bottom)` + `LayersAligned(center_y)`
- D36, D37, J95: row off-frame → `AllLayerBoundsInside(rectangle, frame)`
- E41–E48, K1, K2: rotation defects → `LayerRotationEquals(rect, 0, tol=2.0)`
- E45, E50, K3, K10: pill/circle rects → `CornerRadiusFractionAtMost(rect, 0.4)`
- E43, E44, J94, M6: mirror/flip → `NoLayerFlipped(rectangle)`
- B12, B13, M7: image/gradient fill → `AllFillTypeIs(rect, "solid")`
- B14, B15: stroke-only / empty fills → same
- B16, B17, B18, B19, L1–L4: visibility tricks → `LayerVisible(rectangle)` + `FillOpacityAtLeast`
- B20: stacked fills → `FillCountAtMost(rectangle, 1)`
- I81–I87, N1, N2, N3, N4: not-in-frame / split frames → `StructureRubric` made critical
- G61: frame rotated → `LayerRotationEquals(frame, 0)`
- O1, O2, O3: wrong type → `ShapeCount("rectangle", equals=4)` is critical

### Harness handlers added/changed
- Added `LayersHaveConsistentGap` handler (Pass 2) in `qa_verifiers.py`.
  Mimics `LayersStacked` handler with healthy positive gap derived from `min_gap + 4`.

### Rubric changes
- Added `StructureRubric` (frame/inside-frame nesting) — was missing before.
- Promoted from 4 rubrics → 5 rubrics, weight 0.2 each.

## Acceptable 1.000s (intended passes)
| Cases | Why 1.000 is correct |
|-------|----------------------|
| D40, J96, J100 | perfect row controls |
| B11 | uniform gray fill — prompt allows any solid fill |
| C28 | w=122 within tolerance=3 of 120 |
| C29 | w=125 across all 4 — same-size satisfied |
| F56, F57 | tall/wide rects — no aspect requirement |
| F58, F59 | row near top/bottom edge — no vertical centering required |
| G62, G64–G67, G70 | frame variants (frame size/styling not strict) |
| G63 | row in 2nd frame — verifier walks all frames |
| H73, H76, H77, H80 | event-log extras — efficiency penalty applies but base is full |
| I84, I85 | nested frames / multi-page — verifier walks |
| J99 | rects 3 & 4 same color — prompt has no distinct-color requirement |
| K1, K2 | rotations under 2° tolerance — explicit tolerance band |
| K3 | cornerRadius=48 = 0.40 of size — at threshold |
| K5 | reverse z-order — adjacent non-overlapping rects, z-order moot |

## Borderline (extras tolerated)
| Case | Score | Note |
|------|-------|------|
| A6 | 1.000 | extra ellipse (rect count still 4) |
| A10 | 1.000 | extra polygon (rect count still 4) |

These "extra-shape" cases are tolerated per playbook convention — the prompt
specifies "4 rectangles" not "ONLY 4 rectangles".

## Known limitations
- Cannot detect "ultra-wide thin" (e.g. 280×30) as a defect because the prompt
  doesn't pin aspect ratio.
- Same-color/uniform color across all 4 rects passes (no distinct-color requirement).

## Status snapshot
- Verifier framework: 50/50 OK on `qa_verifiers.py`.
- Task 12: from 65 strict 1.000s → 27 (mostly intended), with all real defect
  classes covered by critical checks.
- delivery-1/task_12/verifier.py is synced.
