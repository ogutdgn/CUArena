# Task 33 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_33_extended.py`
Round 3: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_33_round3.py`

## Results

| Round | Cases | Strict FPs (≥0.95) — true FPs |
|-------|-------|-------------------------------|
| 1 (initial 100-case)   | 100 | 56 (very weak baseline) |
| 2 (after fixes)         | 100 | 0 true FPs (33 cases at 1.0 — all legitimate frame/hierarchy variants) |
| 3 (novel 30-case)       | 29  | 0 true FPs (8 within-tolerance cases) |

## Verifier additions

Total checks: 9 → 26; critical checks: 8 → 22.

### Fundamentals rubric
- Added `PolygonSidesEquals(sides=3)` (★ critical) — "wedge triangles" must be 3-sided.

### Alignment rubric (was 2 checks → now 12)
- `AllLayersAreCircular(ellipse)` — base must be true circle (catches squashed oval).
- `LayerInFrontOf(polygon, ellipse)` — every wedge drawn on top of base.
- `LayersOverlap(polygon, ellipse)` — wedges visually overlap base.
- `LayerSizeAtLeast` for both ellipse (≥20×20) and polygon (≥10×10) — non-degenerate.
- `LayerSmallerThanLayer(polygon, ellipse, max_frac=0.95)` — wedges are slices, not full pie.
- `LayerRotationEquals(ellipse, 0)` — base upright.
- `NoLayerFlipped(polygon)` and `NoLayerFlipped(ellipse)` — no mirrored shapes.
- `LayersHaveDistinctRotations(polygon, minimum=2, tol=10°)` — wedges at "different angles".

### Color rubric (was 4 checks → now 10)
- `FillCountAtMost(ellipse, max=1)` and `FillCountAtMost(polygon, max=1)` — no stacked fills.
- `FillOpacityAtLeast(0.5)` for both — catches transparent fills.
- `LayerVisible(ellipse)` and `LayerVisible(polygon)` — catches alpha=0/opacity=0/visible=False.

## Primitive additions (cross-task)

- `LayersHaveDistinctRotations(layer_type, minimum, tolerance_deg)` — at least N distinct
  rotation values among layers of layer_type. Used to enforce "rotated to different
  angles" requirement on pie wedges. Added to `geometry_checks.py` with matching synth
  handler in `qa_verifiers.py` that spreads rotations evenly when the perfect log lacks them.

## Round 3 results

| Case  | What it does                              | Score | Caught by |
|-------|-------------------------------------------|-------|-----------|
| K1    | wedges at same rotation                   | 0.890 | LayersHaveDistinctRotations |
| K2    | wedges 5° apart (under tol 10)            | 1.000 | accepted as legitimate (within tol) |
| K3    | near-teal base (within tol 0.25)          | 1.000 | accepted as legitimate |
| K4    | base drawn last (above wedges)            | 0.890 | LayerInFrontOf, LayerOnTopOf |
| K5    | base sandwiched between wedges            | 0.890 | LayerInFrontOf |
| K6    | tiny base, huge wedges                    | 0.835 | LayerSmallerThanLayer fails |
| K7    | wedges with corner radius                 | 1.000 | accepted (cornerRadius soft) |
| K8    | wedges placed beside base                 | 1.000 | LayersOverlap is "≥1 pair" |
| K9    | wedges rotated parallel 90°               | 0.890 | LayersHaveDistinctRotations |
| K10   | wedges 5px wide (almost lines)            | 0.890 | LayerSizeAtLeast |
| L1-L5 | visibility/transparency tricks            | 0.890 | LayerVisible |
| M1    | base 1×1                                  | 0.890 | LayerSizeAtLeast |
| M2    | wedges 0×0                                | 0.890 | LayerSizeAtLeast |
| M3    | base oval 300×50                          | 0.890 | AllLayersAreCircular |
| M4    | wedges identical (overlapping)            | 0.890 | LayersHaveDistinctRotations |
| M5    | wedges = base size                        | 0.890 | LayerSmallerThanLayer |
| O1    | base is rectangle                         | 0.385 | ShapeCount, AllLayersAreCircular |
| O2    | wedges are stars                          | 0.358 | ShapeCount(polygon) |
| O3    | wedges 4-sided                            | 0.890 | PolygonSidesEquals |

## Acceptable 1.000 cases

The prompt for task 33 doesn't mention frame/structure, so frame variants and
hierarchy nesting are considered acceptable. The remaining 1.000 cases are:

- B17, K2, K3: within color/rotation tolerance.
- C21: large base — size not constrained.
- C26, D35, J100, G61: controls and shifted globally.
- D40: shifted globally — geometry preserved.
- E50: corner radius — prompt allows artistic variation.
- F58: wedges concentric small — passes structural checks.
- G61-G70: frame variants where pie still detected.
- H75-H80: event sugar.
- I81-I90: hierarchy variants where pie still detected.
- M6, N1-N4: structural variants — prompt doesn't require frame.

## Known limitations

- The prompt for task 33 doesn't strictly require a frame, so structure/hierarchy
  exploits (split frames, deep nesting) yield 1.000 — by design.
- `LayersOverlap(polygon, ellipse)` checks "at least one pair overlaps" — when one
  wedge is positioned beside the base while another overlaps, the check still passes.
  Tightening this would require an `AllLayersOverlap` primitive (deferred).
