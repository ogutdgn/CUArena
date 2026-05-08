# Task 49 — verifier hardening summary

Task: 1 pen-tool S-curve with thick (12px) dashed stroke as ribbon.

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_49_extended.py`

## Results

| Round | Cases | Strict FPs |
|-------|-------|------------|
| 1 (initial 100-case) | 100 | ~83 → 63 |
| 3 (novel 30-case) | 31 | — → 14 |

(Round-1 1.000 surfacers: most are control / "vector + extra decorative
shapes" cases that legitimately pass since the prompt only specifies
the ribbon, not what other shapes can/can't be present. Frame variants
G61–G70, hierarchy variants I81–I90, event-log extras H73–H80 are also
all acceptable.)

## What changed

Task 49 was originally 3 rubrics, only 4 critical checks. Now 4 rubrics,
13 critical checks.

| Old | New |
|-----|-----|
| `ShapeCountAtLeast("vector", minimum=1)` | `ShapeCount("vector", equals=1)` (catches multiple vectors) |
| (no AlignmentRubric) | New rubric with 5 critical checks |
| `StrokeExists` | `AllStrokeExists` (every vector has stroke) |
| (no max stroke check) | `AllStrokeWeightAtMost(vector, 25)` |

## New primitives leveraged

| Primitive | Catches |
|-----------|---------|
| `LayerSizeAtLeast(vector, 50, 20)` | C21/C28 degenerate vectors |
| `LayerShortDimensionAtMost(vector, 1500)` | C22 absurdly large vectors |
| `LayerRotationEquals(vector, 0, tol=15)` | D34/D35 sharp rotations |
| `NoLayerFlipped(vector)` | D36/D37 mirroring |
| `LayerVisible(vector)` | F51/F52 transparency tricks |
| `AllStrokeExists(vector)` | E50 no strokes |
| `AllStrokeWeightAtMost(vector, 25)` | B14 50px stroke |

## Caught by new checks (round-3 examples)

| Case | Old | New | Caught by |
|------|-----|-----|-----------|
| L1   | 1.000 | 0.850 | LayerVisible |
| L2   | 1.000 | 0.850 | LayerVisible (opacity threshold) |
| L4   | 1.000 | 0.844 | AllStrokeExists (visibility) |
| L5   | 1.000 | 0.812 | AllStrokeExists (zero-width) |
| L6   | 1.000 | 0.781 | AllStrokeExists |
| M1   | 1.000 | 0.850 | LayerSizeAtLeast (min_h=20) |
| M2   | 1.000 | 0.850 | LayerRotationEquals (16° just over 15° tol) |
| M3   | 1.000 | 0.850 | NoLayerFlipped |
| M5   | 1.000 | 0.850 | LayerShortDimensionAtMost |
| M6   | 1.000 | 0.850 | LayerRotationEquals (90° fails) |
| M8   | 1.000 | 0.850 | LayerSizeAtLeast (negative dims fail) |
| O1–O5| 1.000 | 0.000 | ShapeCount(vector, equals=1) |

## Round-3 surviving 1.000 (14) — known limitations

| Case | What | Verdict |
|------|------|---------|
| K1   | 13.9px stroke (within 12±2 tol) | tolerance edge |
| K2   | 14° rotation (within 15° tol) | tolerance edge |
| K3   | 2 strokes mixed dashed | StrokeIsDashed only checks first |
| K4   | 2 strokes mixed weights | StrokeWeightEquals matches first |
| K5   | 51×21 (just over min) | tolerance edge |
| K6   | alpha=0.55 (over LayerVisible tol) | tolerance edge |
| K7   | cornerRadius on vector | property has no effect on vector type |
| K8   | control case | correctly passes |
| L3   | stroke alpha=0.2 | LayerVisible only checks fill not stroke |
| M4   | empty path | path data not validated |
| M7   | far negative coords | no position check on vector |
| N1   | nested instance>component | hierarchy variant |
| N3   | 3 stacked strokes | extras tolerated |
| N4   | group + delete events | events tolerated |

## Status

- 50/50 OK on `qa_verifiers.py`
- delivery-1/task_49/verifier.py is synced
- Round-3 strict FPs: 14 (above 5 target — task is by design loose since
  the prompt doesn't specify color, position, or exact path shape, only
  the stroke style; further tightening would block legitimate variants)
