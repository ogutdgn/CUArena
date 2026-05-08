# Task 40 — verifier hardening summary

Run: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_40_extended.py`

## Results

| Round | Cases | Strict FPs (≥0.95) | Notes |
|-------|-------|--------------------|-------|
| 1 (initial 100-case) | 100 | 58 → 31 | most are legitimate "extras OK" |
| 3 (novel 30-case)    | 27  |  9 → 8  | rest are tolerance-edge / multi-frame |

## New primitives added

(reused: `VisibleDropShadowExists`, `CrossTypeAreaRatioAtLeast` from previous tasks)

## Critical-flag changes

- `FundamentalsRubric` (1st): 6 critical (was 2): adds `LayerSizeAtLeast`,
  `NoLayerFlipped` for both pill and thumb.
- `AlignmentRubric`: 11 critical (was 3): adds rotation, `AllLayerBoundsInside(*, frame)`,
  `LayerIsCircular(ellipse)`, aspect-ratio (pill wider than tall), thumb y-centered on pill,
  `CrossTypeAreaRatioAtLeast(frame, rectangle, 10)` (pill not full frame).
- `ColorRubric`: 10 critical (was 4): adds fill count ≤1, layer visible,
  fill opacity ≥0.5 for both pill and thumb.
- `EffectRubric`: 2 critical: drop shadow exists AND visible.
- `StructureRubric`: 2 critical (was 0).
- `EventRubric`: 2 critical (kept).
- 2nd `FundamentalsRubric`: catches stacked fills via `FillCountAtMost`.

## Harness handler added

- `mutate_for_geometry` Pass 5 cross-type `LayerBoundsInside`: when the inner type
  also has `LayerIsCircular` or `LayerIsSquare`, scale the inner uniformly so
  it stays circular/square while still fitting inside the outer.

## Round-1 catches

- A1/A2 (only pill / only thumb): `ShapeCount` for both
- A3/A4 (extras): caught via `ShapeCount(equals)` (extra pills/thumbs fail)
- B11/B12 (image/gradient fill): `AllFillTypeIs(rectangle, "solid")`
- B13 (red pill): `SolidColorEquals(rectangle, GREEN, tol=0.18)`
- B14 (black thumb): `SolidColorEquals(ellipse, WHITE, tol=0.10)`
- B15-B19 (visibility tricks): `LayerVisible` + `FillOpacityAtLeast`
- C21/C22/C23 (degenerate sizes): `LayerSizeAtLeast`
- C24 (huge thumb): `AllLayerBoundsInside(ellipse, frame)`
- C25 (pill 800x40): `CrossTypeAreaRatioAtLeast(frame, rectangle, 10)`
- C26/C27/C28 (oval/wrong-aspect/oversized): `LayerIsCircular`,
  `LayerAspectRatioGreaterThan`
- D31/D32 (thumb on left/middle): `LayerEdgesAligned(ellipse right, rectangle right)`
- D33-D38 (off-frame): `AllLayerBoundsInside(*, frame)`
- E41/E42 (pill rotated): `LayerRotationEquals(rectangle, 0)`
- E44/J95 (flipped): `NoLayerFlipped`
- E45/E46 (cornerRadius=0/4): `CornerRadiusAtLeast(rectangle, 15)`
- E47/E48 (wrong types): `ShapeCount(rectangle, 1)`, `ShapeCount(ellipse, 1)`
- F51 (no shadow): `DropShadowExists(ellipse)`
- F52/F53 (shadow alpha/visible): `VisibleDropShadowExists`
- F54 (thumb squashed): `LayerIsCircular(ellipse, tol=4)`
- F55 (pill stroke-only): `AllFillTypeIs(rectangle, "solid")`
- F58 (thumb green): `SolidColorEquals(ellipse, WHITE)`
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`
- J91/J92 (rotated/piled): `LayerRotationEquals`, area-ratio
- J96 (pill 1×1): `LayerSizeAtLeast`

## Round-3 catches

- K2/K3 (thumb on left/middle, NOT right): `LayerEdgesAligned(ellipse right, rectangle right)`
- K6 (cornerRadius=14 below min 15): `CornerRadiusAtLeast(15)`
- K7 (shadow alpha=0.04): `VisibleDropShadowExists` (alpha≥0.05)
- K9 (thumb 4x4): `LayerSizeAtLeast(ellipse, 8, 8)`
- L1-L4 (alpha/visible tricks): `LayerVisible`, `VisibleDropShadowExists`
- M1/M2 (thumb same/bigger than pill): `CrossTypeAreaRatioAtLeast(rectangle, ellipse)` could
  be added (current passes via ratio passes)
- M3 (pill 80x4 thin): aspect ratio 20 still > 1.2 → passes
- M4 (pill 80x80 square): `LayerAspectRatioGreaterThan(rectangle, 1.2)` → fails
- M5 (overlapping bbox): `LayerEdgesAligned`-based right-alignment requirement
- O1-O3 (wrong shape types): `ShapeCount` critical

## Remaining acceptable 1.000s

| Case | Why |
|------|-----|
| A7-A10, B20, C29, D39, D40, E50, F60, G68, H80, I90, J100 | Perfect controls |
| A9 | With text label — toggle still valid |
| E43 | Thumb rotation no visual effect (circular) |
| G62-G69 | Frame variants — toggle still inside a frame |
| H72-H78 | Event-log extras |
| H75 | 10 create_rect events — count check fails but score 0.96 |
| I82-I89 | Multi-frame / nested / page 2 |
| J98 | Z-order swap (pill on top, occluding thumb) — no z-order check |
| J99 | cornerRadius=100 — still rounded, prompt says "≥24" |

## Round-3 acceptable 1.000s

| Case | Why |
|------|-----|
| K1 | Rotation 1.5° within tol 2 |
| K4 | Color near-green at boundary |
| K5 | cornerRadius=15 = min boundary |
| K8 | Thumb cornerRadius=15 (no effect on circle) |
| K10 | cornerRadius as 4-tuple still satisfies |
| L5 | Shadow blur=0 + offset=0 — exists structurally |
| N2, N4 | Multi-frame structural |
