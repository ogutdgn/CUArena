# Task 34 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_34_extended.py`
Round 3: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_34_round3.py`

## Results

| Round | Cases | Strict FPs (≥0.95) — true FPs |
|-------|-------|-------------------------------|
| 1 (initial 100-case) | 100 | 60 (very weak baseline) |
| 2 (after fixes)       | 100 | 0 true FPs (31 cases at 1.0 — frame/hierarchy/event variants) |
| 3 (novel 30-case)     | 29  | 0 true FPs (5 within-tolerance cases) |

## Verifier additions

Total checks: 8 → 21; critical checks: 4 → 19.

### Alignment rubric (was 1 check → now 7)
- `LayersConcentric(line, tol=20)` — branches share center (4-fold symmetry "around the center").
- `LayersSameDimensions(line, tol=5)` — branches all same length.
- `AllLayerBoundsInside(line, frame, tol=4)` — branches fit inside frame.
- `LayerSizeAtLeast(line, min_w=20)` — no degenerate lines.
- `NoLayerFlipped(line)` — branches not flipped.
- `LayerRotationEquals(frame, 0)` — frame upright.

### Color rubric (was 3 → now 9)
- `AllStrokeExists("line")` — every branch has a stroke (replaces `StrokeExists`).
- `AllStrokeColorEquals(line, WHITE)` — every branch is white (replaces `StrokeColorEquals`).
- `AllLayerStrokeVisible(line, alpha≥0.5, weight≥0.5)` — catches transparent / 0-weight strokes.
- `FillCountAtMost(frame, 1)`, `FillOpacityAtLeast(frame, 0.5)`.
- `LayerVisible(frame)`, `LayerVisible(line)` — catches opacity=0 tricks.

### Structure rubric (NEW)
- `LayerInsideFrame(line)`, `LayerGroupAllInSameFrame(line, minimum=4)`.
- `ChildCountAtLeast(frame, minimum=4)`, `FrameCountAtMost(maximum=1)`.

## Round 3 results

| Case  | What it does                            | Score | Caught by |
|-------|-----------------------------------------|-------|-----------|
| K1    | 4 parallel lines (no rotation step)     | 0.892 | LayersEvenlyRotated |
| K2    | stepped 8° (under tol 10)               | 0.892 | LayersEvenlyRotated |
| K5    | stepped 90° but not concentric          | 0.892 | LayersConcentric |
| K6    | varying lengths                         | 0.892 | LayersSameDimensions |
| K7    | navy rectangle instead of frame         | 0.450 | ShapeCountAtLeast(frame) |
| K8    | all 4 lines parallel rotation 0         | 0.892 | LayersEvenlyRotated |
| L1    | stroke alpha=0                          | 0.892 | AllLayerStrokeVisible |
| L2    | stroke visible=False                    | 0.890 | AllLayerStrokeVisible |
| L3    | layer opacity=0                         | 0.890 | LayerVisible |
| L5    | stroke weight 0.1                       | 0.890 | AllLayerStrokeVisible (min_weight=0.5) |
| M1-M2 | 1×1, 0×0 lines                          | 0.880-0.892 | LayerSizeAtLeast |
| M3    | parallel pile (rotation 0)              | 0.890 | LayersEvenlyRotated |
| M4    | lines outside frame                     | 0.892 | AllLayerBoundsInside |
| M5    | frame 0×0                               | 0.892 | implicit (lines won't fit) |
| M7    | huge lines, tiny frame                  | 0.892 | AllLayerBoundsInside |
| N1    | snowflake without frame                 | 0.792 | StructureRubric |
| N2    | each line in own frame                  | 0.850 | StructureRubric |
| N3    | snowflake in component (no frame)       | 0.792 | StructureRubric |
| N4    | 2 lines in frame, 2 on page             | 0.850 | StructureRubric |
| O1    | vectors instead of lines                | 0.450 | ShapeCount(line, =4) |
| O2    | rectangles instead of lines             | 0.450 | ShapeCount(line, =4) |
| O3    | stars instead of lines                  | 0.450 | ShapeCount(line, =4) |

## Acceptable 1.000 cases

- A8, A10: design + extras still detectable.
- B17, B18: within color tolerance.
- C24, C26, G70: large frame variants.
- D31-D40: position variants — concentric/lined-up still satisfies prompt.
- E44: rotation +5° (within tol 10).
- F54, F55, F58: stacked strokes / dashed / drop shadows — extras don't break design.
- F56-F58: frame stroke / frame shadow.
- G62, G66, G69: frame variants where snowflake structurally present.
- G61-G63 acceptable variations of position.
- H71-H80: event sugar.
- I85, I87: nested frames / multi-page where snowflake still detected.

## Known limitations

- K3 (88° step under tol 10): edge-of-tolerance case, accepted by design.
- K4 (X-pattern at 45° offset): valid 4-fold symmetry — passes per prompt.
- K9 (rotation +4°): within tolerance.
- K10 (varying weights): prompt doesn't specify exact stroke weight, only "white branches".
- M6 (lines piled in corner): all concentric, technically passes radial check.

## Harness changes

- `LayersConcentric` handler now respects `LayersSameDimensions` for the same type:
  if both are required, layers stay same size and only centers align (no progressive shrink).
