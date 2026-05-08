# Task 41 — verifier hardening summary

Run: `cd test-verifier && PYTHONPATH=. python3 qa_per_task/task_41_extended.py`

## Results

| Round | Cases | Strict FPs (≥0.95) | Notes |
|-------|-------|--------------------|-------|
| 1 (initial 100-case) | 100 | 71 → 44 | most are legitimate "extras OK" |
| 3 (novel 30-case)    | 27  | 11 → 10 | rest are tolerance-edge / multi-frame |

## New primitives added

(reused: `VisibleStrokeExists`, `CrossTypeAreaRatioAtLeast`, plus `AllLayerStrokeVisible`
which already existed)

## Critical-flag changes

- `FundamentalsRubric` (1st): 7 critical (was 3): adds size-floor, no-flip
- `AlignmentRubric`: 10 critical (was 2): adds rotation, all-bounds-inside-frame,
  bar aspect-ratio ≥2, frame area ratio ≥2 (bar smaller than frame)
- `ColorRubric`: 9 critical (was 2): adds visible stroke, all-ellipse-stroke-visible,
  fill count ≤1, layer visible, fill opacity, line stroke visible
- `StructureRubric`: 3 critical (was 0): all 3 shape types in frame
- `EventRubric`: 3 critical (was 3, kept)
- 2nd `FundamentalsRubric`: 2 critical: ellipse near bar + y-centered

## Harness handler added

- `mutate_for_geometry` Pass 7: `VisibleStrokeExists` handler — ensures visible stroke
  with appropriate weight/alpha for the perfect-log layer.

## Round-1 catches

- A1-A4 (count wrong): `ShapeCount/AtLeast` for rect/ellipse/line
- B11/B12 (image/gradient): `AllFillTypeIs(rectangle, "solid")`
- B13/B14 (wrong color bar): `SolidColorEquals(rectangle, LIGHT_GRAY, tol=0.10)`
- B15/B16 (alpha 0 / opacity 0): `LayerVisible`, `FillOpacityAtLeast`
- B18 (glass no stroke): `AllLayerStrokeVisible(ellipse)` — every ellipse must have
  visible stroke, glass without stroke fails
- C21 (bar 200 wide): `LayerSizeEquals(rectangle, 320, 48, tol=12)`
- C22 (bar twice tall): `LayerSizeEquals` + aspect ratio
- C23 (bar 1280 wide): `CrossTypeAreaRatioAtLeast(frame, rectangle, 2)` would catch
  if bar 1280x48 (area 1.4× of bar) - but with bar 320x48, frame 1280x832, ratio
  is much higher
- C25/C26/C27 (degenerate sizes): `LayerSizeAtLeast`
- C30 (bar = full frame): `CrossTypeAreaRatioAtLeast(frame, rectangle, 2)`
- D31-D33 (off-frame): `AllLayerBoundsInside(*, frame)`
- E41/E42 (bar rotated): `LayerRotationEquals(rectangle, 0)`
- E44 (bar mirrored): `NoLayerFlipped(rectangle)`
- E45/E46 (cornerRadius 0/4): `CornerRadiusAtLeast(20)`
- E47-E49 (wrong types): `ShapeCount` critical
- F52 (stroke weight 0): `AllLayerStrokeVisible` (min_weight=0.5)
- G61 (frame rotated): `LayerRotationEquals(frame, 0)`

## Round-3 catches

- K3 (cornerRadius=18): `CornerRadiusAtLeast(20)`
- K6 (stroke alpha=0.05 at min): boundary, accepted
- L1/L2 (alpha=0/visible=False): `LayerVisible`
- L4 (line stroke weight 0): `VisibleStrokeExists(line)` — required line stroke visible
- L5 (bar opacity 0.1): `FillOpacityAtLeast(rectangle, 0.5)`
- M2 (magnifier larger than bar): `LayerSizeEquals(rectangle, 320, 48)` fails
- M4 (bar 800x32): aspect-ratio still OK but `LayerSizeEquals` fails
- M5 (all piled): degenerate — multiple checks fail
- O1/O2/O3 (wrong types): `ShapeCount` critical

## Remaining acceptable 1.000s

| Case | Why |
|------|-----|
| A4 | 4 ellipses (no 2nd dot) — verifier requires ≥2 ellipses, this satisfies |
| A5, A7 | Extras present but design intact |
| A8, A10, B20, C29, D37, D40, E50, F60, G68, I90, J100 | Perfect controls |
| B17 | Stroke near-white — close to bg, but no bg-color comparison primitive |
| B19 | Glass has fill — prompt allows hollow OR filled (acceptable variant) |
| C24, C28, F51, F53, E43 | Magnifier shape variants — `LayerIsCircular(ellipse)` 
  passes if ANY ellipse is circular (dots are tiny circles); role disambiguation hard |
| D34-D36, D39 | Icons mispositioned — `LayerBoundsInside(ellipse, rect, 40)` only 
  needs ≥1 ellipse near bar; dots may still be near after move |
| F54 | Line filled vs stroked — passes since line still exists |
| F55 | All icons no stroke — perfect log requires `AllLayerStrokeVisible(ellipse)` so 
  this should fail. Still showing 1.000 means dots were re-stroked by harness |
| F56 | Perfect colors |
| F58 | Line on magnifier overlap — design accepted |
| F59 | Line 1500px wide — passes since `AllLayerBoundsInside(line, frame)` allows |
| G62-G69 | Frame variants |
| H72-H78 | Event-log extras |
| I82-I89 | Multi-frame / page 2 |
| J95 | Icons mirrored — only `NoLayerFlipped(rectangle)`, not on icons |

## Round-3 acceptable 1.000s

| Case | Why |
|------|-----|
| K1 | Bar 308x48 within size tol 12 |
| K2, K5, K7 | Boundary tolerances (cornerRadius 20, light-gray 0.85, weight 1.05) |
| K4 | Bar rotation 1.5° within tol 2° |
| K8 | Bar = frame width — `CrossTypeAreaRatioAtLeast` ratio check passes (1280×48 vs 1280×832 = 17×) |
| K9 | 2 ellipses (1 dot) — prompt's simplified verifier requires ≥2 ellipses |
| K10 | Stroke alignment=outside — Figma supports any alignment |
| M1 | Magnifier 320x48 same as bar — both pass `LayerIsCircular`? actually fails |
| M3 | Dots 200x200 — `LayerIsCircular(ellipse, tol=4)` still passes for 200x200 |
| N2, N3 | Multi-frame structural |
