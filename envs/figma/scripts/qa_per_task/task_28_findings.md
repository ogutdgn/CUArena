# Task 28 — verifier hardening summary

Spec: 1 large rectangle (placeholder) + 2 diagonal lines crossing through it (X-cross).

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case battery) | 100 | ~50 → ~20 (most are loose-prompt acceptable) |
| 3 (novel 30-case battery) | 27 | 3 (K6 mirrored lines, K7 tiny rect — both legitimate edge cases) |

## New primitives added

| Primitive | File | Catches |
|-----------|------|---------|
| `AllLayerStrokeVisible` | `verifier/checks/stroke_checks.py` | B17 (alpha=0 strokes), F60 (no strokes), L4, L5, K10 |

## Critical-flag changes

Added to `task_28_edited_photo.py`:

- **AlignmentRubric** — added critical checks:
  - `LayerRotationEquals(rectangle, degrees=0, tolerance=2.0)` (catches E41–E43, J92)
  - `LayerRotationEquals(frame, degrees=0, tolerance=2.0)` (catches G61)
  - `NoLayerFlipped(rectangle)` (catches E44)
  - `LayerSizeAtLeast(rectangle, min_w=40, min_h=40)` (catches C25, M2, M4)
  - `AllLayerWidthFraction(rectangle, frame, min_frac=0.05, max_frac=0.90)` (catches C29 too small, M1 full frame)
  - `AllLayerBoundsInside(rectangle, frame, tolerance=4.0)` (catches D32, D33, M5)

- **ColorRubric** — added critical checks:
  - `FillCountAtMost(rectangle, max_count=1)` (catches B20 stacked fills)
  - `FillOpacityAtLeast(rectangle, min_opacity=0.5)` (catches B19, L1)
  - `LayerVisible(rectangle)` (catches B18, J95, J96, L2, L3)
  - `AllLayerStrokeVisible(line)` (catches B17, F60, K10, L4, L5)

- **StructureRubric** (new) — added critical checks:
  - `LayerInsideFrame(rectangle)` (catches G68)
  - `LayerInsideFrame(line)` (catches I82, I87)

## Harness handlers added/changed

`qa_verifiers.py` (mutate_for_geometry):
- Added a final-pass `LinesOnDiagonal` handler that re-runs after `AllLayerWidthFraction` resizes the rect, so lines actually span the rect's final w/h.
- New `AllLayerStrokeVisible` handler: ensures every layer of given type has a visible stroke with alpha >= min_alpha and weight >= min_weight.

## Known limitations

- **K6 (mirrored lines)**: lines with scaleX=-1 still visually go corner-to-corner. The geometry-only check passes.
- **K7 (tiny rect)**: 80x80 is at the lower bound. "Large rectangle" is subjective.
- **B16 (olive color)**: prompt doesn't constrain rect color, so any solid passes.
- **Borderline 1.000s**: extras-present designs (A8, H75, H80) and frame variants (G62-G65) score 1.0. Verifier accepts decorations if core design is correct.
