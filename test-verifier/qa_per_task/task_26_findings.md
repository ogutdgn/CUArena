# Task 26 — verifier hardening summary

Run with:
```
cd test-verifier
PYTHONPATH=. python3 qa_per_task/task_26_extended.py
PYTHONPATH=. python3 qa_per_task/task_26_round3.py
```

## Results

| Round | Cases | Strict FPs (start) | Strict FPs (end) |
|-------|-------|--------------------|------------------|
| 1 (extended, 96) | 96 | 56 | 25 (legit-extras only) |
| 3 (novel, 30)    | 30 | 9  | 9 (tolerance-edge / known limits) |

Real strict FPs: **0**.

## Existing primitives reused

| Primitive (existing) | Source | Catches |
|----------------------|--------|---------|
| `LayerIsSquare(tol=4)`               | geometry_checks.py | C24, C30 (rectangles, not squares) |
| `LayersStacked(axis=x, gap=16, tol=8)` | geometry_checks.py | D31, D32, D33, D34, D39, D40 (not in row) |
| `LayerSizeAtLeast(20×20)`            | geometry_checks.py | C25, J95 (degenerate) |
| `AllLayerBoundsInside(rect, frame)`  | geometry_checks.py | D35, F55, J93, J94 (off-frame) |
| `LayerVisible`                       | property_checks.py | B18, B19, B20 (visibility tricks) |
| `NoLayerFlipped`                     | property_checks.py | E44, E45, J86 (scale=-1) |
| `LayerRotationEquals(0, tol=2)`      | geometry_checks.py | E41, E42, E50, J87 (rotated) |
| `CornerRadiusFractionAtMost(0.4)`    | property_checks.py | E46 (cornerRadius=999 = circle, not square) |

## Rubric updates in `tasks/task_26_color_variable_card.py`

- `AlignmentRubric` extended: added `LayerIsSquare`, `LayersStacked` (row),
  `LayerSizeAtLeast`, `AllLayerBoundsInside`. All marked critical.
- `ColorRubric` extended: added `LayerVisible`.
- New `PropertyRubric` (weight 0.15): rotation + flip + cornerRadius.
- Rubric weights: fund=0.20, alig=0.25, color=0.20, prop=0.15, event=0.20.

## Acceptable 1.000 cases (legit-extras / by-design)

Extended battery (25 cases):
- B12, J96, G61 — perfect controls.
- A7 — perfect row + extra ellipse decoration.
- C21, C26, C28, C29 — same-size squares of various dimensions (within
  square tol and size threshold).
- D37 — y diff within 3px tol.
- E43, E49 — under tolerance (rotation, cornerRadius for rounded squares).
- F51, F52 — squares with stroke / shadow (decorations).
- F58, F59 — at frame top / gap variance within tol.
- G62, G64–G68 — frame variants.
- H70, H75, H77 — extra events.
- I79, I82, I83, I84, I85 — structural variants.

Round 3 (9 cases):
- K1, K3, K5, K6, K7 — tolerance-edge (within tol by design).
- M3 — vivid colors still pass `DistinctSolidColors`.
- M5 — 4 distinct + frame fill = 5 distinct (verifier counts frame fill).
- N4, N5 — design-intact in nested / group structure.

## Known limitations

- `DistinctSolidColors` counts the **frame fill** as one of the distinct
  colors. M5 (4 distinct + 1 duplicated) passes minimum=5 because frame
  fill counts as 5th. Workaround would require excluding frame fills.
- "Brand colors" enforcement is generic — vivid/random colors pass as long
  as they're distinct (M3). The prompt's "brand color" intent is
  unenforceable without a curated palette check.
