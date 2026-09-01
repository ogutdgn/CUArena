# Task 17 — verifier hardening summary

Task: Hourglass — 2 triangles point-to-point + 2 horizontal cap rectangles.

## Results

| Round                 | Cases | Strict FPs (≥0.95)    |
|-----------------------|-------|-----------------------|
| 1 (initial 100-case)  | 100   | 57 → 14 (borderline)  |
| 3 (novel 26-case)     | 26    | 4 → 0                 |

## What was fixed

### New primitives added
- `LayersBracketAllOnAxis(bracket_type, inner_type, axis)` → geometry_checks.py
  Stricter than `LayersFlankLayer`: brackets must surround the **union** of all inner_type bboxes,
  not just one pivot's center. Catches "cap inside triangle stack" deceptions (F55).
- `LayersOrderedByRotation(layer_type, rotation_first, rotation_second, axis)` → geometry_checks.py
  Among layers of one type, the one near rotation_first must be positioned before the one near
  rotation_second along the axis. Catches D35/K5 (right rotations, wrong vertical order).

### Critical-flag changes
- Tightened `LayersHaveRotations` tolerance_deg 8→1.5 for triangles (caught K1/K2 4° drift).
- Tightened `LayerRotationEquals` tolerance for caps: 0.5° (caught K3 1° drift).
- Added `PolygonSidesEquals(sides=3)` critical (caught E43/E44 4-sided/6-sided polygons).
- Added `LayerAspectRatioGreaterThan(rectangle, 2.0, "horizontal")` critical
  (caught caps that aren't horizontal — C25/E48/M7).
- Added `LayersAllShareEdge(rectangle, edge="center_x")` critical (caught D32/D38 unaligned caps).
- Added `LayersBracketAllOnAxis(rectangle, polygon, axis="y")` critical (caught F55 cap-inside).
- Added `LayersOrderedByRotation(polygon, 180, 0, "y")` critical (caught D35/K5 inverted).
- Added `LayerVisible` for both polygon and rectangle critical (caught B16-B19, L1-L5).
- Added `FillCountAtMost(max_count=1)` for both types (caught B20 stacked-fills).
- Added `AllLayerBoundsInside(*, frame)` for both types (caught D33/D34/M3/M4 off-frame).
- Added `LayerSizeAtLeast` for both types critical (caught C21/C26/C29/M2/J91 degenerate).
- Added `NoLayerFlipped` for both types critical (caught E47/J89 flipped).
- Added `LayerGroupAllInSameFrame` for both types critical (caught I80 split-frame).
- Added `FrameCountAtMost(maximum=1)` critical (caught I80 multi-frame).
- Added `LayerRotationEquals(frame, 0)` critical (caught G61 frame rotated).
- Added `CornerRadiusFractionAtMost(rectangle, 0.5)` critical (caught K6 caps as pills).
- Restructured rubrics: 4 rubrics × 0.25 weight → 5 rubrics × 0.20 (added StructureRubric).

### Harness handlers added/changed (qa_verifiers.py)
- New: `LayersBracketAllOnAxis` handler positions brackets around the inner span.
- New: `LayersOrderedByRotation` handler assigns rotations and arranges along axis.
- New: `LayersFlankLayer` handler (kept for completeness even though we use bracket instead).

## Acceptable 1.000 cases (intended passes / borderline)

| Case  | Why 1.000 is acceptable |
|-------|-------------------------|
| B11   | All-white hourglass — prompt doesn't require colors |
| C30   | Caps 800-wide — caps are still horizontal rectangles, prompt doesn't size-restrict |
| F59   | Top cap z-order changed — prompt doesn't enforce z-order |
| F60   | Caps far from triangles — they still bracket the triangles vertically |
| G62/G68 | Nested frames — top-level still 1 frame, shapes still inside it |
| G64/G65 | Frame stroke / image fill — frame container variants |
| H72/H73/H77 | Extra events (align, pen+delete, double session_end) — event extras tolerated |
| H78   | 5 polygons created when 2 exist — close to threshold (0.95) |
| I83   | 3-deep nested frames — content still inside |
| I85   | Hourglass on page 2 — multi-page docs |

## Round 3 — surviving deceptions

All round-3 cases now caught.

| Case  | What it does                                        | Old   | New   | Caught by |
|-------|-----------------------------------------------------|-------|-------|-----------|
| K1    | top tri rotation 178° (under tol)                   | 1.000 | 0.889 | tightened tolerance to 1.5° |
| K2    | tris at 178/2°                                      | 1.000 | 0.889 | tightened tolerance |
| K3    | caps rotated 1°                                     | 1.000 | 0.889 | tightened LayerRotationEquals tol to 0.5° |
| K6    | caps cornerRadius=200 (pill-shaped)                 | 1.000 | 0.892 | `CornerRadiusFractionAtMost(0.5)` |

## Status snapshot

- Verifier framework: stable. 50/50 OK on `qa_verifiers.py`.
- Task 17: round-1 strict FPs from 57→14 (all borderline acceptable). Round 3: 0.
- delivery-1/task_17/verifier.py is synced.
