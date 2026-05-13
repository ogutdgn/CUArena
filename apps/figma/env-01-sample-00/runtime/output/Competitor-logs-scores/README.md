# Sonnet Rollout Overview

This folder contains Sonnet rollout artifacts grouped by task and run.

## How these runs were executed

- Environment: `docker compose up -d --build` from this delivery package.
- Tasks were run by opening `http://localhost:5173/?task=task_XX` and interacting with the canvas.
- Verifier re-score was run over each saved `log.json` in this folder with:
  - `docker compose run --rm --no-deps verifier python3 scripts/score_log.py --task task_XX --log /workspace/output/Competitor-logs-scores/task_XX/runs/<run_id>/log.json`

## Score comparison (original vs re-score)

| Task | Run | Original | Re-scored | Delta |
|---|---|---:|---:|---:|
| task_01 | trajectory_1_house_c | 1.0000 | 1.0000 | +0.0000 |
| task_02 | trajectory_2_sunset_c | 0.0937 | 0.0937 | +0.0000 |
| task_03 | trajectory_3_flower_cu | 0.7500 | 0.7500 | +0.0000 |
| task_04 | trajectory_4_squares_cu | 0.3750 | 0.3750 | +0.0000 |
| task_05 | trajectory_5_plus_cu | 1.0000 | 1.0000 | +0.0000 |
| task_07 | trajectory_7_mountain_c | 1.0000 | 1.0000 | +0.0000 |
| task_09 | trajectory_9_grid_cu | 0.5833 | 0.5833 | +0.0000 |
| task_10 | trajectory_10_nested_cu | 1.0000 | 1.0000 | +0.0000 |
| task_51 | trajectory_51_count_r | 1.0000 | 1.0000 | +0.0000 |
| task_52 | trajectory_52_gift_r | 1.0000 | 1.0000 | +0.0000 |
| task_53 | trajectory_53_red_d | 1.0000 | 1.0000 | +0.0000 |

## Aggregate

- Total runs rescored: 11
- Runs with score delta: 0
- Average delta: +0.0000
