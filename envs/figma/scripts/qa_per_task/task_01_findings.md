# Task 01 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_01_extended.py`

## Results

| Metric                        | Before round 1 | After round 1 | After round 2 |
|-------------------------------|----------------|---------------|---------------|
| Cases scoring 1.000           | ~35            | 28            | 22            |
| Strict false-positives @1.000 | ~25            | 6             | **0**         |
| Total checks in task_01       | 17             | 30            | 38            |
| Critical checks               | 7              | 23            | 32            |

## What was fixed (this round)

### New primitives added
- `AllFillTypeIs(layer_type, kind)` → fill_checks.py
- `FillCountAtMost(layer_type, max_count)` → fill_checks.py
- `LayerSizeAtLeast(layer_type, min_w, min_h)` → geometry_checks.py
- `AllLayerWidthFraction(inner_type, parent_type, min_frac, max_frac)` → geometry_checks.py
- `SmallerLayerInsideLarger(layer_type, tolerance)` → geometry_checks.py
- `AllLayerBoundsInside(inner_type, outer_type, tolerance)` → geometry_checks.py
- `NoLayerFlipped(layer_type)` → property_checks.py
- `LayerCenteredOnLayer` extended with `axis="x"|"y"|"both"` parameter

### task_01 critical checks now catch
- B13–B20 (image fill / no fill / gradient / stacked-fill workarounds): `AllFillTypeIs` + `FillCountAtMost`
- C25–C30 (skinny / oversized body, roof, windows): `AllLayerWidthFraction`
- C24 (windows bigger than body): `AllLayerWidthFraction(ellipse, frame, ≤0.20)`
- D38, D36 (house off-frame): `AllLayerBoundsInside(*, frame)`
- D39, D40 (roof not centered on body): `LayerCenteredOnLayer(polygon, rectangle, axis="x")`
- E42, E43 (roof rotated): `LayerRotationEquals(polygon, 0)`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`
- J86 (body mirrored): `NoLayerFlipped(rectangle)`
- J87 (body rotated): `LayerRotationEquals(rectangle, 0)`
- J94 (1×1 windows): `LayerSizeAtLeast(ellipse, 10, 10)`
- J95 (negative-y coords): `AllLayerBoundsInside(*, frame)`

## Round 3 — hunting unknown unknowns

Authored 31 NEW edge cases not in the original 96-case battery
(`qa_per_task/task_01_round3.py`). Found 13 new false positives → all but 1
caught after round-3 fixes.

| Case  | What it does                          | Old   | New   | Caught by |
|-------|---------------------------------------|-------|-------|-----------|
| K3    | body rotated 4° (under 5° tol)        | 1.000 | 0.896 | tighten rotation tol → 2° |
| K5    | roof rotated 4°                       | 1.000 | 0.896 | tighten rotation tol → 2° |
| K6    | body cornerRadius=200 (looks circle)  | 1.000 | 0.896 | `CornerRadiusFractionAtMost(0.4)` |
| K7    | door cornerRadius=70 (looks circle)   | 1.000 | 0.896 | same |
| K8    | roof under body in z-order            | 1.000 | 0.896 | `LayerInFrontOf(polygon, rectangle)` |
| K9    | door above roof in z-order            | 1.000 | 0.896 | same |
| K10   | body in front of everything in z-order| 1.000 | 0.896 | same |
| L2    | body fill alpha=0 (invisible)         | 1.000 | 0.892 | `LayerVisible` |
| L3    | body fill visible=False               | 1.000 | 0.892 | same |
| L4    | body layer opacity=0                  | 1.000 | 0.892 | same |
| N2    | roof in different frame from body     | 0.950 | 0.875 | `StructureRubric` made critical |
| N3    | each shape in its own frame           | 0.950 | 0.875 | same |
| M3    | 3 small roofs instead of 1 big        | 0.950 | 0.950 | accepted (count-extras at 0.95) |

### New primitives added in round 3
- `CornerRadiusFractionAtMost` (property_checks.py)
- `LayerVisible` (property_checks.py) — checks layer opacity, visible flag, fill alpha + opacity, fill visible flag
- `LayerInFrontOf` (geometry_checks.py) — every type_a layer drawn after all type_b (z-order, no overlap requirement)
- `LayerOnTopOf` extended with `require_overlap=False` parameter

### Rubric framework change
- `StructureRubric` now accepts `critical=` parameter. All 4 structure checks
  in task_01 are now critical (catches split-frame designs).

## Round 2 — closing the 6 remaining gaps

| Case  | Old score | New score | New primitive that fired |
|-------|-----------|-----------|--------------------------|
| B19   | 1.000     | 0.890     | `FillOpacityAtLeast(min=0.5)` |
| C23   | 1.000     | 0.887     | `LayerAreaRatioAtLeast(rectangle, min_ratio=3)` |
| D31   | 1.000     | 0.896     | `SmallerLayerCenteredOnLargerEdge(rectangle, "bottom")` |
| D35   | 1.000     | 0.896     | same as D31 |
| E41   | 1.000     | 0.896     | `LayerAboveLargestLayer(polygon, rectangle)` |
| F57   | 1.000     | 0.896     | `AllLayerBoundsInside(ellipse, rectangle)` |

### New primitives added in round 2
- `FillOpacityAtLeast` (fill_checks.py)
- `LayerAreaRatioAtLeast` (geometry_checks.py) — largest area / second-largest ≥ min_ratio
- `SmallerLayerCenteredOnLargerEdge` (geometry_checks.py) — door-on-body-bottom convention
- `LayerAboveLargestLayer` (geometry_checks.py) — polygon must sit ABOVE the largest rectangle, not just any rectangle

### Harness updates (qa_verifiers.py)
- `AllLayerWidthFraction` now scales `h` proportionally when the layer is a container
  in any `AllLayerBoundsInside` check (not just when `LayerIsCircular` requires it).
- `SmallerLayerInsideLarger` final pass now bottom-aligns inner with outer (door-on-body
  convention), and sizes inner so `LayerAreaRatioAtLeast` is satisfied.

## Acceptable 1.000 (intended passes)

| Case  | Why 1.000 is correct |
|-------|----------------------|
| B11   | 4 distinct via frame fill (counted toward color count) |
| B12   | perfect house (control) |
| C22   | body 50% of frame (within range) |
| D37   | house centered (perfect) |
| E46   | roof bottom 5px above body — inside tolerance |
| E49   | no overhang — debatable but acceptable design |
| F60   | windows touching door's edges — not strictly forbidden |
| G62-68| frame-with-extras / nested / translated — structurally fine |
| G66   | close to frame edge — still inside |
| H71-78| event-log extras (align, distribute, deletions, extra fills) |
| I83   | 3-deep nested frames — house still inside a frame |
| I85   | house on page 2 — verifier walks all pages |
| J96   | perfect house (control) |

## Status snapshot

- Verifier framework: stable. 50/50 OK on `qa_verifiers.py`. 96/96 cases run on task_01.
- Task 01: false-positive rate dropped from ~25 to 6 strict cases.
- delivery-1/task_01/verifier.py is synced.
- Remaining 6 strict FPs are documented limitations (not fixable without
  cross-type role disambiguation: "this rectangle is body, this is door").
