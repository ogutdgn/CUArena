# Task 08 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_08_extended.py`

## Results

| Round                    | Cases | Strict FPs (≥0.95) |
|--------------------------|-------|---------------------|
| 1 (initial 100-case)     | 100   | 60+ → 21            |
| 3 (novel 26-case)        | 26    | 6                   |

## What was fixed (round 1)

### New primitives added
- `DistinctTypedStrokeColors(layer_type, minimum, tolerance)` → stroke_checks.py
  — distinct stroke paint colors among ONE specific layer type, excluding strokes
  on other types (e.g., a frame's stroke shouldn't count toward the wave's
  "two distinct blues" requirement).
- `AllStrokeExists(layer_type)` → stroke_checks.py (also used by other tasks via linter)
  — every layer of layer_type has a visible non-zero-weight stroke. Stricter
  than `StrokeExists` (≥1 layer).

### task_08 critical checks now catch
- A1, A2, A5, A9 (wrong vector counts): `ShapeCount("vector", equals=2)`
- A8, B16, B17, F51, F52, K7 (no/wrong stroke): `AllStrokeExists`
- B11, B12, B18, B19, K2 (same/near-identical strokes / gradient): `DistinctTypedStrokeColors`
- B14, B15, C26 (wrong stroke weight): `StrokeWeightEquals(weight=4, tol=1.5)`
- B20, J91, J92 (visibility tricks): `LayerVisible`
- C21-C24, F58 (size extremes): `LayerSizeAtLeast(20, 20)` + `AllLayerWidthFraction`
- C28-C30 (full-frame / 0×0): same primitives
- D31-D34, D40, J97 (off-frame): `AllLayerBoundsInside(vector, frame)`
- E41-E46 (rotation): `LayerRotationEquals(vector, 0, tol=2)`
- E43, E44 (flipped): `NoLayerFlipped(vector)`
- F54, F55 (1px-tall): `LayerSizeAtLeast`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`
- G66, G67 (frame size off): `FrameSizeEquals(1000, 300, tol=10)`
- G69, I82, I87, I88, I89, I90 (split / no-frame): `LayerInsideFrame` + `ChildCountAtLeast`
- H71-H74 (no pen / no create_vector): existing event critical checks
- D36 (no overlap): `LayersOverlap(vector, vector)`

## Round 3 — surviving novel-deception cases

Authored 26 NEW edge cases (`qa_per_task/task_08_round3.py`).

| Case  | What it does                          | Final | Status |
|-------|---------------------------------------|-------|--------|
| K1    | both rotated 1.5° (under 2° tol)      | 1.000 | Borderline (under tol, accepted) |
| K3, M3| stroke 5.4px (within 1.5 tol)         | 1.000 | Within tol — correct pass |
| K4    | vectors with cornerRadius=50           | 1.000 | Vectors don't have native cornerRadius semantics |
| K5    | red strokes (not blue)                 | 1.000 | Known limitation — verifier doesn't enforce blue hue |
| K6    | green strokes (not blue)               | 1.000 | Same as K5 |
| M5    | frame 1010×310 (within 10px tol)       | 1.000 | Within tol — correct pass |

## Critical-flag changes

- Fundamentals: `critical=[0]` (ShapeCount("vector", equals=2))
- Alignment: 8 critical (frame size, vector rotation, frame rotation, size-at-least,
  width-fraction, bounds-inside, no-flipped, layers-overlap)
- Color: 4 critical (AllStrokeExists, StrokeWeightEquals, DistinctTypedStrokeColors, LayerVisible)
- Structure: 2 critical (LayerInsideFrame, ChildCountAtLeast=2)
- Event: 2 critical (ToolUsed("pen"), EventTypeCountAtLeast("create_vector", ≥2))

## Harness handlers added

- `DistinctTypedStrokeColors`: assigns visibly-distinct stroke colors to each layer
  of layer_type so the per-type stroke distinct-color check passes for the synthetic
  perfect log.

## Known limitations

- **Hue/saturation enforcement**: prompt says "blue" but verifier accepts any
  distinct stroke colors. Adding a blue-only check would require new color-space
  primitive (HSL hue range).
- **Stroke caps**: prompt mentions "rounded line caps" — current schema has no
  `cap_style` field, so this isn't enforced.
- **Identical bbox**: two vectors at identical (x,y,w,h) technically satisfy
  overlap + distinct stroke colors; visually they look like one stroke but
  the verifier treats them as 2 layered.
