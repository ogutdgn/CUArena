# Task 35 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_35_extended.py`
Round 3: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_35_round3.py`

## Results

| Round | Cases | Strict FPs (≥0.95) — true FPs |
|-------|-------|-------------------------------|
| 1 (initial 100-case)   | 100 | 51 (very weak baseline) |
| 2 (after fixes)         | 100 | 0 true FPs (38 cases at 1.0 — frame/hierarchy/event variants) |
| 3 (novel 30-case)       | 29  | 0 true FPs (6 within-tolerance cases) |

## Verifier additions

Total checks: 7 → 18; critical checks: 4 → 17.

### Alignment rubric (was 2 → now 6)
- `LayerSizeAtLeast(polygon, min=15)` — no degenerate hexagons.
- `LayerRotationEquals(polygon, 0, tol=5)` — hexagons upright.
- `NoLayerFlipped(polygon)` — no mirrored hexagons.
- `CornerRadiusFractionAtMost(polygon, max=0.1)` — hexagons not "rounded" away.

### Color rubric (was 4 → now 9)
- `AllFillTypeIs(polygon, solid)` — all hexagons solid (no image/gradient).
- `AllStrokeExists("polygon")` (replaces `StrokeExists`).
- `AllStrokeColorEquals(polygon, BLACK)` (replaces `StrokeColorEquals`) — every hex
  has black stroke (catches mixed colors).
- `AllLayerStrokeVisible(polygon, alpha≥0.5, weight≥0.5)` — catches transparent / 0-weight strokes.
- `FillCountAtMost(polygon, 1)` — no stacked fills.
- `FillOpacityAtLeast(polygon, 0.5)` — visible fills.
- `LayerVisible(polygon)` — catches alpha=0/opacity=0/visible=False.

## Round 3 results

| Case  | What it does                            | Score | Caught by |
|-------|-----------------------------------------|-------|-----------|
| K1    | 3 hex + 1 pentagon                      | 0.521 | PolygonSidesEquals |
| K2    | 1 heptagon (7 sides)                    | 0.812 | PolygonSidesEquals |
| K3    | hexagons cornerRadius 30 (rounded)      | 0.875 | CornerRadiusFractionAtMost |
| K4    | rotation 6° (just over tol 5)           | 0.875 | LayerRotationEquals |
| K5    | hexagons mirrored                       | 0.875 | NoLayerFlipped |
| K6    | stroke 0.3px (basically invisible)      | 0.861 | AllLayerStrokeVisible |
| K9    | 4 hexagons in row                       | 0.875 | OffsetGridLayout |
| K10   | regular grid (no offset)                | 0.875 | OffsetGridLayout |
| L1-L5 | visibility/transparency tricks          | 0.835-0.861 | LayerVisible / AllLayerStrokeVisible |
| M1, M2| degenerate sizes                        | 0.875 | LayerSizeAtLeast |
| M3    | hexagons 16×16 (just over min)          | 1.000 | accepted (≥ min) |
| M4    | all stacked at one point                | 0.875 | OffsetGridLayout |
| M5    | all 0×0                                 | 0.812 | LayerSizeAtLeast |
| M6    | varying sizes                           | 0.854 | LayersSameDimensions |
| M7    | squashed 200×30                         | 0.875 | OffsetGridLayout |
| O1    | stars instead of polygons               | 0.358 | ShapeCount(polygon) |
| O2    | ellipses instead of hexagons            | 0.358 | ShapeCount(polygon) |
| O3    | rectangles instead                      | 0.358 | ShapeCount(polygon) |

## Acceptable 1.000 cases

- A7, A8: design + extras (extra rect/ellipse) still pass.
- B17: near-yellow within tol.
- C21: 200×200 hexagons — large but design intact.
- C27, C28: within size tolerance.
- D34, J100: controls.
- D39, D40, J99: shifted globally — geometry preserved.
- F55: dashed strokes — prompt doesn't forbid stroke styling.
- F57: opacity 0.5 — still visually distinguishable.
- G61-G70: frame variants where honeycomb still detected.
- H75-H80: event sugar.
- I81-I90: hierarchy variants.
- J97: huge frame, hexagons inside — design valid.

## Known limitations

- K7 (near-yellow color) and K8 (dark gray near-black stroke) within tolerance — by design.
- N1-N4 (frame split / component / nested groups) yield 1.000: prompt doesn't strictly
  require a single frame structure. Adding a structure rubric would catch these but
  would also block component-based workflows.
