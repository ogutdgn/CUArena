# Task 36 — verifier hardening summary

Run with: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_36_extended.py`
Round 3: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_36_round3.py`

## Results

| Round | Cases | Strict FPs (≥0.95) — true FPs |
|-------|-------|-------------------------------|
| 1 (initial 100-case)   | 100 | ~50+ (very weak baseline) |
| 2 (after fixes)         | 100 | 0 true FPs (45 cases at 1.0 — extras/frame/hierarchy variants) |
| 3 (novel 30-case)       | 29  | 0 true FPs (5 within-tolerance / structure cases) |

## Prompt rebase

The simplified delivery prompt for task 36 only requires:
- 2 rectangles
- Smaller inner inside outer
- Both share same center
- Each can have its own fill color

The legacy verifier checked tilt + drop shadow as critical; these have been
demoted to soft (non-critical) checks while the prompt-explicit constraints
have been hardened.

## Verifier additions

Total checks: 6 → 16; critical checks: 3 → 13.

### Alignment rubric (was 2 → now 8)
- `LayersConcentric(rectangle, tol=15)` (★ critical) — "share the same center".
- `LayerAreaRatioAtLeast(rectangle, min_ratio=1.05)` (★ critical) — inner truly smaller.
- `LayerSmallerThanLayer(rectangle, rectangle, max_frac=0.95)` (★ critical) — inner < 95% of outer.
- `LayerSizeAtLeast(rectangle, min=20×20)` (★ critical) — non-degenerate.
- `NoLayerFlipped(rectangle)` (★ critical) — no mirrored rectangles.
- `CornerRadiusFractionAtMost(rectangle, max_frac=0.4)` (★ critical) — rectangles not "circles".
- `LayerRotationEquals(rectangle, 5°, tol=3)` (soft) — legacy tilt remains as bonus.

### Color rubric (was 2 → now 5)
- `AllFillTypeIs(rectangle, solid)` (★ critical) — both rectangles have a solid fill.
- `FillCountAtMost(rectangle, 1)` (★ critical) — no stacked fills.
- `FillOpacityAtLeast(rectangle, 0.5)` (★ critical) — visible fills.
- `LayerVisible(rectangle)` (★ critical) — catches alpha=0/opacity=0/visible=False.
- `SolidColorEquals(rectangle, WHITE)` (soft) — legacy white-outer remains as bonus.

## Round 3 results

| Case  | What it does                            | Score | Caught by |
|-------|-----------------------------------------|-------|-----------|
| K1    | inner = outer dimensions                | 0.875 | LayerAreaRatioAtLeast, LayerSmallerThanLayer |
| K2    | inner 5px smaller (within tol)          | 0.875 | LayerAreaRatioAtLeast |
| K3    | inner 20px off-center                   | 0.875 | LayersConcentric |
| K5    | inner cornerRadius over max             | 0.875 | CornerRadiusFractionAtMost |
| K7    | inner mirrored                          | 0.875 | NoLayerFlipped |
| K8    | outer flipped V                         | 0.875 | NoLayerFlipped |
| K9    | both opacity=0                          | 0.825 | LayerVisible, FillOpacityAtLeast |
| K10   | both alpha=0                            | 0.835 | LayerVisible |
| L1-L5 | visibility tricks                       | 0.835-0.875 | LayerVisible / FillOpacityAtLeast |
| M1, M2| degenerate sizes                        | 0.815-0.835 | LayerSizeAtLeast |
| M3    | outer = full canvas                     | 1.000 | accepted (size not constrained) |
| M4    | only outer rect                         | 0.562 | ShapeCount(=2) |
| M5    | outer cornerRadius 200 (circle)         | 0.875 | CornerRadiusFractionAtMost |
| M6    | inner above outer                       | 0.875 | SmallerLayerInsideLarger |
| M7    | both rects same size, offset            | 0.875 | LayerAreaRatioAtLeast |
| O1    | outer ellipse                           | 0.473 | ShapeCount(rectangle, =2) |
| O2    | outer polygon                           | 0.473 | ShapeCount |
| O3    | both stars                              | 0.323 | ShapeCount |

## Acceptable 1.000 cases

The prompt is permissive — only 4 hard requirements. Most 1.000 cases are valid:

- D36, J100: controls.
- A5: 2 rects + extra ellipse — design intact.
- B11, B12: rectangle colors not specified by prompt.
- B16, B17: white/near-white (within tol).
- D35, J98: shifted globally — geometry preserved.
- E41-E44, J99: rotation variants — soft constraint.
- E45, E46: cornerRadius (within max 0.4).
- F52, F60: drop shadow variants — soft constraint.
- F55, F56: z-order / same color — prompt allows.
- G61-G70: frame variants — prompt doesn't require frame.
- H75-H80: event sugar.
- I81-I90: hierarchy variants.
- M3: outer = full canvas — size not constrained.
- N1-N4: structural variants — no structure rubric (prompt doesn't require it).

## Known limitations

- K4 (cornerRadius 0.385 — just under 0.4 cap): within tolerance.
- N1-N4 (frame structure variants): prompt doesn't require frame, so no structure rubric.
- F58 (both rects same size, both centered): catches via `LayerAreaRatioAtLeast` only
  if size ratio < 1.05; if sizes are exactly equal it fails. Verified working.
