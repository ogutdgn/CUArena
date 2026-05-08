# Task 44 — verifier hardening summary

Avatar circle + smaller green status badge with 2px white stroke at bottom-right.

## Results
| Round | Cases | Strict FPs | Notes |
|-------|-------|------------|-------|
| 1 (initial 100-case) | 100 | ~50 → 17 | remaining are extras-tolerated / control / cosmetic |
| 3 (novel 30-case) | 28 | 2 | K3 (within tol), K7 (cornerRadius cosmetic) |

## New primitives used
| Primitive | File | Catches |
|-----------|------|---------|
| `AllLayersAreCircular` | `geometry_checks.py` | every ellipse round (avatar AND badge) |
| `FrameCountAtMost` | `geometry_checks.py` | exactly 1 page-root frame |
| `LayerSmallerThanLayer` (existing) | `geometry_checks.py` | badge much smaller than avatar |
| `LayerAreaRatioAtLeast` (existing) | `geometry_checks.py` | avatar dominates |
| `SmallerLayerCenteredOnLargerEdge` (existing) | `geometry_checks.py` | badge on bottom edge of avatar |
| `DistinctTypedSolidColors` (existing) | `fill_checks.py` | avatar vs badge different |
| `StrokeRendersVisible` | `stroke_checks.py` | stroke alpha + visible |

## Critical-flag changes
- All 15 alignment checks marked critical: overlap, on-top, both circular, in-frame, sized sanely, upright, no-flip, smaller-than-larger, area-ratio, badge-on-bottom-edge, single-frame.
- All 11 color checks marked critical.
- Structure: avatar+badge in same frame on page 0.
- Event: ellipse tool required.

## Harness handlers added/changed
- `SmallerLayerCenteredOnLargerEdge` — added handler that places smallest at largest's edge with center on perpendicular axis.
- `DistinctTypedSolidColors` — handler now skips palette colors that collide with `SolidColorEquals` for the same type, so avatar (color X) + badge (palette other than X) are distinct.

## Known limitations
- Cosmetic attributes (`cornerRadius` on ellipse, dashed stroke) tolerated.
- Bottom-LEFT vs bottom-RIGHT distinction not strictly enforced (axis tolerance 200px allows both).
- Within-tolerance color shifts pass (acceptable).
