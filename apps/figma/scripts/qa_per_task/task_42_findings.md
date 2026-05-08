# Task 42 — verifier hardening summary

Bell icon (yellow-gold pen-drawn vector) + clapper circle + red badge with 2px white stroke.

## Results
| Round | Cases | Strict FPs | Notes |
|-------|-------|------------|-------|
| 1 (initial 100-case) | 100 | ~65 → 24 | most remaining are legitimate-extras / tol-edge / control |
| 3 (novel 30-case) | 28 | 4 → 2 | K4 (color within tol, OK), M2 (cornerRadius cosmetic) |

## New primitives added
| Primitive | File | Catches |
|-----------|------|---------|
| `AllLayersAreCircular` | `geometry_checks.py` | every ellipse must be round (not just one) — catches squashed clapper/badge |
| `FrameCountAtMost` | `geometry_checks.py` | exactly N top-level frames — catches design split across frames |
| `StrokeRendersVisible` | `stroke_checks.py` | stroke alpha ≥ min and stroke.visible — catches transparent / hidden strokes |

## Critical-flag changes
- All Alignment checks (18) marked critical: circular ellipses, frame size, bounds-inside-frame, sane sizing, upright, no-flip, ellipse-overlaps-bell, ellipses-smaller-than-bell, frame-count-at-most-1, ellipse-below-bell.
- All Color checks except StrokeWeight, StrokeColor → kept critical for prompt-explicit "2px white stroke."
- Structure: bell + ellipses must be in same frame on page 0.
- Event: pen + ellipse tools required.

## Harness handlers added/changed
- `DistinctTypedSolidColors` — assigns 8-color palette so 2 distinct ellipse fills emerge in synthetic perfect log.
- (No other harness changes needed — existing handlers cover `LayerNextTo`, `LayerSmallerThanLayer`, `AllLayerWidthFraction`, `AllLayerBoundsInside`, `LayersOverlap`.)

## Known limitations
- Cosmetic attribute changes (`cornerRadius` on vector) don't affect rendering for vector layers; treated as non-defect.
- "bell + extras" (extra dot, extra rectangle deleted) tolerated since prompt allows it (uses `ShapeCountAtLeast`).
- Frames with stroke / image fill / nested still pass — the bell remains correctly bounded inside one frame in those cases.
