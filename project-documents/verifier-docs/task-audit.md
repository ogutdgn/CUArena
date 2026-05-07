# Per-Task Verifier Audit

A devil's-advocate review of all 50 tasks: what could pass the current verifier
but shouldn't, what should pass but won't, and which checks from the §16
knowledge tree are missing. Use this to harden each task before next eval run.

---

## Legend

- **Current** — abbreviated rubric content (F=Fundamentals, A=Alignment,
  C=Color, S=Structure, E=Event, X=Effect, P=Property, T=Text, Pg=Page).
- **End-state hole** — the canvas could end up wrong but the verifier passes.
- **Event hole** — the agent could have done something the prompt forbids/
  required without the verifier noticing.
- **Add (now)** — checks that exist in §16 today and should be added.
- **Add (gap)** — checks that don't exist yet (the `[GAP]` items in §16) but
  the prompt requires them; build the primitive first.

Throughout, citations like `LayersAligned` reference §8 catalog entries.

---

## Cross-cutting findings (apply to MANY tasks)

Repeated patterns I found while auditing:

1. **Color-vs-FillType blindness.** Many tasks only check `FillTypeIs(..., kind="solid")` but
   not the actual color. An agent could fill everything black/grey and pass.
   Add `SolidColorEquals` or `AllSolidColorEquals` whenever the prompt names a
   color. Affects tasks: 1, 10, 11, 12, 13, 14, 16, 17, 18, 22, 24, 25, 27, 30,
   31, 32, 33, 36, 37, 38, 40, 41, 43, 44, 45, 46, 47, 50.

2. **Stroke prompts go unverified.** Tasks 14 (4px black on every ring),
   15 (1px gray cloud), 16 (2px dark gray bubble), 19 (14px shackle stroke),
   38 (gray battery body), 39 (6px navy arc), 41 (2px magnifier circle stroke),
   42 (2px white badge stroke), 48 (white hexagon stroke), 49 (custom dash),
   50 (4px white border) all describe strokes — none of those tasks check
   stroke weight/color. Add `StrokeExists` + `StrokeWeightEquals` +
   `StrokeColorEquals`.

3. **Drop-shadow prompts go unverified.** Tasks 12, 24, 27 (×2), 36, 37, 40, 44, 50
   prompt for drop shadows but only some have `DropShadowExists`. Even where
   present, blur/offset/spread aren't checked — those are `[GAP]` checks
   (`DropShadowOffsetEquals`, `DropShadowBlurEquals`, `DropShadowSpreadEquals`).

4. **Rotation prompts go unverified.** Tasks 27 (3 rotated squares) and 36
   (~5°), 37 (~3°) describe rotated layers — only task 27 enforces rotation
   (via `LayersEvenlyRotated`). Tasks 36/37 should add `LayerRotationEquals`.

5. **Frame containment regressions.** Tasks 20, 23, 24, 29, 30, 31, 32, 34, 48
   set up a frame but don't always enforce that subsequent shapes are inside
   it. An agent could draw outside the frame and pass. Add `LayerInsideFrame`.

6. **Equality vs at-least mismatch on events.** Tasks frequently use
   `EventTypeCount(equals=N)` — but if the agent created N+M shapes then
   deleted M, end-state sees N while events see N+M. Either accept events as
   `EventTypeCountAtLeast` or add an explicit `LayerTotalCount` to enforce
   nothing extra exists. Affects most tasks.

7. **No undo-loop detection.** Several prompts allow duplicate-and-modify
   workflows (e.g., task 14, 31, 32). An agent could loop create→undo→create
   and run up the turn count without progress. No check flags this. Optionally
   add `UndoUsed` as a *negative* signal (low weight) on tasks where undo is
   expected to be rare.

8. **"Centered" semantics drift.** "Centered" in prompts can mean (a) center of
   parent frame, (b) centroid of a sibling, or (c) just "near middle." Tasks
   are inconsistent. Use `LayerCenteredInFrame` for (a),
   `LayerCenteredOnLayer` for (b).

---

## Task-by-task audit

### Task 01 — house_task_comprehensive  [in_scope]
**Prompt**: House inside MacBook frame: 2 rectangles + 2 ellipse windows + 1 polygon roof, distinct colors, windows aligned/symmetric, roof bottom touches body top, all in one frame.
**Current**: F (3 ShapeCounts), A (7 alignment checks incl. FrameSizeEquals), C (3 FillTypeIs + DistinctSolidColors≥4), S (3 LayerInsideFrame + ChildCountAtLeast≥5), E (3 ToolUsed + 3 EventTypeCount).
**End-state hole**: Door rectangle isn't distinguished from body rectangle — both must exist but the door could be 5×5px in a corner. No size constraint on the door.
**Event hole**: `set_fill_color` events not required — agent could rely on default fills if defaults happen to differ, masking the "apply distinct colors" requirement.
**Add (now)**: `LayerSizeEquals` for the body rectangle (~min size); `EventTypeCountAtLeast("set_fill_color", minimum=4)` so the agent demonstrably applied colors.

### Task 02 — sunset_gradient  [planned]
**Prompt**: Single rectangle filled with 5-stop linear gradient from purple→pale-yellow.
**Current**: F (rectangle=5), A (sizes/aligned/stacked/inside frame), C (FillTypeIs solid + DistinctSolidColors≥5 + LayersHaveColorOrder), E.
**End-state hole**: Verifier treats this as 5 separate stripes, not a gradient. The actual prompt is *one* rectangle with a gradient fill — the verifier accepts the wrong artifact. This is a Tier-2 gap: needs `[GAP] GradientFillExists` + `GradientStopColorEquals` once gradient fills ship.
**Event hole**: Should require gradient toolchain events once they exist.
**Add (gap)**: `GradientFillExists`, `GradientStopColorEquals`. Until then, the current 5-rectangle workaround is fine but should be flagged as an interim simulation.

### Task 03 — glowing_orb  [planned]
**Prompt**: Single 300px circle on dark navy frame with radial gradient + offset center.
**Current**: F (ellipse=9), A (RadialDistributionExcludeCentral n=8), C (DistinctSolidColors≥8 + CentermostLayerHasColor), E.
**End-state hole**: Same as task 02 — verifier expects 9 ellipses to simulate a radial gradient. Wrong artifact.
**Add (gap)**: `GradientFillExists(kind="radial")`, gradient center offset check.

### Task 04 — color_wheel  [planned]
**Prompt**: Single circle with angular gradient + 6 rainbow stops.
**Current**: F (rectangle=6), A (RadialDistribution n=6 + LayerIsSquare), C (DistinctSolidColors≥6), E.
**End-state hole**: Verifier checks 6 squares in a ring, not 1 circle with angular gradient.
**Add (gap)**: `GradientFillExists(kind="angular")` + per-stop color matching.

### Task 05 — red_heart_union  [out_of_scope]
**Prompt**: Boolean union of 2 circles + triangle to form heart.
**Current**: F (rectangle=2), A (cross-aligned + AspectMix 1H/1V), C (AllSolidColorEquals red), E.
**End-state hole**: Verifier accepts a "+" of 2 perpendicular rectangles — not a heart. This is a documented out_of_scope simulation.
**Event hole**: No `boolean_union` event exists.
**Add (gap)**: Wait until boolean ops ship.

### Task 06 — gold_star_exclude  [out_of_scope]
**Prompt**: Boolean exclude of 2 rotated pentagons → 10-point star, gold fill.
**Current**: F (line=8), A (LayersConcentric + LayersEvenlyRotated step 45°), E.
**End-state hole**: Verifier accepts 8 lines through a point — not a star shape. No fill check at all even though prompt says gold.
**Add (now)**: `AllSolidColorEquals(layer_type="line", expected_rgb=gold)` — but lines have stroke, not fill. So `StrokeColorEquals(layer_type="line", expected_rgb=gold)`.
**Add (gap)**: Boolean ops.

### Task 07 — mountain_range  [in_scope]
**Prompt**: Two pen-tool mountain paths, dark gray + lighter gray (overlapping).
**Current**: F (vector≥2), C (FillTypeIs solid + DistinctSolidColors≥2), E (pen tool + create_vector≥2).
**End-state hole**: No spatial check that the two vectors actually overlap (the prompt says one in front of the other). Two paths in distant corners would pass.
**Event hole**: No check that paths are actually closed (open paths can't have solid fills meaningfully).
**Add (now)**: `LayersOverlap(type_a="vector", type_b="vector")`.
**Add (gap)**: `[GAP] VectorIsClosed` — needs the new check.

### Task 08 — water_waves  [in_scope]
**Prompt**: Two pen-tool S-curves with bezier handles, 4px stroke rounded caps, two blue shades.
**Current**: F (vector≥2), C (DistinctStrokeColors≥2), E (pen + create_vector≥2).
**End-state hole**: No stroke weight check (prompt says 4px). No round-cap check. No "two blue shades" check (DistinctStrokeColors only proves they differ — could be red+green).
**Add (now)**: `StrokeWeightEquals(layer_type="vector", weight=4.0)`. Soft color check via `SolidColorEquals` won't apply to strokes — use a tolerance-loose variant of `StrokeColorEquals` for "blue" if hue range checks existed.
**Add (gap)**: Stroke cap is not in the schema (`stroke.cap` would be a new field). And/or a `StrokeCapIs("round")` check.

### Task 09 — brand_palette  [out_of_scope]
**Prompt**: 4 squares saved as color styles, 2nd row of 4 squares applies styles.
**Current**: F (rectangle=12), A (sameDims + grid 3×4), C (DistinctSolidColors≥12), E.
**End-state hole**: Verifier checks 12 distinct colors but the *prompt* requires only 4 distinct (4 styles applied to 8 rectangles). 12 distinct colors WOULD PASS the verifier but FAIL the prompt.
**Event hole**: No `create_style` / `apply_style` events (color-styles are out_of_scope).
**Add (now)**: Reduce to `DistinctSolidColors(minimum=4)` and add `SameColorAcrossTypes` patterns or pair-wise color equality between top and bottom rows once the right primitive exists.
**Add (gap)**: Color-style events (out_of_scope).

### Task 10 — apple_avatar  [out_of_scope]
**Prompt**: Photo masked by circle = circular avatar.
**Current**: F (rectangle=4), A (concentric + boundsInside), C (FillTypeIs solid), E.
**End-state hole**: Verifier accepts 4 concentric squares — wrong artifact entirely. Photo + mask features are out_of_scope.
**Add (gap)**: `ImageFillExists` is documented but not used here; once masks ship, need a `LayerIsMasked` primitive.

### Task 11 — pressed_button  [out_of_scope]
**Prompt**: Pill button with inner shadow looking pressed.
**Current**: F (polygon=3), A (concentric + boundsInside), C, E.
**End-state hole**: Verifier accepts 3 nested triangles. The actual artifact (a pill rectangle with inner shadow) is unrelated.
**Add (gap)**: `InnerShadowExists` (not in catalog; planned feature). Also `CornerRadiusAtLeast`.

### Task 12 — shadowed_cards  [out_of_scope]
**Prompt**: 3 white rounded cards in a row, sharing one drop-shadow effect style.
**Current**: F (rectangle=4 — should be 3), A (sameDims + center_y aligned), C (FillTypeIs solid), E.
**End-state hole**: 4≠3 (count is wrong). No `DropShadowExists`, no white-fill enforcement, no rounded-corner check, no shared-style check.
**Add (now)**: `ShapeCount("rectangle", equals=3)` (fix), `AllSolidColorEquals(rectangle, white)`, `CornerRadiusAtLeast(rectangle, 8)`, `DropShadowExists("rectangle")`, `LayersStacked(rectangle, axis="x")`.
**Add (gap)**: `DropShadowOffsetEquals` (Y=8), `DropShadowBlurEquals` (24).

### Task 13 — night_sky  [out_of_scope]
**Prompt**: Dark navy frame + crescent moon (boolean) + 6 white star circles.
**Current**: F (line=4), A (rotations 0°/90° each ×2), E.
**End-state hole**: Verifier checks for a "#" hashtag (4 lines crossing) — wrong artifact entirely.
**Add (gap)**: Boolean ops.

### Task 14 — concentric_target  [in_scope]
**Prompt**: 4 concentric circles 240/180/120/60px, alternating red/white, **4px black stroke each**.
**Current**: F (ellipse=4), A (concentric + boundsInside + circular), C (FillTypeIs solid), E.
**End-state hole**: ❌ **No stroke check at all** despite explicit prompt. ❌ No size check (verifier passes if all 4 are 60px). ❌ No "alternating red/white" color check.
**Add (now)**: `StrokeExists("ellipse")`, `StrokeWeightEquals("ellipse", weight=4)`, `StrokeColorEquals("ellipse", expected_rgb=black)`, `LayersHaveColorOrder("ellipse", expected_rgbs=[red, white, red, white], sort_axis="size")` (size sort not supported — use a series of `SolidColorEquals` per-size).
**Note**: `LayersHaveColorOrder` sorts by axis position, not by size. Concentric layers share centers, so size-sort is needed — that's a `[GAP] LayersHaveColorOrderBySize`.

### Task 15 — cloud_union  [out_of_scope]
**Prompt**: Boolean union of 4 white circles → cloud, 1px light gray stroke.
**Current**: F (ellipse=4), A (center_y aligned + overlap), C (AllSolidColorEquals white), E.
**End-state hole**: 4 separate ellipses pass, but a real union would be 1 vector. No stroke check (1px gray prompt).
**Add (now)**: `StrokeExists`, `StrokeWeightEquals(ellipse, weight=1)`, `StrokeColorEquals(ellipse, light_gray)`.
**Add (gap)**: Boolean ops.

### Task 16 — speech_bubble  [out_of_scope]
**Prompt**: Boolean union of rounded rect + triangle, light gray fill, 2px dark gray stroke.
**Current**: F (rectangle=1, polygon=1), A (overlap + cornerRadius≥8), C (FillTypeIs + SameColorAcrossTypes), E.
**End-state hole**: Two separate shapes pass — not a union. No light-gray fill enforcement, no stroke check.
**Add (now)**: `AllSolidColorEquals` (light gray), `StrokeWeightEquals(weight=2)`, `StrokeColorEquals` (dark gray).
**Add (gap)**: Boolean ops.

### Task 17 — play_button  [out_of_scope]
**Prompt**: Boolean subtract: triangle from purple circle → play icon.
**Current**: F (polygon=2, rectangle=2), A (center_x aligned + rotations 0/180), C, E.
**End-state hole**: The verifier expects `=` symbol of 2 triangles point-to-point + 2 rectangle caps — not a play button. Wrong artifact entirely.
**Add (gap)**: Boolean ops.

### Task 18 — donut  [out_of_scope]
**Prompt**: Boolean subtract → donut, plus 5 sprinkle ellipses.
**Current**: F (ellipse=3), A (concentric + boundsInside + circular), C, E.
**End-state hole**: 3 nested concentric circles passes — but the prompt is donut+sprinkles. Sprinkles not checked. Pink fill not checked.
**Add (now)**: For the in_scope simulation, add `SolidColorEquals(expected_rgb=pink)` for the outer ellipse.
**Add (gap)**: Boolean ops.

### Task 19 — padlock  [in_scope]
**Prompt**: Rounded rectangle body (radius 12, dark gray), pen-tool U-shackle (14px stroke round caps), keyhole circle.
**Current**: F (rect≥1, vector≥1, ellipse≥1), A (boundsInside ellipse-in-rect + overlap vector-rect + circular ellipse), C (FillTypeIs solid rect), E (rect+pen+ellipse tools).
**End-state hole**: Corner radius=12 not checked. Stroke weight=14 not checked. Dark gray fill not checked. Black keyhole not checked.
**Add (now)**: `CornerRadiusEquals("rectangle", radius=12)`, `StrokeWeightEquals("vector", weight=14)`, `SolidColorEquals("rectangle", dark_gray)`, `SolidColorEquals("ellipse", black)`.

### Task 20 — glow_blob  [in_scope]
**Prompt**: Dark navy frame + 2 overlapping circles (magenta + cyan) + Layer Blur 80.
**Current**: F (frame≥1, ellipse=2), A (overlap + circular), C (FillTypeIs + DistinctSolidColors≥2 + PageBackgroundColorEquals navy), E.
**End-state hole**: ❌ **No `LayerBlurExists` check** despite Layer Blur being a primary feature. Magenta/cyan colors not enforced (any 2 distinct colors pass).
**Event hole**: No `set_property` event for blur.
**Add (now)**: `LayerBlurExists("ellipse")`, `BlurRadiusEquals("ellipse", radius=80)`, two separate `SolidColorEquals` for magenta and cyan.
**Add (now)**: The frame is on canvas but `PageBackgroundColorEquals` checks the *page* background, not the frame fill — this might be the wrong primitive. Use `SolidColorEquals("frame", dark_navy)`.

### Task 21 — button_stack  [out_of_scope]
**Prompt**: Auto-layout vertical stack of 3 buttons.
**Current**: F (rectangle=3), A (sameDims + center_x aligned + stacked y gap=8), C (FillTypeIs + Distinct≥3), E.
**End-state hole**: No frame enforcement (auto-layout creates a wrapper frame). gap=8 in verifier; prompt says 16. Padding 24 not checked.
**Add (now)**: Update `LayersStacked` gap to 16. Add `LayerInsideFrame("rectangle")` once auto-layout ships and produces a frame parent.

### Task 22 — tag_pills  [out_of_scope]
**Prompt**: 4 pill rectangles (radius 999) + small dot inside each, horizontal auto-layout gap=8.
**Current**: F (rectangle=4), A (sameDims + center_y aligned + cornerRadius≥24), C (FillTypeIs + Distinct≥4), E.
**End-state hole**: ❌ Dots not counted (prompt has 8 layers: 4 pills + 4 dots). No `LayersStacked` for horizontal arrangement. No "pastel" color verification (any 4 distinct pass).
**Add (now)**: `ShapeCount("ellipse", equals=4)` (the dots), `LayersStacked(rectangle, axis="x", gap_px=8)`, `LayerContains(outer_type="rectangle", inner_type="ellipse")` for dot-in-pill.

### Task 23 — stretchy_sidebar  [out_of_scope]
**Prompt**: 1440×900 frame + 240×900 dark gray sidebar pinned Left + Top+Bottom; verify resize.
**Current**: F (frame≥1, rectangle=1), A (verticalAspect + widthFraction 0.08–0.30), C (FillTypeIs), E.
**End-state hole**: Constraints (the entire point of the task) NOT checked. Resize event not enforced.
**Add (gap)**: `[GAP] ConstraintHorizontalEquals("rectangle", "left")`, `[GAP] ConstraintVerticalEquals("rectangle", "top_bottom")`. Once added, also `EventTypeUsed("resize_layer")` to confirm resize was performed.
**Add (now)**: `SolidColorEquals(rectangle, dark_gray)`.

### Task 24 — centered_modal  [out_of_scope]
**Prompt**: 1440×900 parent frame + centered 480×320 white rounded modal with drop shadow + Center+Center constraints; resize parent.
**Current**: F (frame≥1, rectangle=1), A (centeredInFrame + cornerRadius≥8), C (FillTypeIs), E (AlignToolUsed).
**End-state hole**: ❌ White fill not checked. ❌ Drop shadow not checked. ❌ Constraints not checked.
**Add (now)**: `AllSolidColorEquals("rectangle", white)`, `DropShadowExists("rectangle")`, `LayerSizeEquals("rectangle", w=480, h=320)`.
**Add (gap)**: `ConstraintHorizontalEquals("rectangle", "center")`, `ConstraintVerticalEquals("rectangle", "center")`.

### Task 25 — button_component  [out_of_scope]
**Prompt**: 3 IDENTICAL 160×40 rectangles in a row, same color.
**Current**: F (rectangle=3), A (sameDims + center_y aligned), C (FillTypeIs), E.
**End-state hole**: ❌ "Same color" not enforced — verifier passes if all 3 are different colors. No specific size check (160×40).
**Add (now)**: `LayerSizeEquals("rectangle", w=160, h=40)`, replace `FillTypeIs` with logic equivalent to "all rectangles share one color" — closest existing primitive: `DistinctSolidColors(maximum=1)` if `maximum=` existed; current closest is `SameColorAcrossTypes(types=["rectangle"])` (which checks first-of-each-type) or `AllSolidColorEquals` with a specific color.
**Add (gap)**: `LayersAllSameColor` (uniform color across all layers of one type).

### Task 26 — color_variable_card  [out_of_scope]
**Prompt**: Single rectangle filled via Color variable; change variable, rectangle updates.
**Current**: F (rectangle=5 — wrong; should be 1), A (sameDims + center_y), C (Distinct≥5), E.
**End-state hole**: Verifier expects 5 squares — wrong artifact for this task. The actual prompt is 1 rectangle whose fill is a variable.
**Add (gap)**: Variable system is out_of_scope; no checks. `VariableBoundFill` would be a new primitive.

### Task 27 — neumorphic_button  [out_of_scope]
**Prompt**: Light gray frame + matching 200×200 rounded rect with 2 paired drop shadows (highlight + shadow) + center icon.
**Current**: F (rectangle=3), A (sameDims + concentric + evenlyRotated step 30°), C (FillTypeIs + Distinct≥3), E.
**End-state hole**: Wrong artifact entirely — verifier expects 3 rotated rectangles. The actual is 1 rect + 2 effects + an icon.
**Add (now)**: For the in_scope simulation: rotation may not be in original prompt at all — verify intent.
**Add (gap)**: Multiple-effect verification (`[GAP] EffectCount` — count of effects on a layer), `[GAP] DropShadowOffsetEquals` (-8,-8 and +8,+8).

### Task 28 — edited_photo  [out_of_scope]
**Prompt**: Photo + image-fill panel adjustments (contrast, saturation, exposure).
**Current**: F (rectangle=1, line=2), A (LinesOnDiagonal), C, E.
**End-state hole**: Wrong artifact — placeholder rectangle with diagonals, not an edited photo.
**Add (gap)**: `[GAP] ImageFitEquals`, image-adjustment fields are not yet in schema.

### Task 29 — polka_dot_grid  [in_scope]
**Prompt**: Off-white frame + 4 same-color circles in 2×2 grid via Tidy up.
**Current**: F (ellipse=4, frame≥1), A (sameDims + grid 2×2 + circular), C (FillTypeIs), E.
**End-state hole**: ❌ Off-white frame fill not checked. ❌ "Same brand color" not enforced. ❌ No `LayerInsideFrame` for the dots.
**Event hole**: ❌ Tidy Up event (`align_layers` or `distribute_layers`) not required despite being explicit in prompt.
**Add (now)**: `SolidColorEquals("frame", off_white)`, `AllSolidColorEquals("ellipse", brand_color)` or `DistinctSolidColors(maximum=1)` if exists, `LayerInsideFrame("ellipse")`, `AlignToolUsed()` or `EventTypeUsed("distribute_layers")`.

### Task 30 — stripe_wallpaper  [in_scope]
**Prompt**: 6 vertical stripes alternating deep blue / cream, full height of 600×600 frame.
**Current**: F (rect=6, frame≥1), A (sameDims + center_y + stacked x gap=0 + verticalAspect + alternating colors n_colors=2), C (FillTypeIs), E.
**End-state hole**: ❌ Specific colors (deep blue, cream) not enforced — `LayersAlternatingColors` only proves 2 distinct colors alternate. No frame containment.
**Add (now)**: `LayersHaveColorOrder` with explicit RGBs in the alternation, `LayerInsideFrame("rectangle")`.

### Task 31 — sun_rays  [in_scope]
**Prompt**: Yellow center circle + 8 evenly rotated triangle rays (at 45° intervals).
**Current**: F (ellipse=1, polygon=8, frame≥1), A (sameDims polygon + circular ellipse), C (FillTypeIs), E.
**End-state hole**: ❌ **No rotation check on rays** despite the entire prompt being about rotation. ❌ No yellow color enforcement. ❌ No radial arrangement check.
**Add (now)**: `LayersEvenlyRotated("polygon", n=8, step_deg=45.0)`, `RadialDistribution("polygon", n=8)`, `SolidColorEquals("ellipse", yellow)`, `LayerInsideFrame("polygon")`.

### Task 32 — pinwheel  [in_scope]
**Prompt**: 4 triangles rotated 90° apart, alternating two colors, points meet at center, plus small center circle.
**Current**: F (polygon=4, ellipse=1, frame≥1), A (sameDims + radial 4 + evenlyRotated 90° + circular), C (FillTypeIs), E.
**End-state hole**: ❌ Two-color alternation not enforced (all 4 same color passes). ❌ "Points meet at center" not directly checked — `RadialDistribution` ensures they're around center but not that *tips* converge.
**Add (now)**: `LayersAlternatingColors("polygon", n_colors=2)`, optionally `LayerCenteredOnLayer(polygon, ellipse)` for the center alignment.

### Task 33 — pie_chart  [in_scope]
**Prompt**: 1 teal circle + 3 colored pie wedges (rotated triangles) overlaid.
**Current**: F (ellipse=1, polygon=3), A (circular ellipse), C (FillTypeIs), E.
**End-state hole**: ❌ Teal base color not enforced. ❌ Wedges not checked for being on top of the circle. ❌ Wedges' rotation not enforced (could be all stacked).
**Add (now)**: `SolidColorEquals("ellipse", teal)`, `LayerOnTopOf(type_a="polygon", type_b="ellipse")`, `LayersHaveRotations("polygon", expected=[various angles], tolerance_deg=20)`, `DistinctSolidColors(minimum=4)` (3 wedges + base must differ).

### Task 34 — snowflake  [in_scope]
**Prompt**: Navy frame + 6 white branches rotated 60° apart for 6-fold symmetry.
**Current**: F (frame≥1, line≥6), C (FillTypeIs frame), E.
**End-state hole**: ❌ **No rotation/symmetry check** — entire point of the task. ❌ No white stroke enforcement on lines. ❌ Frame navy color not checked.
**Add (now)**: `SolidColorEquals("frame", navy)`, `StrokeColorEquals("line", white)`, `LayersHaveRotations("line", expected=[0,60,120,180,240,300], count_per=N, tolerance_deg=10)` — N depends on how branches are grouped.

### Task 35 — honeycomb  [in_scope]
**Prompt**: 6 yellow hexagons with 1px black stroke, 3×2 honeycomb tile.
**Current**: F (polygon=6 + sides=6), A (sameDims + offsetGrid 2×3), C (FillTypeIs), E.
**End-state hole**: ❌ Yellow fill not enforced. ❌ Black 1px stroke not enforced.
**Add (now)**: `AllSolidColorEquals("polygon", yellow)`, `StrokeExists("polygon")`, `StrokeWeightEquals("polygon", weight=1)`, `StrokeColorEquals("polygon", black)`.

### Task 36 — polaroid  [planned]
**Prompt**: 300×340 white rect rotated ~5°, drop shadow, 260×260 image-fill area + bottom caption shape.
**Current**: F (rectangle=2), A (concentric + boundsInside), C (FillTypeIs), E.
**End-state hole**: ❌ Rotation not checked. ❌ White fill not checked. ❌ Drop shadow not checked. ❌ Image fill not checked. ❌ "Off-center" (more bottom margin than top) not checked — `concentric` would actually FAIL on the real artifact since the inner image is not centered vertically.
**Add (now)**: Replace `LayersConcentric` with `LayerCenteredOnLayer` on x-axis only, `LayerRotationEquals("rectangle", degrees=5, tolerance=2)`, `AllSolidColorEquals("rectangle", white)`, `DropShadowExists("rectangle")`.
**Add (gap)**: `ImageFillExists` is in catalog — use it. (No new primitive needed; existing ones suffice.)

### Task 37 — sticky_note  [in_scope]
**Prompt**: Yellow square (rotated ~3°), drop shadow Y=4 blur=8 op=20%, pen-tool fold, 3 horizontal lines.
**Current**: F (rectangle=1, vector≥1, line≥3), A (boundsInside vector-in-rect), C (FillTypeIs), E.
**End-state hole**: ❌ Rotation 3° not checked. ❌ Yellow fill not checked. ❌ Drop shadow not checked. ❌ Lines being horizontal not checked.
**Add (now)**: `LayerRotationEquals("rectangle", degrees=3, tolerance=2)`, `SolidColorEquals("rectangle", yellow)`, `DropShadowExists("rectangle")`, `LayersHaveRotations("line", expected=[0], tolerance_deg=8)` (all horizontal).
**Add (gap)**: `DropShadowOffsetEquals(y=4)`, `DropShadowBlurEquals(8)`.

### Task 38 — battery_indicator  [in_scope]
**Prompt**: 200×80 rounded rect (radius 8) **no fill, gray stroke** (body), 12×32 terminal, 3 inner bars green/yellow/red.
**Current**: F (rectangle=5), A (LayerHasNoFill), C (FillTypeIs), E.
**End-state hole**: ❌ `LayerHasNoFill("rectangle")` is too broad — it passes if ANY rectangle has no fill, but the body rect specifically should have no fill while bars MUST have solid fill. This is an internal contradiction the current verifier can't resolve. ❌ Gray stroke not checked. ❌ Green/yellow/red bars not specifically colored.
**Add (now)**: `StrokeExists("rectangle")` for the body's stroke. Color enforcement on bars needs per-position check (only first 3 in z-order are the bars) — that's a `[GAP] LayerAtZOrderHasColor`. Keep current and accept the noise.
**Add (gap)**: Per-z-order color check.

### Task 39 — wifi_icon  [in_scope]
**Prompt**: 3 concentric pen-tool arcs above 1 small filled circle, 6px navy stroke round caps.
**Current**: F (vector≥3, ellipse=1), C (FillTypeIs ellipse), E.
**End-state hole**: ❌ Stroke weight 6 not checked. ❌ Navy stroke color not checked. ❌ "Concentric" not checked. ❌ Arcs above the circle not checked.
**Add (now)**: `StrokeWeightEquals("vector", weight=6)`, `StrokeColorEquals("vector", navy)`, `LayersConcentric("vector")`, `SolidColorEquals("ellipse", navy)`.

### Task 40 — toggle_switch  [in_scope]
**Prompt**: Green pill (#34C759, 51×31, radius 999) + 27×27 white circle thumb 2px from right edge + small drop shadow.
**Current**: F (rectangle=1, ellipse=1), A (boundsInside + cornerRadius≥24), C (FillTypeIs), E.
**End-state hole**: ❌ Specific green color not enforced. ❌ White circle not enforced. ❌ Pill size 51×31 not enforced. ❌ Thumb size 27×27 not enforced. ❌ "On the right" not checked. ❌ Drop shadow not checked.
**Add (now)**: `SolidColorEquals("rectangle", expected_rgb={r:0.2,g:0.78,b:0.35})`, `SolidColorEquals("ellipse", white)`, `LayerSizeEquals("rectangle", w=51, h=31)`, `LayerSizeEquals("ellipse", w=27, h=27)`, `DropShadowExists("ellipse")`, `LayerNextTo(type_a="ellipse", type_b="rectangle", side="right")` … actually "inside, right side of pill" — use `LayerEdgesAligned(ellipse-right ≈ rectangle-right)`.

### Task 41 — search_bar  [in_scope]
**Prompt**: 320×48 rounded bar (radius 24) light gray + magnifier icon (16px stroked circle + diagonal line) on left + 2 placeholder dots.
**Current**: F (rect=1, ellipse≥3, line≥1), A (LayerHasNoFill ellipse + circular), C (FillTypeIs), E.
**End-state hole**: ❌ Bar size 320×48 not checked. ❌ Bar light gray not checked. ❌ Magnifier circle's 16px size or 2px stroke not checked. ❌ Magnifier "on the left" not checked.
**Add (now)**: `LayerSizeEquals("rectangle", w=320, h=48)`, `SolidColorEquals("rectangle", light_gray)`, `StrokeWeightEquals("ellipse", weight=2)`, `LayerNextTo(type_a="ellipse", type_b="rectangle", side="left")` for magnifier position.

### Task 42 — bell_icon  [in_scope]
**Prompt**: Yellow-gold pen bell + clapper circle + 16×16 red badge with 2px white stroke at upper-right.
**Current**: F (vector≥1, ellipse≥2), A (circular ellipse), C (FillTypeIs vector + ellipse), E.
**End-state hole**: ❌ Yellow-gold not enforced. ❌ Red badge color not enforced. ❌ White stroke 2px not enforced. ❌ Badge "at upper-right" of bell not checked.
**Add (now)**: `SolidColorEquals("vector", gold)`, `SolidColorEquals("ellipse", red)` for the badge, `StrokeExists("ellipse")`, `StrokeWeightEquals("ellipse", weight=2)`, `StrokeColorEquals("ellipse", white)`, `LayerNextTo(type_a="ellipse", type_b="vector", side="top_right")` if such edge exists, else `LayerEdgesAligned`.

### Task 43 — compass_rose  [in_scope]
**Prompt**: Sand circle + 4 N/E/S/W triangle points (N red, others gray) + 24px gold center circle.
**Current**: F (ellipse=2, polygon=4), A (sameDims polygon + circular), C (FillTypeIs), E.
**End-state hole**: ❌ N-red vs others-gray not enforced. ❌ Sand color not enforced. ❌ Gold center not enforced. ❌ 90° rotation step (the 4 cardinal directions) not enforced.
**Add (now)**: `LayersEvenlyRotated("polygon", n=4, step_deg=90.0)`, `LayersConcentric("polygon")`, `SolidColorEquals("ellipse", sand)` and another for gold (need 2 distinct ellipse colors — `DistinctSolidColors(minimum=2)`), `DistinctSolidColors(layer_type="polygon", minimum=2)` for one-red-others-gray.

### Task 44 — avatar_status  [planned]
**Prompt**: 64×64 image-filled circle + 16×16 green status dot at bottom-right with 2px white stroke.
**Current**: F (ellipse=2), A (overlap + onTopOf + circular), C (FillTypeIs), E.
**End-state hole**: ❌ Image fill not enforced (this is the entire feature). ❌ Sizes (64, 16) not enforced. ❌ Green color not enforced. ❌ White 2px stroke not enforced. ❌ "Bottom-right" position not enforced.
**Add (now)**: `ImageFillExists("ellipse")` (already in catalog), `LayerSizeEquals("ellipse", w=64, h=64)` for one — but `LayerSizeEquals` works on ALL of type, so need distinct handling. `SolidColorEquals("ellipse", green)`, `StrokeWeightEquals("ellipse", weight=2)`, `StrokeColorEquals("ellipse", white)`, `LayerNextTo(...)` or `LayerEdgesAligned` to enforce bottom-right.
**Add (gap)**: Multi-criteria layer-by-index check (handle the 2-of-same-type-but-different-sizes case cleanly).

### Task 45 — geometric_emblem  [in_scope]
**Prompt**: Deep blue 8-point star + smaller yellow circle perfectly centered on top.
**Current**: F (star=1 + StarPointsEquals=8, ellipse=1), A (boundsInside + centeredOnLayer + circular), C (FillTypeIs), E.
**End-state hole**: ❌ Deep blue not enforced. ❌ Yellow not enforced. ❌ "Smaller" not directly checked (only that it fits inside).
**Add (now)**: `SolidColorEquals("star", deep_blue)`, `SolidColorEquals("ellipse", yellow)`, `LayerOnTopOf(type_a="ellipse", type_b="star")`.

### Task 46 — audio_waveform  [out_of_scope]
**Prompt**: 8 vertical 8px-wide bars varying heights, horizontal auto-layout gap=4, graduated color across.
**Current**: F (rectangle=8), C (FillTypeIs), E.
**End-state hole**: ❌ No alignment check. ❌ No bottom-baseline enforcement. ❌ No graduated color. ❌ No 8px width / no varying heights.
**Add (now)**: `LayerWidthFraction` won't help (parents differ); use `LayerSizeEquals("rectangle", width=8)`. Add `LayerEdgesAligned(rectangle-bottom-rectangle-bottom)` for shared baseline, `LayersStacked("rectangle", axis="x", gap_px=4)`, `DistinctSolidColors("rectangle", minimum=8)` for graduated.
**Add (gap)**: A "monotonic-color-gradient-across" primitive would be nicer than just "distinct."

### Task 47 — sunburst_badge  [in_scope]
**Prompt**: 16-point star with inner radius ~70%, warm orange + smaller cream circle centered on top.
**Current**: F (star=1, points=16, innerRatio=0.70±0.05, ellipse=1), A (centeredOnLayer + circular), C (FillTypeIs), E.
**End-state hole**: ❌ Warm orange not enforced. ❌ Cream not enforced. ❌ Circle "smaller" than star not checked.
**Add (now)**: `SolidColorEquals("star", warm_orange)`, `SolidColorEquals("ellipse", cream)`, `LayerBoundsInside(inner_type="ellipse", outer_type="star")`.

### Task 48 — spiderweb  [in_scope]
**Prompt**: Navy frame + 6 white radial lines (60° apart) + 3 concentric stroked hexagons.
**Current**: F (frame≥1, line≥6, polygon=3, sides=6), A (LayerHasNoFill polygon), C (FillTypeIs frame), E.
**End-state hole**: ❌ White stroke on lines not checked. ❌ White stroke on hexagons not checked. ❌ Navy frame color not checked. ❌ Lines being radial (60°) not checked. ❌ Hexagons concentric not checked.
**Add (now)**: `SolidColorEquals("frame", navy)`, `StrokeColorEquals("line", white)`, `StrokeColorEquals("polygon", white)`, `LayersEvenlyRotated("line", n=6, step_deg=60)`, `LayersConcentric("polygon")`.

### Task 49 — decorative_ribbon  [out_of_scope]
**Prompt**: Pen S-curve, 12px stroke custom dash, outline stroke → vector, gold-bronze linear gradient fill.
**Current**: F (vector≥1), C (FillTypeIs solid), E (pen + create_vector).
**End-state hole**: Wrong artifact — gradient not in scope. Stroke 12px not checked. Dash pattern not checked.
**Add (now)**: For the in_scope simulation: maybe `StrokeExists` + `StrokeIsDashed("vector")`.
**Add (gap)**: Gradient fills + outline-stroke event.

### Task 50 — album_cover  [out_of_scope]
**Prompt**: Photo masked by 5-point star, 4px white border around masked region.
**Current**: F (rectangle=1, star=1, points=5), A (boundsInside + centeredOnLayer), C (FillTypeIs), E.
**End-state hole**: Wrong artifact — no photo (image fill), no mask. 4px white border not checked.
**Add (now)**: `StrokeWeightEquals("star", weight=4)`, `StrokeColorEquals("star", white)`.
**Add (gap)**: Mask features (out_of_scope).

---

## Action priorities

**Quick wins** (existing primitives, high-impact across many tasks):

1. Add `SolidColorEquals` / `AllSolidColorEquals` everywhere a prompt names a
   color but only `FillTypeIs` is checked. (~25 tasks)
2. Add stroke checks (`StrokeExists`, `StrokeWeightEquals`, `StrokeColorEquals`)
   wherever the prompt mentions stroke. (~12 tasks)
3. Add `DropShadowExists` everywhere shadow is in the prompt. (~8 tasks)
4. Add `LayerInsideFrame` everywhere a frame is set up. (~10 tasks)
5. Add `LayerRotationEquals` / `LayersEvenlyRotated` wherever rotation is in
   prompt. (~8 tasks)

**Library extensions** (build these `[GAP]` primitives next):

1. `DropShadowOffsetEquals`, `DropShadowBlurEquals`, `DropShadowSpreadEquals` — shipped feature, 6+ tasks need them.
2. `LayersAllSameColor` (or `DistinctSolidColors` with `maximum=1`) — task 25 + 29 + 35.
3. `ConstraintHorizontalEquals`, `ConstraintVerticalEquals` — tasks 23 + 24.
4. `LayersHaveColorOrderBySize` (sort axis = size, for concentric layers) — task 14.
5. `LayerAtZOrderHasColor` — task 38 (battery bars in sequence).

**Wait for feature ship** (Tier-2 gaps):

- Gradient fill checks → unlocks tasks 2, 3, 4, 49.
- Boolean-op verification → unlocks tasks 5, 6, 13, 15, 16, 17, 18.
- Mask features → unlocks tasks 10, 50.
- Variables → unlocks task 26.
- Auto-layout properties → tasks 21, 22, 46.
- Inner shadow → task 11.
- Color/effect styles → tasks 9, 12.

---

## 🟢 Resolved in this round

**New primitives built** (10):
- `effect_checks.py:DropShadowOffsetEquals`, `DropShadowBlurEquals`, `DropShadowSpreadEquals`, `EffectCount`
- `fill_checks.py:LayersAllSameColor` + `LayersHaveColorOrder` extended with `sort_axis="size"`
- `property_checks.py:ConstraintHorizontalEquals`, `ConstraintVerticalEquals`
- `text_checks.py:VerticalAlignEquals`, `LineHeightEquals`, `LetterSpacingEquals`

**Verifier hardenings** (~30 tasks): added missing color, stroke, shadow,
rotation, frame-containment, and constraint checks per the Tier-1 priorities.

**Medium tasks reshaped to Easy** (12 of the original 21):
- 31 sun_rays (8 → 4 rays)
- 33 pie_chart (3 → 2 wedges)
- 34 snowflake (6-fold → 4-fold)
- 35 honeycomb (3×2 → 2×2)
- 39 wifi_icon (3 → 2 arcs)
- 41 search_bar (2 → 1 dot)
- 42 bell_icon (kept simple, hardened)
- 46 audio_waveform (8 → 5 bars)
- 47 sunburst_badge (16 → 8 points)
- 48 spiderweb (6 lines + 3 hex → 4 lines + 2 hex)
- 49 decorative_ribbon (gradient → dashed stroke)
- (35 in this list also appears in hexagon item)

For each reshaped task: prompt.md updated, README index difficulty re-marked
"Easy", verifier rubrics aligned with the new artifact.

**QA harness** extended to satisfy new primitives in synthetic perfect logs:
50/50 tasks score `OK` (≥0.7 perfect, ≤0.3 empty) with no `STRICT`,
`LENIENT`, or `CRASH` flags.

**Delivery-1 sync**: `delivery-1/task_NN/verifier.py` is now in lockstep with
`test-verifier/tasks/task_NN_*.py`. Future re-syncs via
`scripts/sync_delivery.sh`.

**Still open** (Tier-2 + Tier-1 deferred): see §16's tier-1 table for the
9 remaining `[GAP]` items (corner-radius tuple, constraint-related text,
arc properties, image-fit, dash properties, overflow scrolling, multi-run
text, z-order between, distribute event). Build these as new prompts/tasks
require them.
