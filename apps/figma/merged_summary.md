# Merged Run Summary

- **Sources:** qwen35_parallel_10x_20260510_144617, qwen35_fillin_20260510_155010, qwen35_fillin2_20260510_163353, qwen35_fillin3_20260510_170851
- **Total attempts merged:** 150
- **Tasks seen:** 50 / 50
- **Tasks with k=3 complete:** 50

## Headline

| Metric | Value |
|---|---|
| pass@1 | **6.7%** (10/150) |
| pass@3 (tasks ≥1 pass / all tasks seen) | **10.0%** (5/50) |
| pass@3 (only tasks with all 3 attempts) | **10.0%** (5/50) |
| mean score | 0.269 |
| nonzero scores | 141/150 (94%) |
| partial ≥0.1 | 109/150 (73%) |
| total cost (est.) | $34.97 |

## Passing tasks

| Task | Best score | Turns | Attempts passing |
|---|---|---|---|
| `task_05_red_heart_union` | 1.000 | 5 | 2/3 |
| `task_24_centered_modal` | 0.700 | 29 | 1/3 |
| `task_25_button_component` | 0.719 | 200 | 3/3 |
| `task_28_edited_photo` | 0.860 | 9 | 2/3 |
| `task_36_polaroid` | 0.825 | 200 | 2/3 |

## Top partial-credit (non-passing) tasks

| Task | Best score | Turns |
|---|---|---|
| `task_44_avatar_status` | 0.694 | 36 |
| `task_49_decorative_ribbon` | 0.688 | 200 |
| `task_27_neumorphic_button` | 0.680 | 29 |
| `task_23_stretchy_sidebar` | 0.635 | 200 |
| `task_46_audio_waveform` | 0.605 | 12 |
| `task_38_battery_indicator` | 0.500 | 29 |
| `task_40_toggle_switch` | 0.465 | 29 |
| `task_31_sun_rays` | 0.417 | 28 |
| `task_12_shadowed_cards` | 0.367 | 27 |
| `task_18_donut` | 0.343 | 28 |
| `task_29_polka_dot_grid` | 0.328 | 30 |
| `task_13_night_sky` | 0.325 | 29 |
| `task_19_padlock` | 0.322 | 200 |
| `task_26_color_variable_card` | 0.306 | 25 |
| `task_22_tag_pills` | 0.304 | 26 |

## Per-task detail

| Task | k | Best | Mean | Passed (k of n) |
|---|---|---|---|---|
| `house_task_comprehensive` | 3 | 0.065 | 0.024 | 0/3 |
| `task_02_sunset_gradient` | 3 | 0.125 | 0.072 | 0/3 |
| `task_03_glowing_orb` | 3 | 0.050 | 0.042 | 0/3 |
| `task_04_color_wheel` | 3 | 0.150 | 0.131 | 0/3 |
| `task_05_red_heart_union` | 3 | 1.000 | 0.849 | 2/3 |
| `task_06_gold_star_exclude` | 3 | 0.150 | 0.150 | 0/3 |
| `task_07_mountain_range` | 3 | 0.250 | 0.183 | 0/3 |
| `task_08_water_waves` | 3 | 0.138 | 0.079 | 0/3 |
| `task_09_brand_palette` | 3 | 0.300 | 0.233 | 0/3 |
| `task_10_apple_avatar` | 3 | 0.039 | 0.039 | 0/3 |
| `task_11_pressed_button` | 3 | 0.000 | 0.000 | 0/3 |
| `task_12_shadowed_cards` | 3 | 0.367 | 0.306 | 0/3 |
| `task_13_night_sky` | 3 | 0.325 | 0.267 | 0/3 |
| `task_14_concentric_target` | 3 | 0.103 | 0.103 | 0/3 |
| `task_15_cloud_union` | 3 | 0.189 | 0.189 | 0/3 |
| `task_16_speech_bubble` | 3 | 0.099 | 0.099 | 0/3 |
| `task_17_play_button` | 3 | 0.025 | 0.022 | 0/3 |
| `task_18_donut` | 3 | 0.343 | 0.343 | 0/3 |
| `task_19_padlock` | 3 | 0.322 | 0.249 | 0/3 |
| `task_20_glow_blob` | 3 | 0.182 | 0.175 | 0/3 |
| `task_21_button_stack` | 3 | 0.301 | 0.301 | 0/3 |
| `task_22_tag_pills` | 3 | 0.304 | 0.304 | 0/3 |
| `task_23_stretchy_sidebar` | 3 | 0.635 | 0.334 | 0/3 |
| `task_24_centered_modal` | 3 | 0.700 | 0.487 | 1/3 |
| `task_25_button_component` | 3 | 0.719 | 0.719 | 3/3 |
| `task_26_color_variable_card` | 3 | 0.306 | 0.304 | 0/3 |
| `task_27_neumorphic_button` | 3 | 0.680 | 0.680 | 0/3 |
| `task_28_edited_photo` | 3 | 0.860 | 0.743 | 2/3 |
| `task_29_polka_dot_grid` | 3 | 0.328 | 0.217 | 0/3 |
| `task_30_stripe_wallpaper` | 3 | 0.255 | 0.242 | 0/3 |
| `task_31_sun_rays` | 3 | 0.417 | 0.292 | 0/3 |
| `task_32_pinwheel` | 3 | 0.050 | 0.050 | 0/3 |
| `task_33_pie_chart` | 3 | 0.255 | 0.255 | 0/3 |
| `task_34_snowflake` | 3 | 0.289 | 0.163 | 0/3 |
| `task_35_honeycomb` | 3 | 0.000 | 0.000 | 0/3 |
| `task_36_polaroid` | 3 | 0.825 | 0.743 | 2/3 |
| `task_37_sticky_note` | 3 | 0.200 | 0.178 | 0/3 |
| `task_38_battery_indicator` | 3 | 0.500 | 0.500 | 0/3 |
| `task_39_wifi_icon` | 3 | 0.129 | 0.100 | 0/3 |
| `task_40_toggle_switch` | 3 | 0.465 | 0.461 | 0/3 |
| `task_41_search_bar` | 3 | 0.279 | 0.279 | 0/3 |
| `task_42_bell_icon` | 3 | 0.187 | 0.156 | 0/3 |
| `task_43_compass_rose` | 3 | 0.174 | 0.174 | 0/3 |
| `task_44_avatar_status` | 3 | 0.694 | 0.668 | 0/3 |
| `task_45_geometric_emblem` | 3 | 0.007 | 0.007 | 0/3 |
| `task_46_audio_waveform` | 3 | 0.605 | 0.580 | 0/3 |
| `task_47_sunburst_badge` | 3 | 0.000 | 0.000 | 0/3 |
| `task_48_spiderweb` | 3 | 0.121 | 0.081 | 0/3 |
| `task_49_decorative_ribbon` | 3 | 0.688 | 0.576 | 0/3 |
| `task_50_album_cover` | 3 | 0.304 | 0.304 | 0/3 |