# Task 19 — verifier hardening summary

Task: Padlock — rectangle body (cornerRadius=12, dark gray) + pen U-shackle
(14px stroke) above + small black keyhole circle.

## Results

| Round                 | Cases | Strict FPs (≥0.95)    |
|-----------------------|-------|-----------------------|
| 1 (initial 100-case)  | 100   | ~50 → 9 (borderline)  |
| 3 (novel 25-case)     | 25    | 2 → 0                 |

## What was fixed

### Critical-flag changes
- Replaced `ShapeCountAtLeast` with `ShapeCount(equals=N)` (catches A1-A3, A8-A10 extras).
- Added `LayerTotalCount(equals=4)` critical (catches A1-A10 extras).
- Added `LayerCenteredOnLayer(ellipse, rectangle)` critical (catches D36/D39/F57 keyhole off-center).
- Added `LayerNextTo(vector, rectangle, "above")` critical (catches D33/M3 shackle below body).
- Added `LayerSmallerThanLayer(ellipse, rectangle, max_frac=0.4)` critical
  (catches C30/K5 keyhole as big as body).
- Added `LayerRotationEquals` for rectangle/ellipse/vector critical (catches E43/J94/M3 rotated).
- Added `LayerVisible` for rectangle and ellipse critical (catches B17-B19 invisibility).
- Added `StrokeRendersVisible(vector, min_alpha=0.5)` critical (catches L4/L5 invisible stroke).
- Added `FillCountAtMost(max_count=1)` for both critical (catches B20 stacked).
- Added `LayerInsideFrame` + `LayerGroupAllInSameFrame` for all 3 types critical
  (catches I80/N1/N2 split-frame).
- Added `AllLayerBoundsInside(*, frame)` for rect+ellipse critical (catches D34/D35).
- Added `LayerSizeAtLeast` for all 3 types critical with realistic mins
  (rect 80×60, ellipse 8×8, vector 40×40 — catches C21/M2/M5/M6 degenerate/tiny).
- Added `NoLayerFlipped` for rect+ellipse critical (catches E48/E49/J89).
- Added `FrameCountAtMost(maximum=1)` critical (catches I80 multi-frame).
- Added `LayerRotationEquals(frame, 0)` critical (catches G61).
- Added `CornerRadiusFractionAtMost(rectangle, 0.5)` critical (catches E42/K4 pill body).
- Added `EventTypeCount(create_*, equals=1)` for exact event counts (catches H76).
- Tightened `LayerIsCircular` tolerance 3.0 → 2.0 for keyhole.
- Restructured rubrics: 4 × 0.25 → 5 × 0.20 (added StructureRubric).

### Removed checks
- `LayersOverlap(vector, rectangle)` removed — `LayerNextTo("above")` is more accurate
  (shackle and body don't actually need to overlap; just be adjacent).

### Harness handlers (qa_verifiers.py)
- No new handlers needed — all primitives already supported.

## Acceptable 1.000 cases (intended passes / borderline)

| Case  | Why 1.000 is acceptable |
|-------|-------------------------|
| F52   | Shackle stroke red — prompt only specifies body+keyhole color |
| F53   | Shackle dashed — prompt says "round caps" but doesn't forbid dashing |
| G64/G65 | Frame stroke / image fill — content still inside |
| G67   | Frame translated — content still inside |
| H71/H72/H75 | Event extras (align, deletes, multi session_end) tolerated |
| I85   | Padlock on page 2 — multi-page docs |

## Round 3 — surviving deceptions

All caught.

| Case  | What it does                       | Old   | New   | Caught by |
|-------|------------------------------------|-------|-------|-----------|
| M3    | shackle rotated 180° (∩-shape)     | 1.000 | 0.892 | LayerRotationEquals(vector, 0, tol=10) |
| M5    | body 50px wide                     | 1.000 | 0.892 | LayerSizeAtLeast(rectangle, 80×60) |

## Status snapshot

- Verifier framework: stable. 50/50 OK on `qa_verifiers.py`.
- Task 19: round-1 strict FPs from ~50→9 (borderline). Round 3: 0.
- delivery-1/task_19/verifier.py is synced.
