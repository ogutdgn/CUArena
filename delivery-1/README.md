# Delivery 1 — Figma CUA Eval (50 tasks)

Per-task package: each `task_NN/` folder below contains the full
prompt and the verifier script as separate files:

```
task_NN/
  prompt.md     — difficulty, thorough description, simplified prompt, step-by-step
  verifier.py   — the matching verifier from test-verifier/tasks/
```

## Running a verifier

The verifier files in this delivery are READ-ONLY copies for review.
To actually score an agent run, use the framework at `test-verifier/`:

```bash
# 1. Generate the agent log via the test-app (dev mode)
cd test-app && npm run dev      # http://localhost:5173
# (run the task in the browser, then export the log)
python3 scripts/run_task.py --task <module_name>

# 2. Or score an existing log directly
cd test-verifier
PYTHONPATH=. python3 run.py --task <module_name> --log logs/<log>.json

# 3. Smoke-test every verifier against synthetic perfect/empty logs
cd test-verifier
PYTHONPATH=. python3 qa_verifiers.py
```

The `<module_name>` for each task is shown in the index table below
(it matches the original filename in `test-verifier/tasks/`).

## Index

| # | Difficulty | Time | Task | Module |
|---|---|---|---|---|
| 01 | Easy | 10 min | [Build a simple house inside a MacBook Air frame with a body, triangle roof, door, and 2 round windows.](task_01/prompt.md) | `task_01_house_task_comprehensive` |
| 02 | Easy | 12 min | [Stack 5 horizontal rectangle bands in sunset colors (purple, pink, orange, yellow, pale yellow).](task_02/prompt.md) | `task_02_sunset_gradient` |
| 03 | Easy | 14 min | [Draw a yellow center circle and 8 colored petals arranged radially around it.](task_03/prompt.md) | `task_03_glowing_orb` |
| 04 | Easy | 12 min | [Arrange 6 same-size squares in a hexagonal ring with rainbow colors.](task_04/prompt.md) | `task_04_color_wheel` |
| 05 | Easy | 8 min | [Build a plus sign from 2 perpendicular rectangles centered together.](task_05/prompt.md) | `task_05_red_heart_union` |
| 06 | Easy | 12 min | [Draw 8 lines from a center point at 45° intervals to form a burst.](task_06/prompt.md) | `task_06_gold_star_exclude` |
| 07 | Easy | 12 min | [Make a layered gray mountain range using two overlapping pen-tool paths in different shades.](task_07/prompt.md) | `task_07_mountain_range` |
| 08 | Easy | 15 min | [Make two layered water waves drawn with smooth Bezier curves in different blue shades.](task_08/prompt.md) | `task_08_water_waves` |
| 09 | Easy | 16 min | [Arrange 12 same-size colored squares in a 4x3 grid using Tidy up.](task_09/prompt.md) | `task_09_brand_palette` |
| 10 | Easy | 8 min | [Make 4 nested squares with shared center, alternating two colors.](task_10/prompt.md) | `task_10_apple_avatar` |
| 11 | Easy | 8 min | [Make 3 nested triangles with the same center, alternating two colors.](task_11/prompt.md) | `task_11_pressed_button` |
| 12 | Easy | 8 min | [Arrange 4 same-size rectangles in a horizontal row with consistent spacing.](task_12/prompt.md) | `task_12_shadowed_cards` |
| 13 | Easy | 8 min | [Draw 4 lines (2 vertical + 2 horizontal) forming a hashtag (#) shape.](task_13/prompt.md) | `task_13_night_sky` |
| 14 | Easy | 10 min | [Make a dartboard target with 4 concentric red and white circles, centered, each with a 4px black stroke.](task_14/prompt.md) | `task_14_concentric_target` |
| 15 | Easy | 10 min | [Draw 4 overlapping white ellipses forming a cloud silhouette.](task_15/prompt.md) | `task_15_cloud_union` |
| 16 | Easy | 10 min | [Draw a speech bubble: rounded rectangle + small triangle tail at bottom-left.](task_16/prompt.md) | `task_16_speech_bubble` |
| 17 | Easy | 10 min | [Build an hourglass: 2 triangles point-to-point + 2 horizontal cap rectangles.](task_17/prompt.md) | `task_17_play_button` |
| 18 | Easy | 8 min | [Draw an eye icon: 3 nested ellipses (sclera, iris, pupil) sharing a center.](task_18/prompt.md) | `task_18_donut` |
| 19 | Easy | 15 min | [Build a padlock with a rectangle body, a pen-tool U-shackle, and a keyhole.](task_19/prompt.md) | `task_19_padlock` |
| 20 | Easy | 10 min | [Draw 2 overlapping bright-colored circles inside a dark navy frame.](task_20/prompt.md) | `task_20_glow_blob` |
| 21 | Easy | 10 min | [Stack 3 same-size rectangles vertically, different colors, aligned on x.](task_21/prompt.md) | `task_21_button_stack` |
| 22 | Easy | 10 min | [Draw 4 same-size pill rectangles in a horizontal row with different pastel fills.](task_22/prompt.md) | `task_22_tag_pills` |
| 23 | Easy | 8 min | [Draw a left sidebar rectangle inside an outer frame.](task_23/prompt.md) | `task_23_stretchy_sidebar` |
| 24 | Easy | 10 min | [Draw a centered modal rectangle inside an outer frame using align tool.](task_24/prompt.md) | `task_24_centered_modal` |
| 25 | Easy | 8 min | [Draw 3 identical rectangles in a horizontal row with consistent spacing.](task_25/prompt.md) | `task_25_button_component` |
| 26 | Easy | 10 min | [Draw 5 same-size squares in a row with brand colors.](task_26/prompt.md) | `task_26_color_variable_card` |
| 27 | Easy | 12 min | [Draw 3 same-size squares centered together, rotated to different angles.](task_27/prompt.md) | `task_27_neumorphic_button` |
| 28 | Easy | 8 min | [Draw a photo-placeholder rectangle with two diagonal lines forming an X.](task_28/prompt.md) | `task_28_edited_photo` |
| 29 | Easy | 10 min | [Draw a 2x2 polka dot grid using Tidy up to align 4 circles.](task_29/prompt.md) | `task_29_polka_dot_grid` |
| 30 | Easy | 10 min | [Draw 6 alternating vertical stripes filling a 600x600 frame.](task_30/prompt.md) | `task_30_stripe_wallpaper` |
| 31 | Medium | 15 min | [Draw a sun: yellow circle + 8 triangle rays rotated radially around it.](task_31/prompt.md) | `task_31_sun_rays` |
| 32 | Easy | 12 min | [Draw a pinwheel: 4 triangles + small center circle, alternating colors.](task_32/prompt.md) | `task_32_pinwheel` |
| 33 | Medium | 18 min | [Draw a 4-section pie chart with a base circle and 3 colored wedge triangles.](task_33/prompt.md) | `task_33_pie_chart` |
| 34 | Medium | 18 min | [Make a 6-fold symmetric snowflake by duplicating one branch group and rotating 60° five times.](task_34/prompt.md) | `task_34_snowflake` |
| 35 | Medium | 18 min | [Make a 3x2 honeycomb pattern of 6 yellow hexagons.](task_35/prompt.md) | `task_35_honeycomb` |
| 36 | Easy | 10 min | [Draw a vintage frame: outer rectangle + smaller inner rectangle, both centered.](task_36/prompt.md) | `task_36_polaroid` |
| 37 | Easy | 12 min | [Draw a tilted yellow sticky note with a folded corner and 3 note lines.](task_37/prompt.md) | `task_37_sticky_note` |
| 38 | Easy | 12 min | [Build a battery indicator with body, terminal, and 3 inner level bars.](task_38/prompt.md) | `task_38_battery_indicator` |
| 39 | Medium | 18 min | [Build a wifi icon: 3 pen-tool arcs + small filled circle below.](task_39/prompt.md) | `task_39_wifi_icon` |
| 40 | Easy | 10 min | [Build an iOS green toggle switch with a white circle thumb on the right.](task_40/prompt.md) | `task_40_toggle_switch` |
| 41 | Medium | 18 min | [Build a search bar: rounded rectangle + magnifying-glass icon + 2 dots.](task_41/prompt.md) | `task_41_search_bar` |
| 42 | Medium | 18 min | [Build a yellow-gold bell icon + small clapper + red badge.](task_42/prompt.md) | `task_42_bell_icon` |
| 43 | Medium | 18 min | [Build a compass rose: sand circle + 4 N/E/S/W triangles + gold center.](task_43/prompt.md) | `task_43_compass_rose` |
| 44 | Easy | 10 min | [Draw an avatar circle + a small status badge circle at bottom-right.](task_44/prompt.md) | `task_44_avatar_status` |
| 45 | Easy | 10 min | [Build an emblem: 8-point blue star + smaller centered yellow circle.](task_45/prompt.md) | `task_45_geometric_emblem` |
| 46 | Medium | 18 min | [Draw 8 vertical rectangles of varying heights sharing a bottom baseline.](task_46/prompt.md) | `task_46_audio_waveform` |
| 47 | Medium | 18 min | [Build a sunburst stamp: 16-point star + smaller centered cream circle.](task_47/prompt.md) | `task_47_sunburst_badge` |
| 48 | Medium | 18 min | [Make a white spiderweb on a navy frame: 6 radial lines + 3 concentric hexagons.](task_48/prompt.md) | `task_48_spiderweb` |
| 49 | Medium | 18 min | [Draw a single S-curve ribbon using the Pen tool with a solid fill.](task_49/prompt.md) | `task_49_decorative_ribbon` |
| 50 | Easy | 10 min | [Draw a square with a centered 5-point star on top, contrasting colors.](task_50/prompt.md) | `task_50_album_cover` |
