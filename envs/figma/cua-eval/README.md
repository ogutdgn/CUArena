# CUA Eval — 50 Finished Tasks

Mouse-only Figma tasks for evaluating computer-use agents. **All 50 tasks
use only currently-shipped env features and are runnable end-to-end today.**

## Contents

```
cua-eval/
├── README.md                  ← this file
├── BUILDING_TASKS.md          ← step-by-step guide to add new tasks
└── figma_tasks_finished.csv   ← 50 in-scope tasks

delivery-1/
└── task_NN/                   ← per-task package: prompt.md + verifier.py + output/<ts>/
```

## All 50 tasks (runnable today)

| # | Task | Time | Difficulty |
|---|---|---|---|
| 01 | Two-story house | 10m | Easy |
| 02 | Sunset stripe band | 12m | Easy |
| 03 | Radial flower with petals | 14m | Easy |
| 04 | Color hexagon ring | 12m | Easy |
| 05 | Plus-sign emblem | 8m | Easy |
| 06 | Asterisk burst | 12m | Easy |
| 07 | Layered mountain range | 12m | Easy |
| 08 | Layered water waves | 15m | Easy |
| 09 | 12-color swatch grid | 16m | Easy |
| 10 | Concentric squares | 8m | Easy |
| 11 | Triangle pyramid stack | 8m | Easy |
| 12 | Card row | 8m | Easy |
| 13 | Cross-hatch hashtag | 8m | Easy |
| 14 | Concentric ring target | 10m | Easy |
| 15 | Cloud silhouette | 10m | Easy |
| 16 | Speech bubble visual | 10m | Easy |
| 17 | Hourglass shape | 10m | Easy |
| 18 | Eye icon | 8m | Easy |
| 19 | Padlock icon | 15m | Easy |
| 20 | 2 overlapping circles | 10m | Easy |
| 21 | Vertical icon column | 10m | Easy |
| 22 | Tag pill row | 10m | Easy |
| 23 | Sidebar layout | 8m | Easy |
| 24 | Centered modal panel | 10m | Easy |
| 25 | Identical button row | 8m | Easy |
| 26 | Brand color row | 10m | Easy |
| 27 | Neumorphic pressed-button | 12m | Easy |
| 28 | Photo placeholder X | 8m | Easy |
| 29 | 2x2 polka dot grid | 10m | Easy |
| 30 | Vertical stripe wallpaper | 10m | Easy |
| 31 | Sun rays burst | 15m | Medium |
| 32 | Pinwheel | 12m | Easy |
| 33 | Pie chart | 18m | Medium |
| 34 | 6-fold snowflake | 18m | Medium |
| 35 | 3x2 honeycomb | 18m | Medium |
| 36 | Vintage frame | 10m | Easy |
| 37 | Sticky note | 12m | Easy |
| 38 | Battery indicator | 12m | Easy |
| 39 | Wifi signal icon | 18m | Medium |
| 40 | iOS toggle switch | 10m | Easy |
| 41 | Search bar | 18m | Medium |
| 42 | Bell icon with badge | 18m | Medium |
| 43 | Compass rose | 18m | Medium |
| 44 | Avatar with badge | 10m | Easy |
| 45 | Geometric emblem | 10m | Easy |
| 46 | Histogram bars | 18m | Medium |
| 47 | Sunburst badge | 18m | Medium |
| 48 | Spiderweb pattern | 18m | Medium |
| 49 | Tied ribbon | 18m | Medium |
| 50 | Star inside square | 10m | Easy |

**Total**: 50 tasks. Average time per task: ~12 min. Total estimated time: ~10 hours of mouse-only work.

## Verifier approach

Every task uses the same 5-rubric pattern from `house_task_comprehensive.py`:

  - **Fundamentals** — shape primitive counts (`ShapeCount`)
  - **Alignment** — geometric relationships (`LayersAligned`, `LayersSameDimensions`, etc.)
  - **Color** — fill type checks (`FillTypeIs(kind="solid")`)
  - **Event** — action-log events (`ToolUsed`, `EventTypeCount`)

Plus an **EfficiencyRubric** multiplier based on turn count.

Each rubric is wrapped in `WeightedRubric` to normalize the total max score
to **1.0** regardless of how many rubrics a task uses. See `BUILDING_TASKS.md`
for the full template and check catalog.

## Running

```bash
# One-time setup (from apps/figma/)
python3 -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # .venv/bin/pip on Unix

# Score an existing log against any task (numeric prefix or task_NN)
.venv/Scripts/python scripts/score_log.py --task 19 --log scripts/logs/<your_run>.json
.venv/Scripts/python scripts/score_log.py --task task_29 --log scripts/logs/<your_run>.json

# Or full pipeline: live log + score (requires mock running on :5173)
.venv/Scripts/python scripts/run_task.py task_19
```

Each run produces a per-rubric breakdown plus a final score in `[0, 1]`.

## Status

Branch: `cua-eval-50-ready`

- ✅ 50 tasks fully verifiable today (no `# BLOCKED` scaffolds)
- ✅ Reference verifier (`house_task_comprehensive.py`)
- ✅ Builder guide (`BUILDING_TASKS.md`)
- ⏳ Sample logs for each task
