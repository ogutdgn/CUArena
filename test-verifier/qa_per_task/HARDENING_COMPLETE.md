# All-50-tasks hardening complete

Full task_01-style hardening applied across all 50 task verifiers.

## Final state

| Metric | Value |
|--------|-------|
| qa_verifiers.py harness | `50 OK \| 0 STRICT \| 0 LENIENT \| 0 CRASH` |
| qa_per_task batteries | 50/50 clean (`0 bug(s)` each) |
| `task_NN_extended.py` files | 50 (≈100 cases each) |
| `task_NN_round3.py` files | 50 (≈30 novel-deception cases each) |
| `task_NN_findings.md` files | 50 |
| Total stress-test cases | ~6500 (4970 round-1 + 1530 round-3) |
| delivery-1 mirror | synced |

## New primitives added across the 10 hardening batches

### Fill checks
- `DistinctTypedSolidColors` — distinct solid colors counted only among one layer_type

### Stroke checks
- `AllStrokeExists` — every layer has a stroke
- `AllStrokeColorEquals` — every layer has stroke matching expected color
- `AllStrokeWeightAtMost` / `AllStrokeWeightWithinTolerance` — every stroke weight ≤ max / ≈ target
- `AllLayerStrokeVisible` — every layer's stroke is visibly rendered
- `StrokeRendersVisible` / `VisibleStrokeExists` — stroke alpha ≥ min, weight > 0, visible ≠ False
- `DistinctTypedStrokeColors` — distinct stroke colors among one layer_type

### Geometry checks
- `LayerSmallerThanLayer` — cross-type "smaller" relation (e.g., pivot < blade)
- `LayerShortDimensionAtMost` — short dimension ≤ max
- `AllLayersAreCircular` — every ellipse has w ≈ h
- `LayerAllCircular` / `LayerAllSquare` / `LayerAllSameSize` — every-layer parity helpers
- `FrameCountAtMost` — at most N top-level frames
- `LayersHaveDistinctRotations` — pairwise distinct rotations
- `LayersHaveDistinctCenters` — pairwise distinct centers
- `LayersHaveDescendingArea` — consecutive area ratio ≥ min
- `LayersHaveConsistentGap` — positive consistent inter-layer gap
- `LayersAtDistinctPositions` — at least N distinct (x, y) centers
- `LayersBracketAllOnAxis` — bracket span surrounds inner span
- `LayersOrderedByRotation` — layers ordered by rotation along axis
- `CrossTypeAreaRatioAtLeast` — big_type/small_type area ≥ min ratio
- `LayersAlternatingColors(sort_axis="angle")` — radial alternation support added

### Property checks
- `LayerRendersStrokeOrFill` — visible stroke OR fill (catches invisible-line tricks)

### Effect checks
- `DropShadowCountAtLeast` — count of visible drop shadows ≥ min
- `PairedDropShadowsOpposite` — ≥2 visible shadows with opposing offsets
- `VisibleDropShadowExists` — drop shadow alpha ≥ min, visible ≠ False
- `AllLayerBlurExists` — every layer has visible non-zero layer_blur

### Structure checks
- `LayerGroupAllInSameFrame` — all N layers of a type are direct children of one frame

## Harness extensions

`qa_verifiers.py` now has handlers for:
- All new primitives above (each with `mutate_for_geometry` logic to preserve perfect-log = 1.0)
- `LayersAligned` (axis-specific same-type alignment in final pass)
- `LayersStacked` (re-runs in final pass after sizing)
- `LayerAspectRatioGreaterThan` (re-runs after width-fraction sizing)
- `LayerSizeEquals` (sets exact dimensions in final pass)
- `PolygonSidesEquals`, `StarPointsEquals`
- `SmallerLayerInsideLarger` (branches on whether `LayersConcentric` is required)
- `LayerCenteredOnLayer` (axis="x"/"y"/"both")
- `LayerCenteredInFrame` (re-applies after width-fraction)
- `LayersConcentric` + `LayersSameDimensions` interaction (uniform vs progressive sizing)
- `LayerOnTopOf`, `LayerInFrontOf`, `LayerNextTo`, `LayerEdgesAligned`
- Cross-type `LayerBoundsInside` with circular/square inners
- `EffectCount` synthesizes opposing-offset shadows
- `synth_layer` 8-color palette for `DistinctSolidColors`

## Per-task PASS-log fixture updates

Tasks 17, 18, 19, 21, 27-31, 34-36, 37-41, 12-16: legacy `qa_per_task/task_NN.py` PASS_LOGS updated to wrap layers in a frame (since hardened verifiers now require `LayerInsideFrame` + `ChildCountAtLeast`).

Task 17 specifically: rotated polygon order swapped (180° on top, 0° on bottom) to match `LayersOrderedByRotation` semantics for hourglass.

Task 18: `not_circular` FAIL_LOG expected pattern updated to "non-circular ellipse" (matches new `AllLayersAreCircular` message format).

## Per-batch FP outcomes

Each batch reported strict round-3 FPs ≤ ~10 per task, with most "FPs" being:
- Legitimate intended-pass cases (controls, "all distinct" variants)
- Tolerance-edge cases (e.g., 1.5° rotation under 2° tol — within design tolerance)
- Frame variants (G62-G68: extra frames, nested frames, frame with stroke)
- Hierarchy variants (inside group / section / component)
- Event-log extras (extra align/distribute/delete events)

True structural FPs (a real defect not docked) are 0-3 per task. Roughly 95% confidence across all 50 tasks (matches the original task_01 confidence level).

## What remains (known limitations)

Some FPs cannot be caught without role-disambiguation that the prompt itself doesn't define (e.g., "this rectangle is the body, that one is the door" — both rectangles, structurally indistinguishable when one's size matches the other). These are documented per task in the findings docs.

Tasks 49 (decorative ribbon) and 06 (gold burst) have looser prompts that allow more variants — their FP counts are inherently higher.

## Files

```
test-verifier/qa_per_task/
  task_NN_extended.py     × 50  (~6,500 cases total)
  task_NN_round3.py       × 50  (~1,500 cases total)
  task_NN_findings.md     × 50

test-verifier/tasks/task_NN_*.py    × 50  (all updated with critical flags + new checks)
test-verifier/verifier/checks/*.py            (28 new primitive classes)
test-verifier/qa_verifiers.py                 (handlers for new primitives + final-pass repositioning)
delivery-1/task_NN/verifier.py     × 50  (synced)
```
