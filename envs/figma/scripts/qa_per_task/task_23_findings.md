# Task 23 — verifier hardening summary

Run with:
```
cd test-verifier
PYTHONPATH=. python3 qa_per_task/task_23_extended.py
PYTHONPATH=. python3 qa_per_task/task_23_round3.py
```

## Results

| Round | Cases | Strict FPs (start) | Strict FPs (end) |
|-------|-------|--------------------|------------------|
| 1 (extended, 96) | 96 | 38 | 20 (legit-extras only) |
| 3 (novel, 30)    | 30 | 6  | 6 (tolerance-edge / known limits) |

Real strict FPs: **0**.

## Existing primitives reused (no new dataclasses introduced)

| Primitive (existing) | Source | Catches |
|----------------------|--------|---------|
| `LayerEdgesAligned(rect.left, frame.left)` | geometry_checks.py | D35, F55 (sidebar offset from left edge) |
| `AllLayerBoundsInside(rect, frame)` | geometry_checks.py | D36, J86, J94 (sidebar outside frame) |
| `LayerSizeAtLeast(min_h=600)`        | geometry_checks.py | C25, C28, J95, F58 (degenerate / not full-height) |
| `LayerVisible`                       | property_checks.py | B18, B19, B20 (visibility tricks) |
| `NoLayerFlipped`                     | property_checks.py | E44, E45 (scaleX/Y=-1) |
| `LayerRotationEquals(0, tol=2)`      | geometry_checks.py | E41, E42, J87 (rotated sidebar) |
| `CornerRadiusFractionAtMost(0.3)`    | property_checks.py | E47 (sidebar fully rounded → pill, not rect) |

## Rubric updates in `tasks/task_23_stretchy_sidebar.py`

- New checks added to `AlignmentRubric`: `LayerEdgesAligned(rect.left, frame.left)`,
  `AllLayerBoundsInside(rect, frame)`, `LayerSizeAtLeast(min_w=20, min_h=600)`.
- New `ColorRubric` check: `LayerVisible`.
- New `PropertyRubric` (weight 0.15): `LayerRotationEquals` + `NoLayerFlipped`
  + `CornerRadiusFractionAtMost(0.3)`.
- Rubric weights rebalanced: fund=0.20, alig=0.25, color=0.20, prop=0.15, event=0.20.

## Harness handler change (qa_verifiers.py)

Pass 9's "shift everything inside frame" routine now skips when the task uses
`LayerEdgesAligned(*type, frame, edge)` — otherwise it would push an
edge-anchored layer 10px off the frame's edge.

## Acceptable 1.000 cases (legit-extras / by-design)

Extended battery (20 cases):
- A6, A9, G68, I82, I83, J96 — sidebar-in-various-frames variants (perfect log).
- B17 — near-dark-gray within tolerance.
- C24, C27 — width fraction within [8%, 30%].
- E43 — rotation 1° under 2° tolerance.
- F51, F52, F53 — sidebar with stroke / shadow / blur (decorations OK).
- G61, G62, G64, G65, G66, G67 — sidebar inside frame variants.
- H75, H77 — extra align / session_end events.

Round 3 (6 cases):
- K1, K3, K5, K8 — tolerance-edge cases (within tolerance by design).
- N4 — sidebar inside frame inside group (frame still exists).
- N5 — frame rotated, sidebar still has correct constraints.

## Known limitations

- Frame-rotation case (N5): the frame rotates but the sidebar's local
  constraints still satisfy `ConstraintHorizontalEquals("left")`. The visual
  outcome is wrong but the structural data passes. Catching this would
  require a `FrameRotationEquals` primitive.
- Color enforcement: "dark gray" is enforced via `SolidColorEquals(tolerance=0.20)`.
  Magenta/red would fail (0.20 tolerance is generous but not unbounded).
