# Task 02 — verifier hardening summary

5 horizontal rectangle bands stacked top-to-bottom in sunset colors.

## Results
| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | 45 → 20 (most are "design intact + extras") |
| 3 (novel 30-case) | 30 | 9 → 8 (all tolerance-edge) |

## New primitives added
| Primitive | File | Catches |
|-----------|------|---------|
| `LayerGroupAllInSameFrame` | `verifier/checks/structure_checks.py` | All N rectangles must be direct children of one frame (catches split-across-frames, in-group, on-page-no-frame) |

## Critical-flag changes
- AlignmentRubric: added 7 new critical checks: `LayerGroupAllInSameFrame`, `AllLayerBoundsInside`, `LayerSizeAtLeast`, `LayerRotationEquals(rectangle)`, `NoLayerFlipped`, `CornerRadiusFractionAtMost`, `LayerRotationEquals(frame)`.
- ColorRubric: added 3 new critical checks: `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`.
- Tightened: `LayersAligned(center_x, tolerance=3.0)` (was 5.0); `LayersStacked(tolerance=4.0)` (was 8.0).

## Harness handlers added/changed
- Pass 8.5 in `qa_verifiers.py`: when `LayerGroupAllInSameFrame` is required, move all matching layers under the first frame as direct children.

## Known limitations
- The `LayersHaveColorOrder` tolerance is 0.20 (very permissive for sunset color subjectivity) — K2 passes with pink slightly off.
- K1 (bands 20×200): bands at minimum height pass — accepted as legit small composition.
- K3, K6, K7, M3: tolerance-edge cases (rotation 1.9°, gap 3px, width 3px-off, gap 1px) — all genuinely within design tolerance.
- K5 (z-order reversed): bands sorted by Y still show correct color order visually; not a real deception.
- The 20 "FPs" in round 1 are largely design-intact with acceptable extras (extra unrelated shapes, distribute/align toolbar use, frame variations).
