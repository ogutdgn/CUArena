# Task 46 — verifier hardening summary

5 thin vertical rectangles of varying heights, side-by-side, sharing a common
bottom baseline (histogram-like).

## Results
| Round | Cases | Strict FPs | Notes |
|-------|-------|------------|-------|
| 1 (initial 100-case) | 100 | ~55 → 24 | extras-tolerated / control / cosmetic |
| 3 (novel 30-case) | 28 | 6 | all within tolerance — gap, baseline jitter, rotation, cornerRadius |

## New primitives used
| Primitive | File | Catches |
|-----------|------|---------|
| `FrameCountAtMost` | `geometry_checks.py` | exactly 1 page-root frame |
| `LayerAspectRatioGreaterThan` (existing) | `geometry_checks.py` | bars taller-than-wide (axis="vertical") |
| `LayersStacked` (existing) | `geometry_checks.py` | side-by-side with consistent gap |
| `LayersAllShareEdge` (existing) | `geometry_checks.py` | all share bottom baseline |
| `AllLayerWidthFraction` | `geometry_checks.py` | bars sane width relative to frame |

## Critical-flag changes
- All 11 alignment checks marked critical: stacked, baseline, taller-than-wide, frame size, in-frame, sized sanely, upright, no-flip, single-frame.
- 4 of 5 color checks marked critical (DistinctSolidColors deliberately not — varying heights, not hues).
- Structure: bars in same frame on page 0.
- Event: rectangle tool required.

## Harness handlers added/changed
- (None — relies on existing handlers; `LayersStacked` (final pass) re-stacks after sizing; `LayerAspectRatioGreaterThan` (final pass) ensures vertical aspect.)

## Known limitations
- "5 bars same exact height" tolerated (no variance check — could be intentional or marginal).
- Within-tolerance gap/baseline jitter, rotation, cornerRadius all pass.
- "5 bars + extras" tolerated since prompt focuses on the 5 bars.
