# Task 20 — verifier hardening summary

Task: Glow blob — dark navy frame + 2 overlapping blurred circles (distinct fills).

## Results

| Round                 | Cases | Strict FPs (≥0.95)    |
|-----------------------|-------|-----------------------|
| 1 (initial 100-case)  | 100   | ~50 → 10 (borderline) |
| 3 (novel 25-case)     | 25    | 3 → 1 (borderline)    |

## What was fixed

### New primitives added
- `LayersHaveDistinctCenters(layer_type, min_offset)` → geometry_checks.py
  Catches "2 ellipses at IDENTICAL bbox" deceptions where `LayersOverlap` passes trivially
  on a layer overlapping itself or a same-bbox sibling. Forces partial (not full) overlap.
- `AllLayerBlurExists(layer_type, min_radius)` → effect_checks.py
  Stricter than `LayerBlurExists` (≥1 layer) — catches "blur on one ellipse but not the other".

### Critical-flag changes
- Added `LayerTotalCount(equals=3)` critical (catches A1/A6/A9 extras).
- Replaced `LayerIsCircular` with `AllLayersAreCircular` critical (catches K5/K6 ovals).
- Added `LayerRotationEquals(ellipse, 0)` critical (catches E41/E46/M5).
- Added `LayersHaveDistinctCenters(min_offset=20)` critical (catches D35/M2/M6 identical).
- Added `LayerVisible` for ellipse + frame critical (catches B17-B19, L1-L4).
- Added `FillCountAtMost(max_count=1)` for both critical (catches B20).
- Replaced `LayerBlurExists` with `AllLayerBlurExists` critical (catches E44/L4/L5).
- Added `LayerInsideFrame`, `LayerGroupAllInSameFrame(min=2)` critical
  (catches I79/I81/N1/N2 split-frame).
- Added `AllLayerBoundsInside(ellipse, frame)` critical (catches D31/D32/M4 off-frame).
- Added `LayerSizeAtLeast` for ellipse (20×20) and frame (200×200) critical
  (catches C21/C26/C27/M1 degenerate).
- Added `NoLayerFlipped(ellipse)` critical (catches E46/J91 flipped).
- Added `FrameCountAtMost(maximum=1)` critical (catches A10/I81/N2 multi-frame).
- Added `LayerRotationEquals(frame, 0)` critical (catches G61).
- Added `LayersSameDimensions(ellipse)` critical (catches C24 size mismatch).
- Restructured rubrics: 5 × 0.20 + 1 × 0.10 → 6 rubrics total (added StructureRubric, EffectRubric reduced weight).

### Harness handlers (qa_verifiers.py)
- `LayersOverlap(same-type)` handler now offsets second by 30% of width (≥25px) for
  partial overlap — satisfies both `LayersOverlap` and `LayersHaveDistinctCenters`.
- New `AllLayerBlurExists` handler (parallels `LayerBlurExists`).
- `synth_layer` palette updated to 8 perceptually-distinct colors so
  `DistinctSolidColors(min=3)` passes for any 2+ ellipse design.
- `perfect_log` no longer wraps in an outer frame when "frame" is in shapes
  — avoids double-frame in tasks where ShapeCount("frame", N) is part of the spec.

## Acceptable 1.000 cases (intended passes / borderline)

| Case  | Why 1.000 is acceptable |
|-------|-------------------------|
| C28   | Frame 3000×3000 — prompt mentions "800×600" but doesn't enforce strictly |
| D37/D38 | Tiny / 90% overlap — prompt says "~30%" but hard to tighten without false negatives |
| E47   | Ellipses with stroke — prompt doesn't forbid stroke |
| E48   | Ellipses with cornerRadius — no rendering effect for ellipses |
| E50   | Blur radius 100 — within tol of 30 from 80 (acceptable) |
| G64   | Frame stroke — content still inside |
| H73/H77 | Event extras (align, multi session_end) tolerated |
| I84   | Glow on page 2 — multi-page docs acceptable |
| K1    | Frame purple-navy (off-color) — within color tolerance for "navy" |

## Round 3 — surviving deceptions

All but 1 caught.

| Case  | What it does                       | Old   | New   | Caught by |
|-------|------------------------------------|-------|-------|-----------|
| K2    | blur 49 (just under tol)           | 1.000 | 0.875 | tol now 30 from 80 (was 20 → 30 too loose) |
| L4    | both blurs visible=False           | 1.000 | 0.875 | AllLayerBlurExists (visible check) |
| L5    | both blur radius=0                 | 1.000 | 0.875 | AllLayerBlurExists (min_radius=1) |
| M1    | 1×1 ellipses                       | 1.000 | 0.875 | LayerSizeAtLeast(20, 20) |
| M2    | ellipses = full frame              | 1.000 | 0.875 | LayersHaveDistinctCenters (catches identical bbox) |
| M6    | identical bboxes                   | 1.000 | 0.875 | same |
| K1    | frame purple-navy                  | 1.000 | 1.000 | borderline — still within "navy" color tolerance |

## Status snapshot

- Verifier framework: stable. 50/50 OK on `qa_verifiers.py`.
- Task 20: round-1 strict FPs ~50→10 (borderline). Round 3: 1 borderline.
- delivery-1/task_20/verifier.py is synced.
