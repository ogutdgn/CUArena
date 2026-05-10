# Task 06 — verifier hardening summary

8 lines from a center point at 45° intervals to form a burst, gold strokes.

## Results
| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | 50 → 45 (most are valid burst at variant configurations) |
| 3 (novel 30-case) | 30 | 9 (tolerance-edge or design-intact) |

## New primitives added
- None (reused existing primitives `AllLayerStrokeVisible`, `AllStrokeColorEquals`, `LayerSizeAtLeast`, `NoLayerFlipped`, `LayerVisible`).

## Critical-flag changes
- AlignmentRubric: 4 critical — `LayersConcentric`, `LayersEvenlyRotated`, `LayerSizeAtLeast`, `NoLayerFlipped`.
- ColorRubric: 3 critical — `AllLayerStrokeVisible` (catches alpha=0/visible=False/weight=0), `AllStrokeColorEquals` (loose 0.30 tol for "gold"), `LayerVisible`.

## Harness handlers added/changed
- None new (existing `StrokeColorEquals`, `StrokeExists`, `StrokeWeightEquals` handlers cover the new checks).

## Known limitations
- The prompt does NOT require a frame, so all hierarchy/container variants pass.
- Tolerance-edge tests (47.9° step within 8°, ±9px center within 10, weight=0.5 at min) all within design tolerance.
- Long/short line lengths (5 to 10000) accepted as the prompt doesn't specify length.
- K3 (off-center within tol), K6 (gold variations within tol), K8/K10 (length/weight extremes), M5 (frame rotated 90° with lines inside): all design-intact.
- "Gold" tolerance is 0.30 — by design loose since gold is subjective.
