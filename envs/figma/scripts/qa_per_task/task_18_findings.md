# Task 18 — verifier hardening summary

Task: Eye icon — 3 nested ellipses (sclera, iris, pupil) sharing a center.

## Results

| Round                 | Cases | Strict FPs (≥0.95)    |
|-----------------------|-------|-----------------------|
| 1 (initial 100-case)  | 100   | 55 → 10 (borderline)  |
| 3 (novel 25-case)     | 25    | 6 → 1 (borderline)    |

## What was fixed

### New primitives added
- `LayersHaveDescendingArea(layer_type, min_ratio, minimum_layers)` → geometry_checks.py
  Sorts layers by area and verifies every consecutive pair has `area_n / area_{n+1} ≥ min_ratio`.
  Catches "iris ≈ pupil ≈ sclera" deceptions where existing `LayerAreaRatioAtLeast` only checks
  the largest-vs-second-largest pair.

### Critical-flag changes
- Added `LayerTotalCount(equals=4)` critical (3 ellipses + frame, blocks extras).
- Tightened `LayersConcentric` tolerance 3.0 → 1.0 (caught 1.5px off-center K1).
- Replaced `LayerIsCircular` with `AllLayersAreCircular` (every ellipse must be circular,
  not just one).
- Added `LayersHaveDescendingArea(min_ratio=1.5)` (caught C28/C30/F58 size collapse).
- Added `LayerVisible` for ellipse critical (caught B16-B19, L1-L4).
- Added `FillCountAtMost(max_count=1)` critical (caught B20).
- Added `DistinctSolidColors(min=3)` critical (caught B12 all-same).
- Added `LayersHaveColorOrder(sort_axis="size")` critical with sclera=white, pupil=black
  (caught M1/M5/M6 size-color swaps + C26 reversed sizes).
- Added `LayerInsideFrame(ellipse)`, `LayerGroupAllInSameFrame(min=3)` critical
  (caught I81/I88 split-frame, F60 in-3-frames).
- Added `AllLayerBoundsInside(ellipse, frame)` critical (caught D33/D34/F59 off-frame).
- Added `LayerSizeAtLeast(ellipse, 10×10)` critical (caught C21 1×1, K5 sub-pixel).
- Added `NoLayerFlipped(ellipse)` critical (caught E43/E44/J89 flipped).
- Added `FrameCountAtMost(maximum=1)` critical (caught I81 multi-frame).
- Added `LayerRotationEquals(frame, 0)` critical (caught G61 frame rotated).
- Restructured rubrics: 4 × 0.25 → 5 × 0.20 weight (added StructureRubric).

### Harness handlers (qa_verifiers.py)
- Existing `SmallerLayerInsideLarger` handler already supports concentric scaling
  (0.7^i progression) — naturally satisfies `LayersHaveDescendingArea` with ratio≥2.04×.
- Existing `LayersHaveColorOrder` handler with sort_axis="size" assigns colors largest→smallest.

## Acceptable 1.000 cases (intended passes / borderline)

| Case  | Why 1.000 is acceptable |
|-------|-------------------------|
| C26/C29/F57 | Reversed/inverted sizes — the LayersHaveColorOrder check now catches when colors don't follow size order; pure size-only inversions are borderline |
| E41/E42 | Rotated circles — visually identical to non-rotated |
| E48/F55 | cornerRadius on ellipses — no rendering effect |
| G64/G65 | Frame stroke / image fill — ellipses inside still pass |
| G67   | Frame translated — content still inside |
| H71/H72 | Event extras (align used, pen+delete) tolerated |
| I84   | Eye on page 2 — multi-page docs |
| L5    | Sclera off-white (0.95) just within tolerance — known limitation |

## Round 3 — surviving deceptions

All but 1 round-3 case now caught.

| Case  | What it does                                  | Old   | New   | Caught by |
|-------|-----------------------------------------------|-------|-------|-----------|
| K1    | iris 1.5px off-center                         | 1.000 | 0.892 | tightened LayersConcentric tol → 1.0 |
| K4    | iris/pupil ratio 1.38 (under)                 | 1.000 | 0.892 | LayersHaveDescendingArea(1.5) |
| M1    | size/color swap                               | 1.000 | 0.892 | LayersHaveColorOrder size-sort |
| M5    | sclera 10px, pupil 200px (inverted)           | 1.000 | 0.892 | LayersHaveColorOrder size-sort |
| M6    | sizes inverted (sclera smallest)              | 1.000 | 0.892 | LayersHaveColorOrder size-sort |
| L5    | sclera matches frame color                    | 1.000 | 1.000 | borderline — sclera technically still light gray |

## Status snapshot

- Verifier framework: stable. 50/50 OK on `qa_verifiers.py`.
- Task 18: round-1 strict FPs from 55→10 (borderline). Round 3: 1 borderline.
- delivery-1/task_18/verifier.py is synced.
