# Task 45 — verifier hardening summary

8-point deep-blue star + smaller centered yellow circle on top.

## Results
| Round | Cases | Strict FPs | Notes |
|-------|-------|------------|-------|
| 1 (initial 100-case) | 100 | ~53 → 21 | extras-tolerated / control / cosmetic |
| 3 (novel 30-case) | 28 | 2 | K4/K5 within color tol (legit) |

## New primitives used
| Primitive | File | Catches |
|-----------|------|---------|
| `AllLayersAreCircular` | `geometry_checks.py` | every ellipse round |
| `FrameCountAtMost` | `geometry_checks.py` | exactly 1 page-root frame |
| `LayerSmallerThanLayer` (existing) | `geometry_checks.py` | circle smaller than star |
| `AllSolidColorEquals` (existing) | `fill_checks.py` | every star/circle has correct color |
| `LayerInFrontOf` (existing) | `geometry_checks.py` | circle drawn after star (z-order) |

## Critical-flag changes
- All 20 alignment checks marked critical: bounds-inside, centered, on-top, in-front-of, circular, frame size, in-frame, sane sizing, upright, no-flip, smaller-than-larger, single-frame.
- All 10 color checks marked critical: solid fills, every-star-deep-blue, every-circle-yellow, fill-count, fill-opacity, layer-visible.
- Structure: shapes in same frame on page 0.
- Event: star + ellipse tools required.

## Harness handlers added/changed
- (None — relies on existing handlers; `LayerCenteredOnLayer` cross-type handles star/ellipse pair, `LayerBoundsInside` handles inside.)

## Known limitations
- Cosmetic attributes (`cornerRadius` on ellipse, `innerRatio` on star) tolerated.
- "emblem + extras" (extra polygon, text) tolerated as long as star/ellipse counts equal 1 each.
- Within-tolerance color shifts pass (tol=0.20 absorbs minor recolors).
