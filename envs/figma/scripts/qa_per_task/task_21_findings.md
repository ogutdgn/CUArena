# Task 21 — verifier hardening summary

Task: Button stack — 3 same-size rectangles stacked vertically (16px gap),
distinct colors, aligned on x.

## Results

| Round                 | Cases | Strict FPs (≥0.95)    |
|-----------------------|-------|-----------------------|
| 1 (initial 100-case)  | 100   | ~50 → 10 (borderline) |
| 3 (novel 26-case)     | 26    | 4 → 0                 |

## What was fixed

### Critical-flag changes
- Added `LayerTotalCount(equals=4)` critical (catches A1/A6/A8 extras).
- Added `LayerRotationEquals(rectangle, 0)` critical (catches E41/E42/E44/F60).
- Added `LayerAspectRatioGreaterThan(rectangle, 1.5, "horizontal")` critical
  (catches C25/C26 buttons that aren't horizontal/wide).
- Replaced `DistinctSolidColors` with `DistinctTypedSolidColors(rectangle, min=3)`
  (catches F52 — 2 same + 1 different where frame color filled the gap).
- Added `LayerVisible` critical (catches B16-B19 invisible).
- Added `FillCountAtMost(max_count=1)` critical (catches B20).
- Added `LayerInsideFrame`, `LayerGroupAllInSameFrame(min=3)` critical
  (catches I80/I82/N1/N2).
- Added `AllLayerBoundsInside(rectangle, frame)` critical (catches D39/D40 off-frame).
- Added `LayerSizeAtLeast(rectangle, 30×20)` critical (catches C21/C30/M1 degenerate).
- Added `NoLayerFlipped(rectangle)` critical (catches E43/E44/J89).
- Added `FrameCountAtMost(maximum=1)` critical (catches I80 multi-frame).
- Added `LayerRotationEquals(frame, 0)` critical (catches G61).
- Added `CornerRadiusFractionAtMost(rectangle, 0.5)` critical (catches E46/K6 pill-shaped).
- Restructured rubrics: 4 × 0.25 → 5 × 0.20 (added StructureRubric).

### Harness handlers (qa_verifiers.py)
- No new handlers — all primitives already supported (LayerSizeAtLeast, LayerAspectRatioGreaterThan, etc.).

## Acceptable 1.000 cases (intended passes / borderline)

| Case  | Why 1.000 is acceptable |
|-------|-------------------------|
| E45   | cornerRadius=10 (mild rounding) — visually still rectangles |
| E46   | cornerRadius=30 (pill on 60-tall) — at frac threshold, may pass |
| E47   | Rectangles with stroke — prompt doesn't forbid |
| E48   | Drop shadow — prompt doesn't forbid |
| G64/G65 | Frame stroke / image fill — content still inside |
| H71/H72/H76 | Event extras tolerated |
| I85   | Stack on page 2 — multi-page docs |
| J96   | Reversed y-order — same design from top vs bottom |

## Round 3 — surviving deceptions

All 4 round-3 deceptions caught after tolerance tightening.

| Case  | What it does                                        | Old   | New   | Caught by |
|-------|-----------------------------------------------------|-------|-------|-----------|
| K2    | rects rotated 1.5°                                  | 1.000 | 0.880 | LayerRotationEquals tol 2.0 → 1.0 |
| K3    | 203×63 vs 200×60                                    | 1.000 | 0.880 | LayersSameDimensions tol 3.0 → 2.0 |
| K5    | rects drift 2px x                                   | 1.000 | 0.880 | LayersAligned tol 5.0 → 2.0 |
| K6    | cornerRadius=29 (frac 0.483)                        | 1.000 | 0.880 | CornerRadiusFractionAtMost 0.5 → 0.45 |

## Status snapshot

- Verifier framework: stable. 50/50 OK on `qa_verifiers.py`.
- Task 21: round-1 strict FPs ~50→11 (borderline). Round 3: 4 tolerance-edge.
- delivery-1/task_21/verifier.py is synced.
