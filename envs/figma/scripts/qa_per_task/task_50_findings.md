# Task 50 — verifier hardening summary

Task: 1 large square + 1 5-point star centered on top, contrasting fills, 4px white stroke on star.

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_50_extended.py`

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | ~56 → 39 |
| 3 (novel 30-case) | 31 | — → 9 |

(Round-1 1.000 surfacers: control cases A9/J100/G68/I88/I90, "cover + extra
shape" decorative cases A6/A10/F60, frame-wrapping variants G61–G70/I81–I89,
event-log extras H72–H80, hierarchy variants J94/I82/I87.)

## What changed

Task 50 was originally 4 rubrics, ~7 critical checks. Now 4 rubrics, 30
critical checks across ~32 total checks.

| Old | New |
|-----|-----|
| `LayerBoundsInside` | + `LayerSmallerThanLayer(star, rectangle, 0.85)` for size disambiguation |
| (no shape constraint) | + `LayerIsSquare(rectangle, tol=10)` (the prompt says SQUARE) |
| (no rotation) | + `LayerRotationEquals` for both shapes |
| (no flip check) | + `NoLayerFlipped` for both |
| (no min size) | + `LayerSizeAtLeast` for both |
| (no max size) | + `LayerShortDimensionAtMost(rect, 2000)` |
| (no innerRatio) | + `StarInnerRatioEquals(0.4, tol=0.3)` |
| `StrokeExists` | `AllStrokeExists` (catches missing) |
| `StrokeColorEquals` | `AllStrokeColorEquals` (every stroke white) |
| (no z-order) | + `LayerInFrontOf(star, rectangle)` |
| (no corner-radius cap) | + `CornerRadiusFractionAtMost(rect, 0.4)` (catches round-rect) |
| (no visibility) | + `LayerVisible(rectangle)` + `LayerVisible(star)` |
| (no fill caps) | + `FillCountAtMost(1)` for both |
| (no opacity floor) | + `FillOpacityAtLeast(0.5)` for both |

## New primitives leveraged

| Primitive | Catches |
|-----------|---------|
| `LayerSmallerThanLayer(star, rectangle, 0.85)` | M2: star bigger than square |
| `LayerShortDimensionAtMost(rectangle, 2000)` | C26/M8: huge rectangle |
| `LayerIsSquare(rectangle, tol=10)` | C22/C23/M3: rectangle not actually square |
| `CornerRadiusFractionAtMost(rectangle, 0.4)` | O4: rectangle with rounded-circle corners |

## Caught by new checks (round-1+3 examples)

| Case | Old | New | Caught by |
|------|-----|-----|-----------|
| B16   | 1.000 | ~0.86 | FillOpacityAtLeast |
| B17   | 1.000 | ~0.86 | LayerVisible (alpha) |
| B18   | 1.000 | ~0.86 | LayerVisible (opacity) |
| B19   | 1.000 | ~0.86 | LayerVisible (visible flag) |
| B20   | 1.000 | ~0.86 | FillCountAtMost(1) |
| C21–C24 | 1.000 | ~0.85 | LayerSizeAtLeast / LayerIsSquare |
| C28/C29 | 1.000 | ~0.85 | LayerSizeAtLeast |
| D31/D32 | 1.000 | ~0.86 | LayerCenteredOnLayer |
| E44/E45 | 1.000 | ~0.86 | LayerRotationEquals(star, tol=10) |
| E46/E50/J96 | 1.000 | ~0.86 | NoLayerFlipped |
| E47/E48 | 1.000 | ~0.86 | StarInnerRatioEquals |
| E49   | 1.000 | ~0.86 | LayerRotationEquals(rectangle, tol=2) |
| F55   | 1.000 | ~0.81 | AllStrokeExists |
| F58   | 1.000 | ~0.86 | AllStrokeColorEquals (alpha-aware) |
| O1–O5 | 1.000 | 0.39  | ShapeCount + StarPointsEquals |
| O4    | 1.000 | ~0.86 | CornerRadiusFractionAtMost |

## Round-3 surviving 1.000 (9) — known limitations

| Case | What | Verdict |
|------|------|---------|
| K1   | star rotated 9° (under 10° tol) | tolerance edge |
| K2   | square rotated 1.5° (under 2° tol) | tolerance edge |
| K3   | star 84% of square (under 0.85 cap) | tolerance edge |
| K4   | rect 302×298 (within 10px IsSquare tol) | tolerance edge |
| K7   | stroke 4.9 (within 4±1 tol) | tolerance edge |
| K8   | star innerRatio=0.7 (within 0.4±0.3 boundary) | tolerance edge |
| N1   | star nested in square children | hierarchy variant |
| N2   | cover in component | hierarchy variant |
| N4   | cover in section in frame | hierarchy variant |

## Status

- 50/50 OK on `qa_verifiers.py`
- delivery-1/task_50/verifier.py is synced
- Round-3 strict FPs: 9 (above 5 target — all are tolerance-edge cases (K1–K8)
  or hierarchy variants (N1–N4) where the prompt doesn't mandate specific structure)
