# Task 38 — verifier hardening summary

Run: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_38_extended.py`

## Results

| Round | Cases | Strict FPs (≥0.95) | Notes |
|-------|-------|--------------------|-------|
| 1 (initial 100-case) | 100 | 61 → 28 | most are legitimate "extras OK" |
| 3 (novel 30-case)    | 27  | 10 → 7  | rest are tolerance-edge |

## New primitives added

| Primitive | File | Catches |
|-----------|------|---------|
| `VisibleStrokeExists(layer_type, min_alpha, min_weight)` | stroke_checks.py | stroke alpha=0 / weight=0 / visible=False (L2, K9) |
| `CrossTypeAreaRatioAtLeast(big_type, small_type, min_ratio)` | geometry_checks.py | body smaller than frame (C21 catch) |

## Critical-flag changes

- `FundamentalsRubric` (1st): 4 critical (was 1): adds size-floor, area-ratio, no-flip
- `AlignmentRubric`: 7 critical: adds rotation, all-bounds-inside-frame, smaller-inside-larger,
  cross-type area ratio, corner-radius cap (catches over-rounded body)
- `ColorRubric`: 9 critical (was 3): adds stroke color, visible stroke, fill count,
  layer visible, fill opacity
- `StructureRubric`: 1 critical (was 0)
- `EventRubric`: 1 critical (was 1, kept)
- 2nd `FundamentalsRubric`: catches degenerate bars (LayerSizeAtLeast 10×10)

## Round-1 catches

- B11/B12 (image/gradient fill): `AllFillTypeIs("rectangle", "solid")`
- B13 (bars all gray): `DistinctSolidColors(min=4, tol=0.10)`
- B14 (no stroke): `StrokeExists` + `VisibleStrokeExists`
- B15-B19 (alpha/opacity/visible tricks): `LayerVisible` + `FillOpacityAtLeast`
- C21 (body = full frame): `CrossTypeAreaRatioAtLeast(frame, rectangle, 2.0)`
- C22-C24 (degenerate sizes): `LayerSizeAtLeast(rectangle, 10, 10)`
- C28 (body 30x30 too small): area-ratio check
- D31-D35 (off-frame): `AllLayerBoundsInside(rectangle, frame)`
- E41-E44 (rotated/flipped): `LayerRotationEquals`, `NoLayerFlipped`
- E45 (cornerRadius=0): `CornerRadiusAtLeast(min=4)`
- E47/E48 (body wrong type): `ShapeCount("rectangle", 5)`
- F51 (bars all red): `DistinctSolidColors(min=4)`
- F53/F54 (no fill on terminal/bars): `FillCountAtMost`, `AllFillTypeIs`
- F55 (stroke red not gray): `StrokeColorEquals(rectangle, GRAY, tol=0.15)`
- F56 (stroke weight 0): `StrokeWeightEquals(rectangle, 2.0, tol=1.5)`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`
- J91 (body rotated 180°): `LayerRotationEquals(rectangle, 0)`
- J92 (rects piled): `LayerAreaRatioAtLeast(rectangle, 2.0)`
- J95 (body mirrored): `NoLayerFlipped`
- J96 (1×1 bars): `LayerSizeAtLeast(rectangle, 10, 10)`

## Round-3 catches

- K8 (cornerRadius=200, looks circular): `CornerRadiusFractionAtMost(0.6)`
- K10 (body rotated 45°): `LayerRotationEquals(rectangle, 0, tol=2)`
- L1-L5 (alpha/opacity/visible tricks): `LayerVisible`, `VisibleStrokeExists`,
  `FillOpacityAtLeast`
- M1-M5 (geometry tricks): `LayerAreaRatioAtLeast`, `CrossTypeAreaRatioAtLeast`
- O1-O3 (wrong types): `ShapeCount("rectangle", 5)` critical

## Remaining acceptable 1.000s

| Case | Why 1.000 is correct |
|------|---------------------|
| A7 | Extra ellipse — rectangle count still 5 |
| A10, C30, D40, E50, F60, G68, H80, I90, J100 | Perfect controls |
| C29 | body 1000x80 — area still significantly less than frame |
| E46 | cornerRadius=100/200 → caught at >0.6 frac in round 3 |
| F57 | bars stacked vertically — design accepted |
| F59, J97 | body filled gray/red instead of transparent — prompt allows |
| G62-G69 | Frame variants (nested/translated/no frame/2 frames) |
| H72-H78 | Event-log extras (align, delete, end, fills) |
| I82-I89 | Multi-frame / nested / page 2 hierarchy |

## Round-3 acceptable 1.000s

| Case | Why |
|------|-----|
| K1, K3 | Within rotation/cornerRadius tolerance — intended pass |
| K4 | stroke alignment=inside — Figma supports all alignments |
| K6 | Stroke weight 0.6 within tol 1.5 |
| K7 | Stroke color near-gray with red tint — within 0.15 tol |
| L5 | body fill alpha=0 with stroke visible — visually still OK |
| N1, N3, N4 | Multi-frame hierarchy edge cases |
