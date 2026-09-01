# Task 43 — verifier hardening summary

Compass rose: sand circle + 4 N/E/S/W triangles + gold center pivot.

## Results
| Round | Cases | Strict FPs | Notes |
|-------|-------|------------|-------|
| 1 (initial 100-case) | 100 | ~50 → 15 | most remaining are control/extras-tolerated/tol-edge |
| 3 (novel 30-case) | 28 | 5 → 0 | RadialDistribution closed remaining gaps |

## New primitives used
| Primitive | File | Catches |
|-----------|------|---------|
| `AllLayersAreCircular` | `geometry_checks.py` | every ellipse round (sand AND gold center) — catches squashed sand/center oval |
| `FrameCountAtMost` | `geometry_checks.py` | exactly 1 page-root frame |
| `DistinctTypedSolidColors` | `fill_checks.py` (existing) | distinct N (red) vs gray triangles; distinct sand vs gold ellipses |
| `RadialDistribution` | `geometry_checks.py` (existing) | triangles spread radially around the center — catches piled / cornered triangles |
| `LayerSmallerThanLayer` | `geometry_checks.py` (existing) | center much smaller than sand |
| `LayerAreaRatioAtLeast` | `geometry_checks.py` (existing) | sand dominates center |
| `LayerCenteredOnLayer` (same-type) | `geometry_checks.py` (existing) | gold center on sand center |

## Critical-flag changes
- All 20 alignment checks marked critical.
- Color: distinct fills, gold center, sane fill stack & opacity.
- Structure: all shapes in same frame on page 0.

## Harness handlers added/changed
- `LayerCenteredOnLayer` — added same-type case (largest as anchor; smallest aligned to center). Previously fell through when type_a == type_b.
- `AllLayersAreCircular` — added to Pass 1 aspect-ratio handler so synthetic ellipses get h=w.
- `DistinctTypedSolidColors` — assigns 8-color palette so synthetic per-type distinct colors emerge.

## Known limitations
- Tolerance-edge cases (4° rotation under 5° tolerance, 91° spacing under 15° tol) intentionally accepted.
- "compass + text label" still passes — text doesn't violate any check.
- Frame nesting / image fill on frame are cosmetic and tolerated.
