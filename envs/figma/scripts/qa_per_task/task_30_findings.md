# Task 30 — verifier hardening summary

Spec: 6 vertical stripes alternating deep-blue/cream filling a 600x600 frame.

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case battery) | 100 | ~50 → ~25 (mostly borderline-acceptable) |
| 3 (novel 30-case battery) | 27 | 1 (K9 stripes shorter than frame — height constraint hard to enforce) |

## New primitives added

No new primitives needed — reused existing `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`, `LayerRotationEquals`, `NoLayerFlipped`, `LayerSizeAtLeast`, `AllLayerBoundsInside`, `LayerGroupAllInSameFrame`.

## Critical-flag changes

Added to `task_30_stripe_wallpaper.py`:

- **AlignmentRubric** — added critical checks:
  - `LayerRotationEquals(rectangle, degrees=0, tolerance=2.0)` (catches E41, E42, E47, E49)
  - `LayerRotationEquals(frame, degrees=0, tolerance=2.0)` (catches G61)
  - `NoLayerFlipped(rectangle)` (catches E43, J96)
  - `LayerSizeAtLeast(rectangle, min_w=10, min_h=100)` (catches C26 1px wide, M4 under-min)
  - `AllLayerBoundsInside(rectangle, frame, tolerance=4.0)` (catches D33 off-frame, D36 negative coords, M1)

- **ColorRubric** — added critical checks:
  - `FillCountAtMost(rectangle, max_count=1)` (catches B20 stacked fills)
  - `FillOpacityAtLeast(rectangle, min_opacity=0.5)` (catches B19, L3)
  - `LayerVisible(rectangle)` (catches B18, J94, J95, L1, L2, L4, L5)

- **StructureRubric** (new) — added critical check:
  - `LayerGroupAllInSameFrame(rectangle, minimum=6)` (catches G68, I82, I86, I87, I88, N1, N2, N3, N4)

## Harness handlers added/changed

No new harness handlers — `LayerGroupAllInSameFrame` Pass 8.5 handler already existed.

## Known limitations

- **K9 (stripes shorter than frame)**: 400px-tall stripes in a 600px frame still pass aspect-ratio check (400/100=4 > 2). Hard to enforce "must fill frame height" without frame-relative sizing.
- **F51 (reversed pattern), F53 (red-green)**: `LayersHaveColorOrder` is non-critical (per prompt: "alternating two colors" but order not pinned).
- **F54 (slightly off colors)**: within `LayersHaveColorOrder` tolerance of 0.25.
- **C29, D39 (partial fill)**: stripes that don't span full height; LayerSizeAtLeast min_h=100 catches the worst, but partial fills still pass when h≥100.
- **Borderline 1.000s**: extras-present designs (A6) and decorations (E44-E50) score 1.0.
