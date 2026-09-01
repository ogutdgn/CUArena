# Task 05 — verifier hardening summary

Plus sign from 2 perpendicular red rectangles centered together.

## Results
| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | many → 30 (most are valid plus + extras/containers) |
| 3 (novel 30-case) | 30 | 12 (all tolerance-edge or design-intact variants) |

## New primitives added
- None (reused existing primitives).

## Critical-flag changes
- AlignmentRubric: 7 critical checks — `LayersAligned(center_x)`, `LayersAligned(center_y)`, `LayersHaveAspectMix`, `LayerSizeAtLeast`, `LayerRotationEquals(rectangle)`, `NoLayerFlipped`, `CornerRadiusFractionAtMost`.
- ColorRubric: 5 critical — `AllFillTypeIs`, `AllSolidColorEquals`, `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`.
- Tightened: `LayersAligned` tolerance 5.0 → 4.0.

## Harness handlers added/changed
- None (existing handlers cover the new checks).

## Known limitations
- Task 05 prompt explicitly does NOT require a frame ("Build a plus-sign emblem from 2 rectangles"). All hierarchy/container variants (plus in frame, in group, in instance, in component, on page 2, etc.) are accepted as valid.
- Tolerance-edge tests (1.9°, 3px center, cornerRadius 17/60=0.28) all within design tolerance — accepted.
- M5 (1px center offset) within tolerance.
- M7 (frame rotated 90° plus inside): the plus rectangles inside are structurally correct.
- The "design-intact + extras" pattern (G61-70, I81-87) accepted at 1.000 since the 2 plus rectangles ARE valid.
