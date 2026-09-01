# Task 14 — verifier hardening summary

Run with:
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_14_extended.py`
- `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_14_round3.py`

## Results

| Round                          | Cases | Strict FPs (≥0.95) |
|--------------------------------|-------|--------------------|
| 1 (initial 100-case)           | 100   | 54 → 28            |
| 3 (novel 30-case)              | 29    | 7 (all acceptable) |

## What was fixed

### New primitives added
- `AllStrokeWeightWithinTolerance(layer_type, target_weight, tolerance)` → stroke_checks.py
  - Catches "1 of N has wrong stroke weight" (StrokeWeightEquals only checks ≥1).

### Reused primitives
- `AllStrokeExists`, `AllStrokeColorEquals` (existed) — now critical in task_14.

### Critical-flag changes — task_14 critical checks now catch
- A1, A2, A3, A4, A5, A6, A8: count != 4 → `ShapeCount("ellipse", equals=4)`
- C23, J93, J99: tiny / degenerate ellipses → `LayerSizeAtLeast(min=15)`
- D31, D37, D38: target off-frame → `AllLayerBoundsInside(ellipse, frame, 4)`
- C21, C27, C30: same-size circles → `LayerAreaRatioAtLeast(ellipse, min_ratio=1.4)`
- C25, C26, M2: oval not circle → `LayerIsCircular(tol=3)`
- D33, D34, D35, D39: not concentric → `LayersConcentric(tol=2)` (already there)
- E48: 1 ellipse no stroke → `AllStrokeExists`
- E49: 1 stroke wrong color → `AllStrokeColorEquals`
- E50: 1 stroke wrong weight → `AllStrokeWeightWithinTolerance`
- F51, F52, K8: stroke weight wrong → `AllStrokeWeightWithinTolerance`
- F55, F56: stroke color wrong → `AllStrokeColorEquals`
- B19, L1, L2, L3, L4: invisible → `LayerVisible` + `FillOpacityAtLeast`
- B20: stacked fills → `FillCountAtMost(1)`
- B16, C22, B17, B18, J95, J97: wrong colors → `LayersHaveColorOrder`
- E43, E44, M7: mirror/flip → `NoLayerFlipped`
- I81–I87, N1–N4: not in single frame → `StructureRubric` made critical
- O1, O2, O3: wrong type → `ShapeCount("ellipse", equals=4)` is critical

### Harness handlers added (qa_verifiers.py)
- `AllStrokeWeightWithinTolerance` handler — sets stroke weight to target_weight.

## Acceptable 1.000s (intended passes)
| Cases | Why 1.000 is correct |
|-------|----------------------|
| A7, A9, J96, J100 | controls / extras tolerated |
| C29 | sizes within shrink-tolerance |
| D32 | centers within tol=2px |
| D40 | control |
| E41, E42, E47, J94 | rotation invariant for circle |
| E45 | cornerRadius is no-op for ellipse |
| E46 | rotation 4° — could pass via `LayersConcentric` slack |
| F53, F54 | stroke alignment / dashed — prompt is silent |
| F58, F59 | stroke params within tolerance |
| G62, G63, G64, G65, G67, G70 | frame variants / nesting |
| H73, H76, H80 | event-log extras |
| I84, I85 | nested / page-2 |
| K1, K2, K3, K4 | under-tolerance variants |
| K7 | z-order moot for concentric circles |
| K9 | linear shrink is still nested/decreasing |
| M3 | rotated circles look identical |

## Known limitations
- Outermost-vs-innermost color order requires `LayersHaveColorOrder(sort_axis="size")`,
  which works only when sizes vary. If all 4 are same size, sort is unstable.

## Status snapshot
- Verifier framework: 50/50 OK on `qa_verifiers.py`.
- Task 14: from 54 strict 1.000s → 28 (mostly intended/borderline).
- delivery-1/task_14/verifier.py is synced.
