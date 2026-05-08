# Task 47 — verifier hardening summary

Task: 8-point warm-orange star + smaller centered cream circle on top.

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_47_extended.py`

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | ~56 → 33 |
| 3 (novel 30-case) | 31 | — → 4 |

(Most round-1 1.000 cases are legitimate: control cases A10/J100, in-frame
variants G61–G70/I81–I90, hierarchy variants, off-canvas, near-warm-orange
within color tolerance, decorative extras A8/A9.)

## New primitives added

| Primitive | File | Catches |
|-----------|------|---------|
| `LayerSmallerThanLayer(smaller_type, larger_type, max_frac)` | geometry_checks.py | Cross-type "smaller circle" deception: circle ≥ 70% of star |
| `LayerShortDimensionAtMost(layer_type, max_value)` | geometry_checks.py | Star giant-size (e.g., 5000×5000 absurd) |

## Critical-flag changes

Task 47 had 7 critical checks across 4 rubrics; now has 28 critical across 4 rubrics.

- `AlignmentRubric` now critical[0..12] — every alignment check is prompt-mandated
- `ColorRubric` now critical[0..9] — solid-fill, color match, no stacked, opacity, visibility
- `FundamentalsRubric` retained critical[0,1,2]
- `EventRubric` retained critical[0,1]

## Harness handlers added

- `LayerSmallerThanLayer` → Pass 5: scales `smaller_type` so its short dim ≤ 0.7·max_frac × largest `larger_type`'s short dim
- `LayerShortDimensionAtMost` → Pass 5: caps `w` and `h` at `max_value`

## Round-3 surviving 1.000 cases (4)

| Case | What it does | Verdict |
|------|--------------|---------|
| K1   | star rotated 1.5° (under 2° tol) | tolerance edge — accepted |
| N1   | star in frame, circle on page | known limitation — prompt doesn't mandate same parent |
| N2   | badge in component (not frame) | known limitation — prompt doesn't ban components |
| N3   | circle as child of star | known limitation — flat-vs-nested hierarchy unspecified |

## Caught by new checks (round-3 examples)

| Case | Old | New | Caught by |
|------|-----|-----|-----------|
| K2   | 1.000 | 0.865 | LayerBoundsInside (corner = on edge) |
| K5   | 1.000 | 0.865 | LayerSmallerThanLayer (71% > 70%) |
| K6   | 1.000 | 0.865 | LayerInFrontOf (circle behind) |
| K7   | 1.000 | 0.865 | StarInnerRatioEquals (0.85 vs 0.5±0.3 boundary) |
| L1–L5| 1.000 | 0.825-0.863 | LayerVisible / FillOpacityAtLeast |
| M1   | 1.000 | 0.865 | LayerSmallerThanLayer (same size) |
| M2/M3| 1.000 | 0.837 | LayerSizeAtLeast (collapsed dimension) |
| M5   | 1.000 | 0.856 | LayerSmallerThanLayer (roles swapped) |
| O1–O5| 1.000 | 0.205-0.381 | ShapeCount + StarPointsEquals + ToolUsed |

## Status

- 50/50 OK on `qa_verifiers.py`
- Round-3 strict FPs: 4 (≤ 5 target)
- delivery-1/task_47/verifier.py is synced
