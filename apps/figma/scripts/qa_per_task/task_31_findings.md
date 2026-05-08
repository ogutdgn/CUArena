# Task 31 — verifier hardening summary

Spec: Yellow center circle + 4 triangle rays at 90° intervals (radial sun).

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case battery) | 100 | ~50 → ~27 (most are loose-prompt acceptable) |
| 3 (novel 30-case battery) | 27 | 1 (K4 91° step within 10° rotation tolerance) |

## New primitives added

No new primitives needed for task 31 — reused existing `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`, `LayerRotationEquals`, `NoLayerFlipped`, `LayerSizeAtLeast`, `AllLayerWidthFraction`, `AllLayerBoundsInside`, `LayerInsideFrame`, `PolygonSidesEquals`.

## Critical-flag changes

Added to `task_31_sun_rays.py`:

- **FundamentalsRubric** — added critical check:
  - `PolygonSidesEquals(sides=3)` (catches K1 sides=4, K2 sides=5, E41, E42)

- **AlignmentRubric** — added critical checks:
  - `LayerRotationEquals(ellipse, degrees=0, tolerance=2.0)` (catches E46 circle rotated)
  - `LayerRotationEquals(frame, degrees=0, tolerance=2.0)` (catches G61 frame rotated)
  - `NoLayerFlipped(ellipse)` (catches J97)
  - `NoLayerFlipped(polygon)` (catches E47)
  - `LayerSizeAtLeast(ellipse, min_w=20, min_h=20)` (catches C21 tiny circle, M4)
  - `LayerSizeAtLeast(polygon, min_w=15, min_h=15)` (catches C23 tiny rays)
  - `AllLayerWidthFraction(ellipse, frame, 0.02, 0.40)` (catches C22 huge, M1 full-frame)
  - `AllLayerWidthFraction(polygon, frame, 0.02, 0.30)` (catches C24 huge rays, M2)
  - `AllLayerBoundsInside(ellipse/polygon, frame, tolerance=4.0)` (catches D32, D40 off-frame)

- **ColorRubric** — added critical checks:
  - `FillCountAtMost(ellipse/polygon, max_count=1)` (catches B20 stacked fills)
  - `FillOpacityAtLeast(ellipse/polygon, min_opacity=0.5)` (catches B19, L3)
  - `LayerVisible(ellipse/polygon)` (catches B18, J94, J95, L1, L2, L4, L5)

- **StructureRubric** (new) — added critical checks:
  - `LayerInsideFrame(ellipse)` (catches G66 no frame)
  - `LayerInsideFrame(polygon)` (catches I82 split, I86 component, N1, N2, N3, N4)

## Harness handlers added/changed

No new harness handlers needed.

## Known limitations

- **K4 (rays at 91° steps)**: cumulative drift over 4 steps is 4° — within `LayersEvenlyRotated` tolerance of 10°. Tightening would risk rejecting legitimate near-90° drifts.
- **C29 (rays 60/62 within tol)**: legitimate.
- **D33 (circle off-center, rays radial around frame center)**: rays still pass `RadialDistribution` even when circle is elsewhere. The check focuses on rays only.
- **F58 (rays touching circle edge)**: legitimate close placement.
- **F59 (rays at 89/271° within tol)**: legitimate.
- **Borderline 1.000s**: extras-present designs (A7, A8, H75, H78, H79) and decorations (E48-E50) score 1.0.
