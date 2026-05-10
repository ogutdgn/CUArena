# Task 16 — verifier hardening summary

Run with:
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_16_extended.py`
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_16_round3.py`

## Results

| Round                          | Cases | Strict FPs (≥0.95) |
|--------------------------------|-------|--------------------|
| 1 (initial 100-case)           | 100   | 57 → 22            |
| 3 (novel 30-case)              | 29    | 7 (all acceptable) |

## What was fixed

### Reused primitives (no new ones for task_16)
- `LayerSizeAtLeast`, `AllLayerBoundsInside`, `LayerRotationEquals`,
  `AllLayerWidthFraction`, `CrossTypeAreaRatioAtLeast` — all critical.
- `AllStrokeExists`, `AllStrokeColorEquals`, `AllStrokeWeightWithinTolerance`
  (added in task_14) — for stroke uniformity.
- `CornerRadiusFractionAtMost(0.4)` — catches "bubble cornerRadius too high"
  (basically a pill, not rounded rect).
- `LayerVisible`, `NoLayerFlipped` — for visibility/flip.
- `FillCountAtMost`, `FillOpacityAtLeast`, `AllFillTypeIs` — for fills.
- `PolygonSidesEquals(3)` — "triangle" tail explicit.

### Critical-flag changes — task_16 critical checks now catch
- A2, A3, A5: count != 1 rect / 1 poly → `ShapeCount`
- A1, A4, A6, A8, A10: extra/missing → `ShapeCount` (already there)
- B11–B17, B19, B20, J95: wrong color / invisible → `AllSolidColorEquals`,
  `LayerVisible`, `FillOpacityAtLeast`
- B12, B14: image / gradient → `AllFillTypeIs(rect/poly, "solid")`
- B15: empty fills → `AllFillTypeIs` + `LayerVisible`
- B18: 1 stroke missing → `AllStrokeExists`
- C21–C23, C25, C26, J93: degenerate → `LayerSizeAtLeast`
- C22, J97: bubble = full frame → `AllLayerWidthFraction(rect, frame, ≤0.80)`
- C24, C30, M4, M5: tail too big → `CrossTypeAreaRatioAtLeast(rect, poly, 3)`
- C28, C29: bubble too thin → `LayerSizeAtLeast` + width-frac
- D31, D34, D35, D39, J98: tail not overlapping bubble → `LayersOverlap` (was there)
- D32, D33, J95: off-frame → `AllLayerBoundsInside(rect/poly, frame)`
- E41, E42: cornerRadius missing/low → `CornerRadiusAtLeast(8)` (was there)
- E43, E44, O3: wrong polygon sides → `PolygonSidesEquals(3)`
- E45, F57, K3: bubble rotated → `LayerRotationEquals(rect, 0, tol=2)`
- E47, K9: tail rotated → `LayerRotationEquals(polygon, 0, tol=2)`
- E46, E48, J94, M6: flipped → `NoLayerFlipped(rect/poly)`
- E50, F59, J99, K8: cornerRadius extreme → `CornerRadiusFractionAtMost(0.4)`
- F51: no strokes → `AllStrokeExists` (rect & poly)
- F52, F53: stroke weight wrong → `AllStrokeWeightWithinTolerance(2, 1)`
- F54: stroke color wrong → `AllStrokeColorEquals(DARK_GRAY)`
- I81–I87, N1–N4: not in single frame → `StructureRubric` made critical
- O1, O2: wrong type → `ShapeCount` enforces 1 rect + 1 polygon

### Rubric changes
- task_16 grew from 4 → 5 rubrics (added Structure).
- Weights normalised to 0.2 each.

## Acceptable 1.000s (intended passes)
| Cases | Why 1.000 is correct |
|-------|----------------------|
| A7, A9, J96, J100 | controls / extras tolerated |
| D37, D38 | tail at top-left or bottom-right — prompt only suggests "bottom-left" |
| F55, F56 | stroke alignment / dashed — prompt is silent |
| G62, G63, G64, G65, G67, G70 | frame variants |
| H73, H76, H80 | event-log extras |
| H77 | created+deleted polygon (efficiency penalty applied) |
| I84, I85 | nested / page-2 |
| K1 | cornerRadius=8 at min — at boundary |
| K4, K5, K6 | params at tolerance boundary |
| K7 | reverse z-order — overlapping shapes still both visible |
| K10 | tail at same point as bubble (overlapping fully) |

## Known limitations
- Cannot detect "tail at center of bubble" vs "tail at edge" without a
  positional pinning primitive — `LayersOverlap` doesn't care about edge proximity.

## Status snapshot
- Verifier framework: 50/50 OK on `qa_verifiers.py`.
- Task 16: from 57 strict 1.000s → 22 (mostly intended/borderline).
- delivery-1/task_16/verifier.py is synced.
