# Task 07 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_07_extended.py`

## Results

| Round                    | Cases | Strict FPs (≥0.95) |
|--------------------------|-------|---------------------|
| 1 (initial 100-case)     | 100   | 60+ → 17            |
| 3 (novel 30-case)        | 26    | 7                   |

After round 1 most "borderline" 1.000s are intentional (perfect-control cases,
acceptable-extras cases, frame-extras-with-design-intact cases, event-log extras).

## What was fixed (round 1)

### New primitives added
- `DistinctTypedSolidColors(layer_type, minimum, tolerance)` → fill_checks.py
  — distinct fills among ONE specific layer_type, excluding frame fills that
  would otherwise count toward `DistinctSolidColors` and inflate the threshold.

### task_07 critical checks now catch
- A1, A4, A7, A9 (wrong vector counts): `ShapeCount("vector", equals=2)`
- B11, B17 (same/near-identical grays): `DistinctTypedSolidColors`
- B12-B16, B20 (image / gradient / stroke-only / stacked fills): `AllFillTypeIs("vector", "solid")` + `FillCountAtMost`
- B18, B19, J91, J92 (visibility tricks): `LayerVisible("vector")` + `FillOpacityAtLeast`
- C21, C22, C29, C30 (sizing extremes): `LayerSizeAtLeast` + `AllLayerWidthFraction`
- C24, C25 (extreme aspect): `LayerSizeAtLeast(min_w=20, min_h=20)`
- D31, D32, D33, D34, J97 (off-frame): `AllLayerBoundsInside(vector, frame)`
- E41-E47, E50 (rotation/zero size): `LayerRotationEquals(vector, 0, tol=2.0)`
- E44, E45, F55 (flipped): `NoLayerFlipped(vector)`
- G61 (frame rotated): `LayerRotationEquals(frame, 0, tol=2.0)`
- G66, G67 (frame size off): `FrameSizeEquals(1000, 400, tol=10)`
- G69, I82, I87, I88, I89, I90 (split / no-frame structure): `LayerInsideFrame("vector")` + `ChildCountAtLeast("frame", 2)`

## Round 3 — surviving novel-deception cases

Authored 26 NEW edge cases (`qa_per_task/task_07_round3.py`).

| Case  | What it does                          | Final | Status |
|-------|---------------------------------------|-------|--------|
| K1    | both rotated 1.5° (under 2° tol)      | 1.000 | Borderline (under tolerance, accepted) |
| K3    | red+blue (NOT gray shades)            | 1.000 | Known limitation — verifier doesn't enforce gray hue |
| K4    | purple+cyan                            | 1.000 | Same as K3 |
| K6    | vectors with cornerRadius=100          | 1.000 | Vectors don't naturally have corner radius semantics |
| K7    | far-vector drawn on top of near-vector | 1.000 | Known limitation — same-type role disambiguation impossible |
| M5    | both vectors piled at exact same pos   | 1.000 | Borderline (technically overlap, distinct colors) |
| M6    | frame 1010x410 (within 10px tol)       | 1.000 | Within tolerance — correct pass |

## Critical-flag changes

- Fundamentals: `critical=[0]` (ShapeCount("vector", equals=2))
- Alignment: 8 new critical checks (overlap, frame size, rotation, size-at-least, width-fraction, bounds-inside, no-flipped)
- Color: 5 critical (all-fill-type, distinct-typed-solid, fill-count-at-most, fill-opacity-at-least, layer-visible)
- Structure: 2 critical (LayerInsideFrame, ChildCountAtLeast=2)
- Event: 2 critical (ToolUsed("pen"), EventTypeCountAtLeast("create_vector", ≥2))

## Harness handlers

No new harness handlers required — existing `mutate_for_geometry` already handles
all primitives used. `DistinctTypedSolidColors` works because synth_layer assigns
idx-based colors that are distinct beyond 0.05 tolerance.

## Known limitations

- **Hue/saturation enforcement**: prompt says "gray" but verifier accepts any
  distinct colors. Adding gray-only check would require new saturation primitive.
- **Same-type z-order**: "near in front of far" can't be enforced because both
  are `vector` — no role-disambiguation hook for same-type stacking.
- **Same-position duplicates**: two vectors at identical (x,y,w,h) technically
  satisfy overlap + distinct colors; visually they look like one mountain but
  the verifier treats them as 2 layered.
