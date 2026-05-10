# Task 04 — verifier hardening summary

6 same-size squares arranged in a hexagonal ring with rainbow colors.

## Results
| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | high → 20 (most are design-intact extras/variants) |
| 3 (novel 30-case) | 30 | 8 (all tolerance-edge or design-variant) |

## New primitives added
| Primitive | File | Catches |
|-----------|------|---------|
| `LayerAllSquare` | `verifier/checks/geometry_checks.py` | EVERY rectangle must be square (catches "5 squares + 1 wide rect") |

(`LayerGroupAllInSameFrame`, `LayerAllCircular` were added by prior tasks and reused here.)

## Critical-flag changes
- AlignmentRubric: 11 critical checks — `LayersSameDimensions`, `RadialDistribution`, `LayerAllSquare`, `LayerSizeAtLeast`, `LayerInsideFrame`, `LayerGroupAllInSameFrame`, `AllLayerBoundsInside`, `LayerRotationEquals(rectangle)`, `NoLayerFlipped`, `LayerRotationEquals(frame)`, `CornerRadiusFractionAtMost`.
- ColorRubric: 5 critical — `AllFillTypeIs`, `DistinctSolidColors`, `LayerVisible`, `FillCountAtMost`, `FillOpacityAtLeast`.

## Harness handlers added/changed
- `LayerAllSquare` handled identically to `LayerIsSquare` in Pass 1 (set h=w).

## Known limitations
- Plausibly-valid ring sizes (radius variants, side variants) score 1.000.
- Tolerance-edge tests (1.9° rotation, 80x82 within 3-tol, 23/80 cornerRadius) all within design tolerance.
- M5 (radius=15 near-concentric) — RadialDistribution permits when scale-relative.
- Frame variants (G62-65, G68) accepted since prompt doesn't specify frame size/style.
- Extras outside ring (A9, F55) accepted since the 6 ring squares ARE correct.
