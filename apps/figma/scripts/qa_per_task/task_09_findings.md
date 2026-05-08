# Task 09 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_09_extended.py`

## Results

| Round                    | Cases | Strict FPs (≥0.95) |
|--------------------------|-------|---------------------|
| 1 (initial 100-case)     | 100   | 50+ → 24            |
| 3 (novel 21-case)        | 21    | 4                   |

## What was fixed (round 1)

### Primitives reused
- `LayerAllSquare` → geometry_checks.py (newly added by parallel agent; used here)
- `DistinctTypedSolidColors` → fill_checks.py (added in task_07 work; reused)

### task_09 critical checks now catch
- A1, A3, A5 (wrong rect counts): `ShapeCount("rectangle", equals=12)`
- A6, J96 (wrong types — ellipses/stars instead of rects): `ShapeCount` + `ToolUsed`
- B11, B12, B13 (color count <12): `DistinctTypedSolidColors(rectangle, 12)`
- B14, B15, B16 (image/gradient/no fill): `AllFillTypeIs(rectangle, "solid")`
- B17 (stroke-only no fill): `AllFillTypeIs("solid")` fails
- B18 (stacked fills): `FillCountAtMost(1)`
- B19, B20, J91, J92 (visibility tricks): `LayerVisible` + `FillOpacityAtLeast`
- C22, C28 (degenerate sizes): `LayerSizeAtLeast(15, 15)`
- C24, C25 (non-square rects): `LayerAllSquare`
- C26 (1 outlier size): `LayersSameDimensions`
- C30 (mixed sizes): `LayersSameDimensions`
- D31, D32, D33, D34, D35, D40 (not 4x3 grid): `LayersInGrid(3, 4, tol=10)`
- D37, J97 (off-frame): `AllLayerBoundsInside(rectangle, frame)`
- E41, E42, E43, E49, E50 (rotation): `LayerRotationEquals(rectangle, 0)`
- E44, J98 (flipped): `NoLayerFlipped(rectangle)`
- E45 (cornerRadius=40, looks circular): `CornerRadiusFractionAtMost(0.4)`
- F51 (mixed shapes): `LayerAllSquare`
- F52 (mixed sizes): `LayersSameDimensions`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`
- G66 (no frame): `LayerInsideFrame("rectangle")` + `ChildCountAtLeast`
- I82, I84, I87, I88, I89, I90 (split / wrong-container): `LayerInsideFrame` + `ChildCountAtLeast(12)`

## Round 3 — surviving novel-deception cases

Authored 21 NEW edge cases (`qa_per_task/task_09_round3.py`).

| Case  | What it does                          | Final | Status |
|-------|---------------------------------------|-------|--------|
| K1    | all rotated 1.5° (under 2° tol)       | 1.000 | Borderline (within tol, accepted) |
| K3    | all cornerRadius=20 (rounded squares) | 1.000 | Acceptable — still squares-with-corners |
| K5    | all 79×80 (within 2px tol)            | 1.000 | Within tol — correct pass |
| M5    | frame rotated 1.5° (under tol)        | 1.000 | Within tol — correct pass |

## Critical-flag changes

- Fundamentals: `critical=[0]` (ShapeCount("rectangle", equals=12))
- Alignment: 9 critical (same-dims, in-grid, all-square, rect rotation, frame rotation,
  size-at-least, bounds-inside, no-flipped, corner-radius-fraction)
- Color: 5 critical (all-fill-type, distinct-typed-solid, fill-count-at-most,
  fill-opacity-at-least, layer-visible)
- Structure: 2 critical (LayerInsideFrame, ChildCountAtLeast=12)
- Event: 2 critical (ToolUsed("rectangle"), EventTypeCount("create_rectangle", 12))

## Harness handlers added/changed

- Extended `DistinctTypedSolidColors` palette in `qa_verifiers.py` from 8 to 16
  colors so the perfect log can satisfy `DistinctTypedSolidColors(rectangle, 12)`.

## Known limitations

- **Sub-tolerance rotation/sizing**: 1.5° rotation, 1px size diff fall under
  tolerance and are intentionally accepted.
- **CornerRadius 20 on a 80×80 square**: 25% radius — visually still reads as a
  square with rounded corners. The 0.4 max threshold is intentionally lenient
  (only catches >40% which clearly looks circular).
