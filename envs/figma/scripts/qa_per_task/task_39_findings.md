# Task 39 — verifier hardening summary

Run: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_39_extended.py`

## Results

| Round | Cases | Strict FPs (≥0.95) | Notes |
|-------|-------|--------------------|-------|
| 1 (initial 100-case) | 100 | 73 → 35 | most are legitimate "extras OK" |
| 3 (novel 30-case)    | 27  | 11 → 8  | rest are tolerance-edge / multi-frame |

## New primitives added

(none — leveraged existing primitives + new ones from task 37/38: `VisibleStrokeExists`, `CrossTypeAreaRatioAtLeast`)

## Critical-flag changes

- `FundamentalsRubric` (1st): 6 critical: count of arcs/circle, sizes, no-flip.
- `AlignmentRubric`: 9 critical: rotation, all-bounds-inside-frame, dot centered on arcs (x), 
  dot is circular, dot below arcs, area ratios (dot < arcs, dot < frame).
- `ColorRubric`: 10 critical: solid fills, navy color, stroke exists/weight/color/visible, 
  fill count ≤1, layer visible, fill opacity, vector visible.
- `StructureRubric`: 2 critical (was 0): both vector and ellipse must be in frame.
- `EventRubric`: 2 critical: pen and ellipse tools.

## Round-1 catches

- A1-A4 (counts wrong): `ShapeCountAtLeast(vector, 2)`, `ShapeCount(ellipse, 1)`
- B11/B12 (image/gradient fills): `AllFillTypeIs("ellipse", "solid")`
- B13 (no fill on dot): `LayerVisible` + `AllFillTypeIs`
- B14 (red dot): `SolidColorEquals(ellipse, NAVY, tol=0.20)`
- B15 (red arcs stroke): `StrokeColorEquals(vector, NAVY, tol=0.20)`
- B16/B17 (stroke too thin/thick): `StrokeWeightEquals(vector, 6, tol=2)`
- B18-B20 (visibility tricks): `LayerVisible`, `FillOpacityAtLeast`
- C21/C26 (degenerate dot): `LayerSizeAtLeast(ellipse, 8, 8)`
- C23 (degenerate arcs): `LayerSizeAtLeast(vector, 20, 10)`
- C24 (huge arcs): `AllLayerBoundsInside(vector, frame)`
- C27 (oval dot): `LayerIsCircular(ellipse, tol=8)`
- D31-D33 (off-frame): `AllLayerBoundsInside(*, frame)`
- D34 (dot above arcs): `LayerEdgesAligned(ellipse top, vector bottom, tol=100)`
- D35 (dot far from arcs x): `LayerCenteredOnLayer(ellipse, vector, axis="x")`
- E42/E43 (arcs rotated): `LayerRotationEquals(vector, 0)`
- E44 (dot flipped): `NoLayerFlipped(ellipse)`
- E47/E48/E49 (wrong arc types): `ShapeCountAtLeast(vector, 2)`
- F52/F53 (no stroke): `StrokeExists("vector")` + `VisibleStrokeExists`
- F55/F56 (stroke alpha=0/visible=False): `VisibleStrokeExists`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`

## Round-3 catches

- K5/K6 (stroke alpha=0.04 / weight=0.4): `VisibleStrokeExists` (alpha≥0.05, weight≥0.5)
- K8 (no strokes): `StrokeExists` critical
- K10 (dot 0x0): `LayerSizeAtLeast(ellipse, 8, 8)`
- L1-L5 (alpha/visible tricks): `LayerVisible`, `VisibleStrokeExists`
- M1 (dot = full frame): `CrossTypeAreaRatioAtLeast(frame, ellipse, 10)`
- M4 (dot bigger than arcs): `CrossTypeAreaRatioAtLeast(vector, ellipse, 1.0)`
- M5 (stroke weight 0): `VisibleStrokeExists`
- O1-O3 (wrong types): `ShapeCount` critical

## Remaining acceptable 1.000s

| Case | Why |
|------|-----|
| A5 | 5 vectors — extras OK (≥2 satisfied) |
| A8 | Extra rectangle — doesn't break wifi |
| A10, C29, D38, E50, F60, G68, H80, I90, J100 | Perfect controls |
| C25 | dot 200x200 — no specific size limit; LayerIsCircular still passes |
| D36, D37 | Arc placement variants |
| D39, J91 | Dot rotation (no visible diff for circular dot) |
| D40 | All at origin — within bounds tolerance |
| F51, F58, J98 | Arc placement variants — both arcs upright, navy, etc. |
| G62-G69 | Frame variants (nested, with stroke, oversized) |
| H72-H78 | Event-log extras |
| I82, I85, I86, I89 | Multi-frame / nested / page 2 hierarchy |

## Round-3 acceptable 1.000s

| Case | Why |
|------|-----|
| K1, K2, K3 | Within rotation/stroke tolerance |
| K4 | Color near-navy at boundary (max diff 0.20 = tol) |
| K9 | Arcs same size but offset — both visible navy arcs |
| M2, M3 | Geometric variants — dot/arcs still rendered |
| N1, N3 | Multi-frame structural — arcs/dot in different frames |
