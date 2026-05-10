# Task 03 — verifier hardening summary

1 yellow center circle + 8 radial colored petals (ellipses).

## Results
| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | 52 → 26 (most are valid size/extras variants) |
| 3 (novel 30-case) | 30 | 8 (all tolerance-edge or radial variants) |

## New primitives added
| Primitive | File | Catches |
|-----------|------|---------|
| `LayerAllCircular` | `verifier/checks/geometry_checks.py` | EVERY ellipse must have w≈h (catches the case where 8 circular petals make the existing `LayerIsCircular` pass even with a 60×30 oval center) |
| `LayerAllSameSize` | `verifier/checks/geometry_checks.py` | Variant of LayersSameDimensions that's strictly per-layer (added as helper, not used directly here) |

(`LayerGroupAllInSameFrame` was added as part of task 02 work.)

## Critical-flag changes
- AlignmentRubric: added critical checks: `LayerAllCircular`, `LayerSizeAtLeast`, `LayerInsideFrame`, `LayerGroupAllInSameFrame`, `AllLayerBoundsInside`, `LayerRotationEquals(ellipse)`, `NoLayerFlipped`, `LayerRotationEquals(frame)`.
- ColorRubric: added critical: `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`.

## Harness handlers added/changed
- Pass 1 in `qa_verifiers.py`: `LayerAllCircular` and `LayerAllSquare` now treated like `LayerIsCircular`/`LayerIsSquare` (set h = w).

## Known limitations
- The verifier accepts plausibly-valid radial flowers at different radii (K6: r=100, K7: r=350) — the prompt allows for any radius.
- Slight size variation among petals (K9, ±2px) tolerated — within `LayerAllCircular` tolerance.
- M4 (petals at radius ~5) almost concentric with center — `RadialDistributionExcludeCentral` with `radius_tolerance_frac=0.25` permits this when scale-relative.
- Color tolerance (`DistinctSolidColors` at 0.05, `CentermostLayerHasColor` at 0.20) allows near-gray distinct or near-yellow center.
- Prompt does not mandate single frame size, so frame variant tests (G62-65, G68-69) often score 1.000 since "design intact in valid frame" is acceptable.
