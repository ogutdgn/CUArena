# Task 10 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_10_extended.py`

## Results

| Round                    | Cases | Strict FPs (≥0.95) |
|--------------------------|-------|---------------------|
| 1 (initial 100-case)     | 100   | 50+ → 1             |
| 3 (novel 23-case)        | 23    | 1                   |

## What was fixed (round 1)

### Primitives reused
- `LayerAllSquare` → geometry_checks.py
- `DistinctTypedSolidColors` → fill_checks.py
- `LayerAreaRatioAtLeast` → geometry_checks.py (existing — used to enforce outer >> inner)
- `CornerRadiusFractionAtMost` → property_checks.py

### task_10 critical checks now catch
- A1, A2, A3 (≠4 squares): `ShapeCount("rectangle", equals=4)`
- A4, A6 (extras): `ShapeCount` exact match
- A8 (ellipses): `ShapeCount` + `ToolUsed`
- B11, K5 (all same color): `DistinctTypedSolidColors(rectangle, 2)`
- B13, B14 (image/gradient): `AllFillTypeIs("solid")`
- B15 (stacked fills): `FillCountAtMost(1)`
- B17 (near-identical colors): tighter `DistinctTypedSolidColors`
- B18, B19, B20, J91, J92 (visibility tricks): `LayerVisible` + `FillOpacityAtLeast`
- C21 (all same size): `SmallerLayerInsideLarger` + `LayerAreaRatioAtLeast`
- C22 (increasing size): `SmallerLayerInsideLarger` (largest must contain smaller)
- C23 (sizes within 6px): `LayerAreaRatioAtLeast(2.0)` enforces outer ≥ 2x inner
- C24 (tiny <20px): `LayerSizeAtLeast(15, 15)`
- C25 (1500x1500 outer): `AllLayerBoundsInside(rectangle, frame)`
- C26, C27 (rectangular not square): `LayerAllSquare`
- C28 (gentle 80% step): `LayerAreaRatioAtLeast(2.0)`
- C30 (1×1 inner): `LayerSizeAtLeast`
- D31-D40 (not concentric): `LayersConcentric(tolerance=8)`
- E41-E50 (rotation): `LayerRotationEquals(rectangle, 0)`
- E44, J98 (flipped): `NoLayerFlipped`
- E45 (50% cornerRadius — circles): `CornerRadiusFractionAtMost(0.4)`
- F51 (sizes shuffled): `SmallerLayerInsideLarger` + `LayerAreaRatioAtLeast`
- F52 (rect aspect): `LayerAllSquare`
- F53 (4 piled): `SmallerLayerInsideLarger` requires distinct sizes
- F55 (barely-decreasing): `LayerAreaRatioAtLeast(2.0)`
- F59, K5 (1 distinct color): `DistinctTypedSolidColors(2)`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`
- G63 (no frame): `LayerInsideFrame`
- I82, I84, I87, I88, I89, I90 (split / wrong-container): `LayerInsideFrame` + `ChildCountAtLeast(4)`

## Round 3 — surviving novel-deception cases

Authored 23 NEW edge cases (`qa_per_task/task_10_round3.py`).

| Case  | What it does                          | Final | Status |
|-------|---------------------------------------|-------|--------|
| M4    | aggressive 2x nesting (400/200/100/50)| 1.000 | Acceptable — meets all design requirements |

## Critical-flag changes

- Fundamentals: `critical=[0]` (ShapeCount("rectangle", equals=4))
- Alignment: 9 critical (concentric, smaller-inside-larger, all-square, rect rotation,
  frame rotation, size-at-least, bounds-inside, no-flipped, area-ratio)
- Color: 6 critical (all-fill-type, distinct-typed-solid, fill-count, fill-opacity,
  layer-visible, corner-radius)
- Structure: 2 critical (LayerInsideFrame, ChildCountAtLeast=4)
- Event: 2 critical (ToolUsed("rectangle"), EventTypeCount(create_rectangle, 4))

## Harness handlers added/changed

- Extended palette in `DistinctTypedSolidColors` handler.
- Existing `LayersConcentric` handler now respects `LayersSameDimensions` flag
  (parallel agent change) — if same-dimensions also required, doesn't shrink
  layers progressively.

## Known limitations

- **Same-type z-order**: prompt says "largest at back, smallest at front" but
  this can't be enforced for same-type (both rectangle). LayerInFrontOf requires
  cross-type. F54 (smallest-to-largest in z-order) and K2 (z-order reversed) are
  caught only via `SmallerLayerInsideLarger` size-order constraint; some z-swap
  cases pass.
- **Sub-tolerance accuracy**: 1.5° rotation, 7px off-center, 3px size drift are
  intentionally accepted as "essentially correct".
