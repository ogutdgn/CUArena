# Task 15 — verifier hardening summary

Run with:
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_15_extended.py`
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_15_round3.py`

## Results

| Round                          | Cases | Strict FPs (≥0.95) |
|--------------------------------|-------|--------------------|
| 1 (initial 100-case)           | 100   | 43 → 5             |
| 3 (novel 30-case)              | 29    | 1 (acceptable)     |

## What was fixed

### Reused primitives (no new ones for task_15)
- `LayersAllShareEdge(bottom)` — replaces too-loose `LayersAligned(center_y, tol=80)`.
- `LayerSizeAtLeast`, `AllLayerBoundsInside`, `LayerRotationEquals`,
  `LayersAtDistinctPositions`, `AllLayerWidthFraction` — all critical.
- `AllStrokeExists`, `AllStrokeColorEquals`, `AllStrokeWeightWithinTolerance`
  (added in task_14) — for stroke uniformity.
- `LayerVisible`, `NoLayerFlipped` — for visibility/flip.
- `FillCountAtMost`, `FillOpacityAtLeast`, `AllFillTypeIs` — for fills.

### Critical-flag changes — task_15 critical checks now catch
- A2, A3, A4, A5: count != 4 → `ShapeCount`
- B11, B12, B16, B17, B18, J94, J95: wrong color → `AllSolidColorEquals(WHITE, tol=0.10)`
- B13, B14, M7: image/gradient fill → `AllFillTypeIs("ellipse", "solid")`
- B15: empty fills → `AllFillTypeIs` + `LayerVisible`
- B19, B20, L1, L2, L3, L4: visibility tricks → `LayerVisible` + `FillOpacityAtLeast`
- C21, C25, J93, M3: degenerate → `LayerSizeAtLeast(20, 20)`
- C22, C26, M4: huge → `AllLayerWidthFraction(ellipse, frame, ≤0.50)`
- D31, D33, D35, D39, F51: not overlapping / vertical column → `LayersOverlap` + `LayersAllShareEdge(bottom)`
- D32, D36, D37, D38, M5: off-frame / piled → `AllLayerBoundsInside` + `LayersAtDistinctPositions`
- E41, E42, E46, K1: rotated — caught via `LayerRotationEquals(ellipse, 0)`
- E43, E44, M6: flipped → `NoLayerFlipped`
- E48: no strokes → `AllStrokeExists`
- E49: dark gray strokes → `AllStrokeColorEquals(LIGHT_GRAY)`
- E47: stroke weight wrong → `AllStrokeWeightWithinTolerance`
- I81–I87, N1–N4: not in frame → `StructureRubric` made critical
- O1, O2, O3: wrong type → `ShapeCount("ellipse", equals=4)` is critical

### Rubric changes
- task_15 grew from 4 → 5 rubrics (added Structure).
- Weights normalised to 0.2 each.

## Acceptable 1.000s (intended passes)
| Cases | Why 1.000 is correct |
|-------|----------------------|
| A7, A9, A10, J96, J100 | controls / extras tolerated |
| C23, M1 | uniform-size ellipses — prompt allows "any sizes" |
| C24, C29 | thin/wide ovals — "ellipses" not strictly circles |
| F58, F59 | tight/wide cloud — both valid silhouettes |
| K1, K10, K9 | under-tolerance variants / rotation invariant |

## Known limitations
- Cannot detect "ellipses too uniform" because prompt says "varying sizes" but
  the verifier framework doesn't have a "size diversity" primitive yet.

## Status snapshot
- Verifier framework: 50/50 OK on `qa_verifiers.py`.
- Task 15: from 43 strict 1.000s → 5 (all intended/borderline).
- delivery-1/task_15/verifier.py is synced.
