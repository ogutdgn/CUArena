# Task 32 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_32_extended.py`
Round 3: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_32_round3.py`

## Results

| Round | Cases | Strict FPs (≥0.95) — true FPs |
|-------|-------|-------------------------------|
| 1 (initial 100-case) | 100 | 1 (F59 alternation defeated) |
| 2 (after fixes)       | 100 | 0 (extras / position / frame variants only) |
| 3 (novel 30-case)     | 29  | 0 (legitimate within-tol cases only) |

After round 2, 21 cases remain at 1.000 in the extended battery — all
legitimate (extras, frame variants, hierarchy variants, control cases).

## Verifier additions

Total checks: 4 → 28; critical checks: 4 → 26.

### Fundamentals rubric
- Added `PolygonSidesEquals(sides=3)` (★ critical) — "triangles" requires 3 sides.

### Alignment rubric (was 4 checks → now 12)
- `AllLayersAreCircular("ellipse")` — pivot must be a true circle (catches squashed ellipse).
- `AllLayerBoundsInside(polygon, frame)` and `(ellipse, frame)` — blades & pivot inside frame.
- `LayerSizeAtLeast` for both polygon (≥10×10) and ellipse (≥8×8) — no degenerate shapes.
- `LayerSmallerThanLayer(ellipse, polygon, max_frac=0.8)` — "small center circle" enforced.
- `LayerInFrontOf(ellipse, polygon)` — pivot must render on top of all blades.
- `NoLayerFlipped(polygon)` — blades not mirrored.

### Color rubric (was 3 checks → now 10)
- `AllFillTypeIs("ellipse")` — pivot has solid fill.
- Switched `LayersAlternatingColors(sort_axis="x")` → `(sort_axis="angle")` — alternation
  cycles around the wheel angularly, defeating the A,A,B,B → A,B,A,B re-sort exploit.
- `FillCountAtMost` for both polygon and ellipse — no stacked fill workarounds.
- `FillOpacityAtLeast(0.5)` for both — catches transparent fills.
- `LayerVisible` for both — catches alpha=0, opacity=0, visible=False tricks.

### Structure rubric (NEW)
- `LayerInsideFrame(polygon)`, `LayerInsideFrame(ellipse)`.
- `LayerGroupAllInSameFrame(polygon, minimum=4)` and `(ellipse, minimum=1)`.
- `ChildCountAtLeast("frame", minimum=5)`.
- `FrameCountAtMost(maximum=1)` — exactly one top-level frame.

## Primitive additions (cross-task)

- `LayersAlternatingColors.sort_axis="angle"` — sorts layers by angle around centroid
  (radial layouts where x/y cycling is ambiguous). New code path in `geometry_checks.py`
  and matching synth handler in `qa_verifiers.py`.

## Round 3 results

Starting from the round-1 fixed verifier:

| Case  | What it does                            | Score | Caught by |
|-------|-----------------------------------------|-------|-----------|
| K1    | uniform color (alternation defeated)    | 0.890 | LayersAlternatingColors angle |
| K2    | A,A,B,B colors (x-sort exploit)         | 0.890 | LayersAlternatingColors angle |
| K6    | pivot 200×200 (not 'small')             | 0.892 | LayerSmallerThanLayer |
| K7    | pivot drawn behind blades               | 0.892 | LayerInFrontOf |
| K8    | pivot huge, occludes blades             | 0.892 | LayerSmallerThanLayer |
| K9    | blades 5×5 (degenerate)                 | 0.883 | LayerSizeAtLeast |
| K10   | pivot 1×1                               | 0.892 | LayerSizeAtLeast |
| L1-L5 | visibility tricks (alpha, opacity)      | 0.880-0.890 | LayerVisible |
| M1    | blades 1×1                              | 0.883 | LayerSizeAtLeast |
| M2    | blades overflow frame                   | 0.892 | AllLayerBoundsInside |
| N1    | pivot outside frame, blades inside      | 0.850 | StructureRubric |
| N2    | each shape in own frame                 | 0.850 | StructureRubric |
| N3    | pinwheel inside component               | 0.792 | StructureRubric (no frame) |
| O3    | polygons all 4 sides (squares)          | 0.875 | PolygonSidesEquals |

## Acceptable 1.000 cases

- D38, J100: control (perfect pinwheel).
- C27, E45: within rotation/size tolerance.
- D31, D32, D37, F51: pivot off-center — prompt doesn't constrain pivot position.
- F55: rotation +45° offset (still 90° step) — valid radial.
- G61-G70, I85-I90: frame/hierarchy variants — pinwheel structurally present.
- H75-H80: extra event noise (deletions, align tools).

## Harness changes

- `LayersAlternatingColors` handler now supports `sort_axis="angle"` — sorts layers
  by angle from centroid before assigning cycle colors.
- `LayersConcentric` handler skips progressive shrinking when `LayersSameDimensions`
  is also required for the same type.
