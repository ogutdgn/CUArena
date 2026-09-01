# Task 29 — verifier hardening summary

Spec: Off-white frame + 4 same-color circles in 2×2 grid (Tidy up).

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case battery) | 100 | ~50 → ~25 (mostly borderline-acceptable) |
| 3 (novel 30-case battery) | 27 | 2 (K10 white-vs-off-white within tol, M5 overlapping but valid 2x2) |

## New primitives added

No new primitives needed for task 29 — reused existing `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`, `LayerRotationEquals`, `NoLayerFlipped`, `LayerSizeAtLeast`, `AllLayerWidthFraction`, `AllLayerBoundsInside`, `LayerGroupAllInSameFrame`.

## Critical-flag changes

Added to `task_29_polka_dot_grid.py`:

- **AlignmentRubric** — added critical checks:
  - `LayerRotationEquals(ellipse, degrees=0, tolerance=2.0)` (catches E41 rotation)
  - `LayerRotationEquals(frame, degrees=0, tolerance=2.0)` (catches G61 frame rotated)
  - `NoLayerFlipped(ellipse)` (catches E42, J98)
  - `LayerSizeAtLeast(ellipse, min_w=20, min_h=20)` (catches C25 1x1, M4)
  - `AllLayerWidthFraction(ellipse, frame, 0.02, 0.40)` (catches C21 tiny, C22 huge, J96 full-frame, K7)
  - `AllLayerBoundsInside(ellipse, frame, tolerance=4.0)` (catches D40, J97 negative coords)

- **ColorRubric** — added critical checks:
  - `FillCountAtMost(ellipse, max_count=1)` (catches B20 stacked fills)
  - `FillOpacityAtLeast(ellipse, min_opacity=0.5)` (catches B19, L3)
  - `LayerVisible(ellipse)` (catches B18, J94, J95, L1, L2, L4, L5)

- **StructureRubric** (new) — added critical check:
  - `LayerGroupAllInSameFrame(ellipse, minimum=4)` (catches G68 no frame, I82 split frames, I86 component, I87 section, N1, N2, N3, N4)

## Harness handlers added/changed

No new handlers — `LayerGroupAllInSameFrame` already had a Pass 8.5 handler that ensures all dots are direct children of the frame.

## Known limitations

- **K10 (pure white frame)**: distance from off-white (0.97, 0.95, 0.92) to (1, 1, 1) ≈ 0.10, within 0.15 tolerance. Tightening would risk rejecting legitimate near-white frames.
- **M5 (overlapping dots in 2x2)**: dots arranged in 2x2 layout but with size > gap so they overlap. Layout still passes `LayersInGrid`. Visual overlap is legit per prompt.
- **B15, F51, F60 (color variants)**: prompt says "same color OR all different", so these are acceptable per prompt.
- **Borderline 1.000s**: extras-present designs (A5, A6) and decorations (E46-E49) score 1.0.
