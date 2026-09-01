# Verifier Audit — figma-50 vs. Qwen3.5-27B rollouts

_Generated May 10, 2026 from `audit_data.json` (433,398 bytes)._

This audit cross-references all 50 task verifiers in `delivery-1/` against the
merged 150-attempt rollout (parent + 3 fill-ins). For each task it inspects:
- the verifier's rubrics, weights, critical checks, and tolerance values (statically)
- the 3 rollout attempts' scores, plateau pattern, stop reasons, and per-rubric breakdown
- the actual scene-graph + semantic events from a representative log.json

Each task gets a single-word verdict that distinguishes verifier issues from model issues:

| Verdict | Meaning |
|---|---|
| `passing` | Task already passes (best ≥ 0.7) |
| `verifier-primary` | **Verifier IS the bottleneck.** Estimated post-verifier-fix score ≥ 0.7. Fixing the verifier would unlock this task. |
| `model-primary` | Verifier has issues but model is the bigger blocker. Verifier fix lifts the score but still < 0.7. |
| `honest` | No verifier-fixable lift available. Low score reflects model capability. |
| `mock-gap` | Hard zero: agent attempted the required tool but the mock didn't log the shape. |
| `model-gap` | Hard zero: agent never attempted the required tool. |

Verdicts use a `compute_verdict()` heuristic that simulates removing the two
biggest verifier brittleness sources (frame-mandate + critical-halving) and re-scores.
Tasks where the simulated score crosses 0.7 are `verifier-primary`. Tasks where the
lift is real but doesn't reach 0.7 are `model-primary` — the verifier compounds the
gap, but the model can't fully close it either way.

## Headline

| Metric | Value |
|---|---|
| Tasks audited | **50/50** |
| Tasks passing (≥0.7) | 2 |
| Plateau tasks (range < 0.05 across 3 attempts) | **27** (54%) |
| Verifiers requiring a frame | **38** (76%) |
| Verifiers with alignment tolerance < 15 px | **24** (48%) |

**Verdict distribution:**

- `model-primary`: **33** tasks
- `verifier-primary`: **7** tasks
- `honest`: **5** tasks
- `passing`: **2** tasks
- `model-gap`: **2** tasks
- `mock-gap`: **1** tasks

## Aggregate gap categories

### Gap 1 — Frame mandated by verifier but not by prompt

**38/50 verifiers** include either `LayerInsideFrame(...)` or
`AllLayerBoundsInside(outer_type="frame")`. The model rarely creates an explicit
frame element (it draws shapes directly on the canvas), so this check fails on
nearly every attempt. The cost is ~10% of the rubric weight per affected task.

Tasks where the verifier IS the primary blocker (verdict=`verifier-primary`):

- `house_task_comprehensive` (best=0.065)
- `task_03_glowing_orb` (best=0.125)
- `task_07_mountain_range` (best=0.250)
- `task_08_water_waves` (best=0.138)
- `task_09_brand_palette` (best=0.300)
- `task_12_shadowed_cards` (best=0.354)
- `task_13_night_sky` (best=0.317)
- `task_14_concentric_target` (best=0.095)
- `task_15_cloud_union` (best=0.181)
- `task_16_speech_bubble` (best=0.095)
- `task_18_donut` (best=0.308)
- `task_19_padlock` (best=0.285)
- `task_20_glow_blob` (best=0.182)
- `task_21_button_stack` (best=0.253)
- `task_22_tag_pills` (best=0.301)
- `task_23_stretchy_sidebar` (best=0.635)
- `task_24_centered_modal` (best=0.550)
- `task_25_button_component` (best=0.688)
- `task_26_color_variable_card` (best=0.299)
- `task_27_neumorphic_button` (best=0.557)
- _...and 16 more_

### Gap 2 — Brittle alignment tolerances (< 15 px)

**24/50 verifiers** use a sub-15px alignment tolerance.
Typical agent drag-creation lands ±20-30px off perfect alignment. Combined with
the critical-halving rule in `verifier/rubrics/_base.py:36`, a single off-center
rectangle collapses the entire alignment rubric to 50% × (pass_count/total).

Verbatim from `verifier/rubrics/_base.py:36`:
```python
if any(i < len(results) and not results[i].passed for i in self.critical):
    score *= 0.5
```

### Gap 3 — All-or-nothing effect rubrics

Effect-heavy tasks like task_27 (`EffectRubric`: 4 checks for drop-shadow
count + opposing offsets) score 0/0.2 every time because the model never opens
the effects panel. With no partial credit for "shadow exists," the rubric is
an information-free hard zero.

### Gap 4 — Hard zeros from missing shape types

Tasks scoring exactly 0.000 across all 3 attempts where the verifier requires
a shape type the mock never logged or the agent never attempted:

- `task_11_pressed_button` — verdict=`model-gap`, required: ['polygon'], missing: ['polygon']
- `task_35_honeycomb` — verdict=`model-gap`, required: ['polygon'], missing: ['polygon']
- `task_47_sunburst_badge` — verdict=`mock-gap`, required: ['star', 'ellipse'], missing: ['star', 'ellipse']

### Gap 5 — Plateau scores reveal deterministic failure modes

**27/50 tasks scored within 0.05 across all 3 attempts.** This
means k=3 retries are not unlocking variance — the model lands on the same
partial solution every time, and the verifier locks that solution at a fixed
sub-threshold score. k>3 retries would NOT improve these tasks.

## Per-task verdicts

All 50 tasks, grouped by verdict and sorted by best score.

### 🔧 Verifier-primary tasks (7) — fixing the verifier would push past 0.7

| Task | Best | Mean | Plateau | Frame req | Brittle align | Top reason |
|---|---|---|---|---|---|---|
| `task_25_button_component` | 0.688 | 0.674 | yes | yes | yes | Current 0.688; post-verifier-fix estimate 0.792 → would pass (lift +0.104) |
| `task_49_decorative_ribbon` | 0.688 | 0.576 | — | — | — | Current 0.688; post-verifier-fix estimate 0.750 → would pass (lift +0.062) |
| `task_28_edited_photo` | 0.643 | 0.526 | — | yes | — | Current 0.643; post-verifier-fix estimate 0.814 → would pass (lift +0.171) |
| `task_23_stretchy_sidebar` | 0.635 | 0.334 | — | yes | — | Current 0.635; post-verifier-fix estimate 0.755 → would pass (lift +0.120) |
| `task_44_avatar_status` | 0.605 | 0.587 | yes | yes | — | Current 0.605; post-verifier-fix estimate 0.823 → would pass (lift +0.218) |
| `task_46_audio_waveform` | 0.599 | 0.575 | yes | yes | yes | Current 0.674; post-verifier-fix estimate 0.905 → would pass (lift +0.232) |
| `task_27_neumorphic_button` | 0.557 | 0.557 | yes | yes | — | Current 0.557; post-verifier-fix estimate 0.743 → would pass (lift +0.186) |

### 🤖 Model-primary tasks (33) — verifier issues exist but model is the bigger blocker

| Task | Best | Mean | Plateau | Frame req | Brittle align | Top reason |
|---|---|---|---|---|---|---|
| `task_24_centered_modal` | 0.550 | 0.387 | — | yes | — | Verifier fix would lift 0.550 → 0.640 (+0.090), still below 0.7 threshold — m... |
| `task_38_battery_indicator` | 0.393 | 0.393 | yes | yes | — | Verifier fix would lift 0.393 → 0.617 (+0.225), still below 0.7 threshold — m... |
| `task_12_shadowed_cards` | 0.354 | 0.295 | — | yes | yes | Verifier fix would lift 0.355 → 0.527 (+0.173), still below 0.7 threshold — m... |
| `task_29_polka_dot_grid` | 0.328 | 0.217 | — | yes | yes | Verifier fix would lift 0.328 → 0.478 (+0.150), still below 0.7 threshold — m... |
| `task_13_night_sky` | 0.317 | 0.258 | — | yes | yes | Verifier fix would lift 0.317 → 0.467 (+0.150), still below 0.7 threshold — m... |
| `task_18_donut` | 0.308 | 0.289 | yes | yes | yes | Verifier fix would lift 0.308 → 0.430 (+0.122), still below 0.7 threshold — m... |
| `task_50_album_cover` | 0.304 | 0.304 | yes | — | — | Verifier fix would lift 0.304 → 0.482 (+0.179), still below 0.7 threshold — m... |
| `task_22_tag_pills` | 0.301 | 0.301 | yes | yes | yes | Verifier fix would lift 0.301 → 0.438 (+0.137), still below 0.7 threshold — m... |
| `task_09_brand_palette` | 0.300 | 0.183 | — | yes | yes | Verifier fix would lift 0.300 → 0.400 (+0.100), still below 0.7 threshold — m... |
| `task_26_color_variable_card` | 0.299 | 0.297 | yes | yes | yes | Verifier fix would lift 0.358 → 0.508 (+0.150), still below 0.7 threshold — m... |
| `task_34_snowflake` | 0.289 | 0.163 | — | yes | yes | Verifier fix would lift 0.289 → 0.575 (+0.286), still below 0.7 threshold — m... |
| `task_19_padlock` | 0.285 | 0.217 | — | yes | — | Verifier fix would lift 0.285 → 0.419 (+0.135), still below 0.7 threshold — m... |
| `task_33_pie_chart` | 0.255 | 0.255 | yes | — | — | Verifier fix would lift 0.255 → 0.385 (+0.130), still below 0.7 threshold — m... |
| `task_30_stripe_wallpaper` | 0.255 | 0.242 | yes | yes | yes | Verifier fix would lift 0.255 → 0.409 (+0.155), still below 0.7 threshold — m... |
| `task_21_button_stack` | 0.253 | 0.253 | yes | yes | yes | Verifier fix would lift 0.315 → 0.455 (+0.140), still below 0.7 threshold — m... |
| `task_07_mountain_range` | 0.250 | 0.183 | — | yes | — | Verifier fix would lift 0.250 → 0.400 (+0.150), still below 0.7 threshold — m... |
| `task_40_toggle_switch` | 0.238 | 0.235 | yes | yes | — | Verifier fix would lift 0.238 → 0.405 (+0.166), still below 0.7 threshold — m... |
| `task_31_sun_rays` | 0.217 | 0.170 | — | yes | yes | Verifier fix would lift 0.217 → 0.433 (+0.217), still below 0.7 threshold — m... |
| `task_42_bell_icon` | 0.183 | 0.153 | — | yes | — | Verifier fix would lift 0.183 → 0.327 (+0.143), still below 0.7 threshold — m... |
| `task_20_glow_blob` | 0.182 | 0.175 | yes | yes | — | Verifier fix would lift 0.182 → 0.300 (+0.118), still below 0.7 threshold — m... |
| `task_15_cloud_union` | 0.181 | 0.181 | yes | yes | — | Verifier fix would lift 0.181 → 0.386 (+0.206), still below 0.7 threshold — m... |
| `task_43_compass_rose` | 0.168 | 0.168 | yes | yes | yes | Verifier fix would lift 0.168 → 0.247 (+0.078), still below 0.7 threshold — m... |
| `task_41_search_bar` | 0.164 | 0.164 | yes | yes | — | Verifier fix would lift 0.164 → 0.322 (+0.158), still below 0.7 threshold — m... |
| `task_04_color_wheel` | 0.150 | 0.131 | yes | — | — | Verifier fix would lift 0.150 → 0.250 (+0.100), still below 0.7 threshold — m... |
| `task_08_water_waves` | 0.138 | 0.079 | — | yes | — | Verifier fix would lift 0.138 → 0.325 (+0.188), still below 0.7 threshold — m... |
| `task_39_wifi_icon` | 0.129 | 0.100 | — | yes | — | Verifier fix would lift 0.129 → 0.285 (+0.156), still below 0.7 threshold — m... |
| `task_03_glowing_orb` | 0.125 | 0.079 | — | yes | — | Verifier fix would lift 0.125 → 0.200 (+0.075), still below 0.7 threshold — m... |
| `task_48_spiderweb` | 0.121 | 0.081 | — | yes | yes | Verifier fix would lift 0.169 → 0.307 (+0.138), still below 0.7 threshold — m... |
| `task_37_sticky_note` | 0.100 | 0.089 | yes | yes | — | Verifier fix would lift 0.100 → 0.234 (+0.134), still below 0.7 threshold — m... |
| `task_16_speech_bubble` | 0.095 | 0.095 | yes | yes | — | Verifier fix would lift 0.190 → 0.363 (+0.173), still below 0.7 threshold — m... |
| `task_14_concentric_target` | 0.095 | 0.094 | yes | yes | yes | Verifier fix would lift 0.189 → 0.411 (+0.222), still below 0.7 threshold — m... |
| `house_task_comprehensive` | 0.065 | 0.024 | — | yes | yes | Verifier fix would lift 0.075 → 0.171 (+0.096), still below 0.7 threshold — m... |
| `task_32_pinwheel` | 0.042 | 0.042 | yes | yes | yes | Verifier fix would lift 0.042 → 0.117 (+0.075), still below 0.7 threshold — m... |

### = Honest scoring tasks (5) — no verifier-fixable lift, score reflects model

| Task | Best | Mean | Plateau | Frame req | Brittle align | Top reason |
|---|---|---|---|---|---|---|
| `task_06_gold_star_exclude` | 0.150 | 0.150 | yes | — | — | No meaningful verifier-fixable lift (0.150 → 0.150). Score reflects model cap... |
| `task_02_sunset_gradient` | 0.050 | 0.044 | yes | — | yes | No meaningful verifier-fixable lift (0.050 → 0.050). Score reflects model cap... |
| `task_10_apple_avatar` | 0.039 | 0.039 | yes | — | yes | No meaningful verifier-fixable lift (0.050 → 0.050). Score reflects model cap... |
| `task_17_play_button` | 0.015 | 0.015 | yes | yes | yes | No meaningful verifier-fixable lift (0.015 → 0.031). Score reflects model cap... |
| `task_45_geometric_emblem` | 0.006 | 0.006 | yes | yes | — | No meaningful verifier-fixable lift (0.006 → 0.013). Score reflects model cap... |

### ✓ Passing tasks (2)

| Task | Best | Mean | Plateau | Frame req | Brittle align | Top reason |
|---|---|---|---|---|---|---|
| `task_36_polaroid` | 0.825 | 0.743 | — | — | — | Passing (2/3 attempts) |
| `task_05_red_heart_union` | 0.733 | 0.649 | — | — | yes | Passing (1/3 attempts) |

### 0️⃣ Hard zero (model-gap) (2) — agent never tried required tool

| Task | Best | Mean | Plateau | Frame req | Brittle align | Top reason |
|---|---|---|---|---|---|---|
| `task_11_pressed_button` | 0.000 | 0.000 | — | — | yes | Agent never created required shape type(s) ['polygon'] in any log across 3 at... |
| `task_35_honeycomb` | 0.000 | 0.000 | — | — | yes | Agent never created required shape type(s) ['polygon'] in any log across 7 at... |

### 🪵 Hard zero (mock-gap) (1) — mock didn't log the shape type

| Task | Best | Mean | Plateau | Frame req | Brittle align | Top reason |
|---|---|---|---|---|---|---|
| `task_47_sunburst_badge` | 0.000 | 0.000 | — | — | — | Required ['star', 'ellipse'] but only ['star'] ever attempted |

## Plateau math (top 10)

Tasks where all 3 attempts produced near-identical scores. The plateau score
equals the sum of rubric × weight × (pass_count/total) [× 0.5 if any critical
check fails in that rubric]:

### `task_25_button_component` — plateau at 0.688 × 3 attempts

- **fundamentals**: 0.200/0.200 (1/1 checks pass)
- **alignment**: 0.062/0.250 (3/6 checks pass)
  - fail: `rect_mp0: w=100 ≠ 160; rect_mp0: h=100 ≠ 40; rectangl: w=100 ≠ 160; rectangl: h=100 ≠ 40; rectangl: w=100 ≠ 160; rectangl: h=100 ≠ 40`
  - fail: `rectangle gaps on x: min=-100.0 max=-90.0 (need min ≥ 4.0, variance ≤ 8.0)`
- **color**: 0.200/0.200 (3/3 checks pass)
- **property**: 0.100/0.100 (2/2 checks pass)
- **event**: 0.125/0.250 (1/2 checks pass)
  - fail: `event 'create_rectangle': expected 3, got 1`
- _verdict_: **verifier-primary** — Current 0.688; post-verifier-fix estimate 0.792 → would pass (lift +0.104); frame-fix alignment: +1 check

### `task_44_avatar_status` — plateau at 0.605 × 3 attempts

- **fundamentals**: 0.200/0.200 (1/1 checks pass)
- **alignment**: 0.069/0.200 (11/16 checks pass)
  - fail: `No frame at 1280×832 (±25.0px)`
  - fail: `Need both ellipse and frame layers`
- **color**: 0.036/0.200 (4/11 checks pass)
  - fail: `No ellipse with solid fill {'r': 0.06, 'g': 0.72, 'b': 0.5} (tol 0.28)`
  - fail: `No ellipse with stroke color {'r': 1.0, 'g': 1.0, 'b': 1.0}`
- **structure**: 0.100/0.200 (1/2 checks pass)
  - fail: `All 2 ellipse not direct children of a single frame`
- **event**: 0.200/0.200 (2/2 checks pass)
- _verdict_: **verifier-primary** — Current 0.605; post-verifier-fix estimate 0.823 → would pass (lift +0.218); frame-fix alignment: +1 check; unhalve color: 0.036->0.073; frame-fix structure: +1 check

### `task_46_audio_waveform` — plateau at 0.599 × 3 attempts

- **fundamentals**: 0.200/0.200 (1/1 checks pass)
- **alignment**: 0.064/0.200 (7/11 checks pass)
  - fail: `rectangle stacked on x (gap=4.0px): max deviation 34.0px (tolerance 12.0px)`
  - fail: `No frame at 1280×832 (±25.0px)`
- **color**: 0.160/0.200 (4/5 checks pass)
  - fail: `distinct solid colors: expected ≥2, got 1`
- **structure**: 0.050/0.200 (1/2 checks pass)
  - fail: `All 5 rectangle not direct children of a single frame`
- **event**: 0.200/0.200 (2/2 checks pass)
- _verdict_: **verifier-primary** — Current 0.674; post-verifier-fix estimate 0.905 → would pass (lift +0.232); frame-fix alignment: +1 check; frame-fix structure: +1 check

### `task_27_neumorphic_button` — plateau at 0.557 × 3 attempts

- **fundamentals**: 0.200/0.200 (1/1 checks pass)
- **alignment**: 0.057/0.200 (4/7 checks pass)
  - fail: `No rectangle with cornerRadius ≥ 16.0`
  - fail: `No frame layers found`
- **color**: 0.200/0.200 (2/2 checks pass)
- **effect**: 0.000/0.200 (0/4 checks pass)
  - fail: `No rectangle with drop shadow found`
  - fail: `1/1 rectangle have wrong effect count`
- **structure**: 0.000/0.100 (0/1 checks pass)
  - fail: `No rectangle found as direct child of a frame`
- **event**: 0.100/0.100 (2/2 checks pass)
- _verdict_: **verifier-primary** — Current 0.557; post-verifier-fix estimate 0.743 → would pass (lift +0.186); frame-fix alignment: +1 check; frame-fix structure: +1 check

### `task_38_battery_indicator` — plateau at 0.393 × 3 attempts

- **fundamentals**: 0.040/0.160 (2/4 checks pass)
  - fail: `rectangle: expected 5, got 1`
  - fail: `Need ≥2 rectangle layers, got 1`
- **alignment**: 0.022/0.180 (2/8 checks pass)
  - fail: `No rectangle with cornerRadius ≥ 4.0`
  - fail: `Need ≥2 rectangle layers, found 1`
- **color**: 0.040/0.180 (4/9 checks pass)
  - fail: `distinct solid colors: expected ≥4, got 1`
  - fail: `No rectangle with a stroke found`
- **structure**: 0.000/0.100 (0/1 checks pass)
  - fail: `No rectangle found as direct child of a frame`
- **event**: 0.090/0.180 (1/2 checks pass)
  - fail: `event 'create_rectangle': expected 5, got 1`
- **fundamentals**: 0.200/0.200 (1/1 checks pass)
- _verdict_: **model-primary** — Verifier fix would lift 0.393 → 0.617 (+0.225), still below 0.7 threshold — model is the bigger gap; unhalve fundamentals: 0.040->0.080; frame-fix alignment: +1 check; unhalve color: 0.040->0.080

### `task_18_donut` — plateau at 0.308 × 3 attempts

- **fundamentals**: 0.000/0.200 (0/2 checks pass)
  - fail: `ellipse: expected 3, got 1`
  - fail: `Total layers: expected 4, got 2`
- **alignment**: 0.033/0.200 (1/3 checks pass)
  - fail: `Need ≥2 ellipse layers, found 1`
  - fail: `Need exactly 3 ellipse, found 1`
- **color**: 0.060/0.200 (3/5 checks pass)
  - fail: `distinct solid colors: expected ≥3, got 1`
  - fail: `Need exactly 3 ellipse, found 1`
- **structure**: 0.114/0.200 (4/7 checks pass)
  - fail: `No ellipse found as direct child of a frame`
  - fail: `Found 1 ellipse (need ≥3)`
- **event**: 0.100/0.200 (1/2 checks pass)
  - fail: `event 'create_ellipse': expected 3, got 1`
- _verdict_: **model-primary** — Verifier fix would lift 0.308 → 0.430 (+0.122), still below 0.7 threshold — model is the bigger gap; unhalve alignment: 0.033->0.067; unhalve color: 0.060->0.120; frame-fix structure: +1 check

### `task_50_album_cover` — plateau at 0.304 × 3 attempts

- **fundamentals**: 0.042/0.250 (1/3 checks pass)
  - fail: `star: expected 1, got 0`
  - fail: `No star layers found`
- **alignment**: 0.054/0.250 (6/14 checks pass)
  - fail: `Need both star and rectangle layers`
  - fail: `Need both star and rectangle layers`
- **color**: 0.083/0.250 (4/6 checks pass)
  - fail: `No star layers found`
  - fail: `distinct solid colors: expected ≥2, got 1`
- **event**: 0.125/0.250 (2/4 checks pass)
  - fail: `tool 'star': never used`
  - fail: `event 'create_star': expected 1, got 0`
- _verdict_: **model-primary** — Verifier fix would lift 0.304 → 0.482 (+0.179), still below 0.7 threshold — model is the bigger gap; unhalve fundamentals: 0.042->0.083; unhalve alignment: 0.054->0.107; unhalve color: 0.083->0.167

### `task_22_tag_pills` — plateau at 0.301 × 3 attempts

- **fundamentals**: 0.000/0.200 (0/1 checks pass)
  - fail: `rectangle: expected 4, got 1`
- **alignment**: 0.018/0.250 (1/7 checks pass)
  - fail: `Need ≥2 rectangle layers, found 1`
  - fail: `Need ≥2 rectangle layers, found 1`
- **color**: 0.083/0.250 (2/3 checks pass)
  - fail: `distinct solid colors: expected ≥4, got 1`
- **property**: 0.100/0.100 (2/2 checks pass)
- **event**: 0.100/0.200 (1/2 checks pass)
  - fail: `event 'create_rectangle': expected 4, got 1`
- _verdict_: **model-primary** — Verifier fix would lift 0.301 → 0.438 (+0.137), still below 0.7 threshold — model is the bigger gap; frame-fix alignment: +1 check; unhalve color: 0.083->0.167

### `task_26_color_variable_card` — plateau at 0.299 × 3 attempts

- **fundamentals**: 0.000/0.200 (0/1 checks pass)
  - fail: `rectangle: expected 5, got 1`
- **alignment**: 0.042/0.250 (2/6 checks pass)
  - fail: `Need ≥2 rectangle layers, found 1`
  - fail: `Need ≥2 rectangle layers, found 1`
- **color**: 0.067/0.200 (2/3 checks pass)
  - fail: `distinct solid colors: expected ≥5, got 1`
- **property**: 0.150/0.150 (3/3 checks pass)
- **event**: 0.100/0.200 (1/2 checks pass)
  - fail: `event 'create_rectangle': expected 5, got 1`
- _verdict_: **model-primary** — Verifier fix would lift 0.358 → 0.508 (+0.150), still below 0.7 threshold — model is the bigger gap; frame-fix alignment: +1 check; unhalve color: 0.067->0.133

### `task_33_pie_chart` — plateau at 0.255 × 3 attempts

- **fundamentals**: 0.042/0.250 (1/3 checks pass)
  - fail: `polygon: expected 2, got 0`
  - fail: `No polygon layers found`
- **alignment**: 0.042/0.250 (3/9 checks pass)
  - fail: `Need both polygon and ellipse layers`
  - fail: `Need both polygon and ellipse layers`
- **color**: 0.047/0.250 (3/8 checks pass)
  - fail: `No polygon layers found`
  - fail: `No ellipse with solid fill {'r': 0.0, 'g': 0.6, 'b': 0.6} (tol 0.28)`
- **event**: 0.125/0.250 (2/4 checks pass)
  - fail: `tool 'polygon': never used`
  - fail: `event 'create_polygon': expected 2, got 0`
- _verdict_: **model-primary** — Verifier fix would lift 0.255 → 0.385 (+0.130), still below 0.7 threshold — model is the bigger gap; unhalve fundamentals: 0.042->0.083; unhalve alignment: 0.042->0.083; unhalve color: 0.047->0.094

## Top fix candidates

Ranked by estimated score lift × number of tasks affected. Patches are
scoped to verifier or mock files only (no agent-side changes).

### #1 — Remove or relax frame mandate (38 tasks affected)

Audit which tasks' prompts actually require a frame. For those that don't,
replace `AllLayerBoundsInside(outer_type="frame")` and `LayerInsideFrame(...)`
with optional checks (e.g. score 0 if not present but don't halve the rubric)
or remove entirely.

_Estimated lift_: ~0.10 per task on best score × 38 tasks affected.

### #2 — Raise sub-15px alignment tolerances (24 tasks affected)

Increase `LayersAligned(..., tolerance=...)` and `LayersConcentric(...)` from
12-15 px to 25-30 px on non-prompt-critical alignment. Keep strict tolerances
only when the prompt explicitly says "perfectly centered" or equivalent.

_Estimated lift_: ~0.05-0.15 per task × 24 tasks affected.

### #3 — Add effect partial credit (task_27 + others)

In `EffectRubric` for tasks like task_27, replace the 4 all-or-nothing checks
with graded credit: 0.025 for "any drop shadow exists," 0.025 for "≥ 2 shadows,"
0.025 for "shadows oppose," 0.025 for "shadows pair on offset." That way the
rubric can score 0.025-0.100 instead of locked at 0.0.

### #4 — Resolve hard-zero shape-type gaps (3 tasks)

For the 3 tasks scoring exact 0.0 across all attempts:
- `task_11_pressed_button` — verdict=`model-gap`
- `task_35_honeycomb` — verdict=`model-gap`
- `task_47_sunburst_badge` — verdict=`mock-gap`

Action depends on verdict:
- `model-gap` → real CUA capability gap; no harness change needed
- `mock-gap` → fix mock to log the missing shape type; expect score lift

## Methodology notes

- Verifier introspection uses Python's standard `dataclasses.asdict` on each
  check instance. Each check's class name + parameter dict is captured.
- `frame_required` is True iff any check is `LayerInsideFrame` or
  `AllLayerBoundsInside(outer_type="frame")`.
- `brittle_alignment_tolerance` is True iff any `Layers*` check has tolerance < 15.
- Rollout aggregation reads `merged_attempts.json` (the cross-run dedup).
- Log scan walks `outcome.document.pages[].children` recursively across all 4 runs.
- Verdict heuristic in `audit_verifiers.py:compute_verdict()`.

Per [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md), this audit does **not** modify any
`delivery-1/task_NN/verifier.py` or `prompt.md` files. Authorize specific patches
via follow-up if you want them applied.
