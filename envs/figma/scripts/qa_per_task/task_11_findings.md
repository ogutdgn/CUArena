# Task 11 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_11_extended.py`

## Results

| Round                    | Cases | Strict FPs (≥0.95) |
|--------------------------|-------|---------------------|
| 1 (initial 100-case)     | 100   | 50+ → 20            |
| 3 (novel 24-case)        | 24    | 2                   |

## What was fixed (round 1)

### Primitives reused
- `LayerAreaRatioAtLeast` → geometry_checks.py
- `DistinctTypedSolidColors` → fill_checks.py
- `PolygonSidesEquals` → shape_checks.py (already in original; kept critical)
- `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`, `NoLayerFlipped`

### task_11 critical checks now catch
- A1, A2, A4 (≠3 polygons): `ShapeCount("polygon", equals=3)`
- A6 (extra polygon): `ShapeCount` exact match
- A7, K3 (sides=4): `PolygonSidesEquals(sides=3)`
- A8, A9 (wrong types): `ShapeCount` + `ToolUsed`
- B11, K2 (1 distinct color): `DistinctTypedSolidColors(2)`
- B13, B14 (image/gradient): `AllFillTypeIs("solid")`
- B15 (stacked fills): `FillCountAtMost(1)`
- B16 (no fill): `AllFillTypeIs("solid")`
- B17 (near-identical): tighter tolerance in `DistinctTypedSolidColors`
- B18, B19, B20, J91, J92 (visibility tricks): `LayerVisible` + `FillOpacityAtLeast`
- C21 (all same size): `SmallerLayerInsideLarger` + `LayerAreaRatioAtLeast`
- C23 (tiny <20px): `LayerSizeAtLeast(20, 20)`
- C24 (>frame): `AllLayerBoundsInside`
- C26 (within tol — gentle): `LayerAreaRatioAtLeast(2.0)`
- C27, J99 (1×1, degenerate): `LayerSizeAtLeast`
- D31, D32, D33, D34, D36, D40 (not concentric): `LayersConcentric(tol=10)`
- E41-E50 (rotation): `LayerRotationEquals(polygon, 0)`
- E44, E48, J98 (flipped): `NoLayerFlipped`
- E45 (sides=5): `PolygonSidesEquals(3)`
- F52 (mixed aspects): impossible to enforce all-equilateral; partial via PolygonSides
- F53 (cascade): `LayersConcentric` fails
- F55 (overlapping not concentric): `LayersConcentric` fails
- F57, F58, F59 (not concentric): `LayersConcentric`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`
- G63 (no frame): `LayerInsideFrame`
- I82, I84, I87, I88, I89, I90 (split / wrong-container): `LayerInsideFrame` + `ChildCountAtLeast(3)`

## Round 3 — surviving novel-deception cases

Authored 24 NEW edge cases (`qa_per_task/task_11_round3.py`).

| Case  | What it does                          | Final | Status |
|-------|---------------------------------------|-------|--------|
| K1    | all rotated 1.5° (under 2° tol)       | 1.000 | Borderline (within tol, accepted) |
| K5    | z-order reversed (smallest 1st)       | 1.000 | Known limitation — same-type z-order |

## Critical-flag changes

- Fundamentals: `critical=[0, 1]` (ShapeCount("polygon", equals=3), PolygonSidesEquals(3))
- Alignment: 8 critical (concentric, smaller-inside-larger, polygon rotation, frame
  rotation, size-at-least, bounds-inside, no-flipped, area-ratio)
- Color: 5 critical (all-fill-type, distinct-typed-solid, fill-count, fill-opacity,
  layer-visible)
- Structure: 2 critical (LayerInsideFrame, ChildCountAtLeast=3)
- Event: 2 critical (ToolUsed("polygon"), EventTypeCount(create_polygon, 3))

## Harness handlers added/changed

No new harness handlers required; existing `mutate_for_geometry` already handles
all primitives used. PolygonSidesEquals is satisfied by the existing harness pass.

## Known limitations

- **Same-type z-order**: prompt says "largest at back, smallest at front" but
  this can't be enforced for same-type (all polygon). LayerInFrontOf requires
  cross-type. Z-order tests like K5 (reverse) and F54 (ascending z-order) pass.
- **Sub-tolerance accuracy**: 1.5° rotation, 2px size drift are intentionally
  accepted as "essentially correct".
- **Polygon aspect**: PolygonSidesEquals(3) catches the "must be triangle" rule
  but doesn't enforce equilateral aspect (a 100×50 stretched triangle still
  has 3 sides).
