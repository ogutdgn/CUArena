# Verifier Correctness Audit — does each verifier check what its prompt asks for?

_Generated May 10, 2026. This audit ignores model performance entirely. The only
question is: **does each task's verifier accurately enforce what its own
`prompt.md` asks for**?_

For each task, we parse the prompt's `## Thorough description` section
(the contract the harness sends to the model in default prompt-mode) and
cross-reference it against the verifier's checks. Mismatches are flagged
by category:

| Issue type | Meaning | Severity |
|---|---|---|
| `FRAME-OVERSPEC` | Verifier requires `LayerInsideFrame` / `AllLayerBoundsInside(outer=frame)` but the prompt's thorough description never mentions a Figma frame. | high |
| `FRAME-UNDERSPEC` | Prompt explicitly asks for a frame but verifier has no frame containment check. | low |
| `BRITTLE-ALIGN-TOLERANCE` | Verifier uses an alignment tolerance below 15 px. Tight relative to typical drag-create variance. | medium |
| `EFFECT-OVERSPEC` | Verifier requires drop-shadow / blur effect but prompt doesn't mention effects. | medium |
| `SIZE-OVERSPEC` | Verifier requires exact W×H but the prompt only gives a qualitative size. | medium |
| `COLOR-OVERSPEC` | Verifier requires a specific RGB but the prompt mentions no color. | medium |
| `SHAPE-CHECK-MISSING` | Prompt names a quantity of shapes but verifier has no ShapeCount check for that type. | medium |
| `CORNER-RADIUS-OVERSPEC` | Verifier REQUIRES rounded corners (`CornerRadiusAtLeast(min_value > 0)`) but prompt doesn't mention 'rounded'. | medium |

Notes on what we **don't** flag:
- `CornerRadiusFractionAtMost` (a 'don't be too round / accidentally became a pill' sanity check) is
  legitimate and not counted as over-spec.
- Tool-use is a recipe hint, not a contract. Verifiers should check outputs, not which tool
  produced them. Tool-mismatch is not a correctness gap.
- Critical-halving rules in the rubric framework are a tuning issue, not a correctness gap.

## Headline

| Metric | Value |
|---|---|
| Tasks audited | **50/50** |
| **CLEAN** (no detected issues) | **11** |
| With ≥ 1 issue | 39 |
| High-severity issues total | 27 |
| Medium-severity issues total | 31 |

**Issue-type counts:**

| Issue type | Count | % of tasks |
|---|---|---|
| `FRAME-OVERSPEC` | 27 | 54% |
| `BRITTLE-ALIGN-TOLERANCE` | 24 | 48% |
| `EFFECT-OVERSPEC` | 3 | 6% |
| `SIZE-OVERSPEC` | 2 | 4% |
| `FRAME-UNDERSPEC` | 1 | 2% |
| `SHAPE-CHECK-MISSING` | 1 | 2% |
| `COLOR-OVERSPEC` | 1 | 2% |

**Cross-tabulation of the two biggest issues:**

| | brittle-align | clean align |
|---|---|---|
| frame-overspec | 14 | 13 |
| clean frame | 10 | 13 |

## CLEAN tasks (11)

Verifiers that match their prompt cleanly — no detected over-spec or brittleness:

- `task_04_color_wheel`
- `task_06_gold_star_exclude`
- `task_07_mountain_range`
- `task_08_water_waves`
- `task_20_glow_blob`
- `task_23_stretchy_sidebar`
- `task_33_pie_chart`
- `task_36_polaroid`
- `task_47_sunburst_badge`
- `task_49_decorative_ribbon`
- `task_50_album_cover`

## Per-issue inventories

### `FRAME-OVERSPEC` (27 tasks)

- `task_03_glowing_orb` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_09_brand_palette` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_12_shadowed_cards` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_13_night_sky` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_14_concentric_target` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_15_cloud_union` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_16_speech_bubble` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_17_play_button` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_18_donut` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_19_padlock` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_21_button_stack` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_22_tag_pills` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_25_button_component` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_26_color_variable_card` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_27_neumorphic_button` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_28_edited_photo` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_31_sun_rays` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_32_pinwheel` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_37_sticky_note` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_38_battery_indicator` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_40_toggle_switch` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_41_search_bar` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_42_bell_icon` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_43_compass_rose` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_44_avatar_status` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_45_geometric_emblem` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio
- `task_46_audio_waveform` — Verifier requires LayerInsideFrame / AllLayerBoundsInside(outer=frame) but prompt's Thorough description does not mentio

### `BRITTLE-ALIGN-TOLERANCE` (24 tasks)

- `house_task_comprehensive` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_02_sunset_gradient` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_05_red_heart_union` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_09_brand_palette` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_10_apple_avatar` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_11_pressed_button` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_12_shadowed_cards` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_13_night_sky` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_14_concentric_target` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_17_play_button` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_18_donut` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_21_button_stack` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_22_tag_pills` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_25_button_component` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_26_color_variable_card` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_29_polka_dot_grid` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_30_stripe_wallpaper` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_31_sun_rays` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_32_pinwheel` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_34_snowflake` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_35_honeycomb` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_43_compass_rose` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_46_audio_waveform` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom
- `task_48_spiderweb` — Verifier uses alignment tolerance < 15 px — strict beyond typical drag accuracy. This is a calibration issue, not a prom

### `FRAME-UNDERSPEC` (1 tasks)

- `task_02_sunset_gradient` — Prompt mentions a frame (Create a frame) but verifier has no frame containment check.

### `EFFECT-OVERSPEC` (3 tasks)

- `task_24_centered_modal` — Verifier requires drop-shadow / effect checks but prompt mentions no effects.
- `task_37_sticky_note` — Verifier requires drop-shadow / effect checks but prompt mentions no effects.
- `task_40_toggle_switch` — Verifier requires drop-shadow / effect checks but prompt mentions no effects.

### `SIZE-OVERSPEC` (2 tasks)

- `task_25_button_component` — Verifier requires exact W×H (1 check(s)) but prompt mentions no pixel dimensions.
- `task_41_search_bar` — Verifier requires exact W×H (1 check(s)) but prompt mentions no pixel dimensions.

### `COLOR-OVERSPEC` (1 tasks)

- `task_41_search_bar` — Verifier requires 1 specific RGB(s) but prompt mentions no named color or hex.

### `SHAPE-CHECK-MISSING` (1 tasks)

- `task_39_wifi_icon` — Prompt mentions '200 frame(s)' but verifier has no ShapeCount/ShapeCountAtLeast check for 'frame'.

## Full per-task table

| Task | # Issues | Severity max | Types |
|---|---|---|---|
| `task_25_button_component` | 3 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC, SIZE-OVERSPEC |
| `task_41_search_bar` | 3 | high | COLOR-OVERSPEC, FRAME-OVERSPEC, SIZE-OVERSPEC |
| `task_09_brand_palette` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_12_shadowed_cards` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_13_night_sky` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_14_concentric_target` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_17_play_button` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_18_donut` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_21_button_stack` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_22_tag_pills` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_26_color_variable_card` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_31_sun_rays` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_32_pinwheel` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_37_sticky_note` | 2 | high | EFFECT-OVERSPEC, FRAME-OVERSPEC |
| `task_40_toggle_switch` | 2 | high | EFFECT-OVERSPEC, FRAME-OVERSPEC |
| `task_43_compass_rose` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_46_audio_waveform` | 2 | high | BRITTLE-ALIGN-TOLERANCE, FRAME-OVERSPEC |
| `task_03_glowing_orb` | 1 | high | FRAME-OVERSPEC |
| `task_15_cloud_union` | 1 | high | FRAME-OVERSPEC |
| `task_16_speech_bubble` | 1 | high | FRAME-OVERSPEC |
| `task_19_padlock` | 1 | high | FRAME-OVERSPEC |
| `task_27_neumorphic_button` | 1 | high | FRAME-OVERSPEC |
| `task_28_edited_photo` | 1 | high | FRAME-OVERSPEC |
| `task_38_battery_indicator` | 1 | high | FRAME-OVERSPEC |
| `task_42_bell_icon` | 1 | high | FRAME-OVERSPEC |
| `task_44_avatar_status` | 1 | high | FRAME-OVERSPEC |
| `task_45_geometric_emblem` | 1 | high | FRAME-OVERSPEC |
| `task_02_sunset_gradient` | 2 | medium | BRITTLE-ALIGN-TOLERANCE, FRAME-UNDERSPEC |
| `house_task_comprehensive` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_05_red_heart_union` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_10_apple_avatar` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_11_pressed_button` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_24_centered_modal` | 1 | medium | EFFECT-OVERSPEC |
| `task_29_polka_dot_grid` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_30_stripe_wallpaper` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_34_snowflake` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_35_honeycomb` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_39_wifi_icon` | 1 | medium | SHAPE-CHECK-MISSING |
| `task_48_spiderweb` | 1 | medium | BRITTLE-ALIGN-TOLERANCE |
| `task_04_color_wheel` | 0 | — | — |
| `task_06_gold_star_exclude` | 0 | — | — |
| `task_07_mountain_range` | 0 | — | — |
| `task_08_water_waves` | 0 | — | — |
| `task_20_glow_blob` | 0 | — | — |
| `task_23_stretchy_sidebar` | 0 | — | — |
| `task_33_pie_chart` | 0 | — | — |
| `task_36_polaroid` | 0 | — | — |
| `task_47_sunburst_badge` | 0 | — | — |
| `task_49_decorative_ribbon` | 0 | — | — |
| `task_50_album_cover` | 0 | — | — |

## Recommended actions (verifier-side only)

In priority order by tasks-affected × severity:

### 1. Audit and remove unstated frame mandates (27 tasks)

Review every verifier flagged FRAME-OVERSPEC. For each:
- Re-read the prompt's thorough description.
- If the prompt doesn't mention a Figma frame as a design element, remove
  `LayerInsideFrame(...)` and replace `AllLayerBoundsInside(outer_type="frame", ...)` with
  either no containment check or a permissive equivalent.
- If the prompt does mention a frame implicitly (e.g. 'in a 200×200 canvas')
  but not as a Figma frame primitive, decide whether the verifier should be
  flexible about page-level vs frame-level containment.

### 2. Calibrate sub-15 px alignment tolerances (24 tasks)

Find every `Layers*` check with `tolerance < 15` and increase to 25–35 px,
unless the prompt explicitly says 'pixel-perfect' or 'exactly centered'.
Combined with the critical-halving rule in
`apps/figma/verifier/rubrics/_base.py:36`, a single sub-15 px miss collapses
the entire alignment rubric to 50% × (pass_count / total).

### 3. Audit the 3 EFFECT-OVERSPEC tasks

Tasks where the verifier checks for drop shadows the prompt never requested:
- `task_24_centered_modal`
- `task_37_sticky_note`
- `task_40_toggle_switch`

Decide: is the shadow check intentional ("bonus credit") or a mistake? If
intentional, document it. If a mistake, remove the EffectRubric.

### 4. Resolve narrow size/color over-specifications

- `SIZE-OVERSPEC` (2 tasks): verifier asks for exact pixel dimensions the
  prompt never gave. Remove the LayerSizeEquals or replace with a permissive
  size range.
- `COLOR-OVERSPEC` (1 task): verifier asks for a specific RGB the prompt
  doesn't name. Replace with LayersAllSameColor or a fill-type check.

---

Per [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md), this audit only reports;
it does not patch `delivery-1/task_NN/verifier.py` files. Authorize specific
patches as a follow-up if you want them applied.
