# CUA Eval — Tasks + Verifier Approach (WIP)

Mouse-only Figma tasks for evaluating computer-use agents, plus the verifier
pattern used to score agent runs.

## Contents

```
cua-eval/
├── README.md              ← this file
└── figma_tasks_WIP.csv    ← 50 tasks (Easy/Medium, 8–25 min each)

test-verifier/tasks/
└── house_task_comprehensive.py  ← reference verifier (Task 1)
```

The CSV lives here. The runnable verifier code lives in `test-verifier/tasks/`
because it imports from the cofounder's verifier framework
(`test-verifier/verifier/`).

## CSV format

`figma_tasks_WIP.csv` — 50 rows, 5 columns:

| Column | Purpose |
|---|---|
| `Difficulty` | `Easy` or `Medium` |
| `Thorough Description` | Full goal-style spec for the task author |
| `Simplified Prompt` | One-line natural prompt fed to the agent |
| `Time (minutes)` | Time horizon for a new mouse-only user |
| `Step-by-step` | Numbered atomic mouse actions (one per discrete log event) |

Tasks are constrained to mouse-only operations (no keyboard shortcuts, no
typed text). Step counts: 7–17 steps per task. Total estimated human time
across all 50 tasks: ~14 hours.

## Verifier approach

Two-layer scoring per task:

  - **End-state** — inspects `outcome.document` (the layer tree the env
    emits at session end). Catches "did the agent achieve the goal?"
  - **Action-log** — inspects `semantic` events (the agent's mouse trace).
    Catches "did the agent use the right features?"

Both layers compose into a single normalized score in `[0, 1]`.

## Reference verifier — Task 1 (two-story house)

`test-verifier/tasks/house_task_comprehensive.py` demonstrates the pattern:
five rubrics, each weighted to 0.2 (sum = 1.0), multiplied by an efficiency
factor based on turn count.

| Rubric | Source | Weight | Checks |
|---|---|---|---|
| Fundamentals | end-state | 0.2 | shape primitive counts (2 rect, 2 ellipse, 1 polygon) |
| Alignment | end-state | 0.2 | windows aligned/symmetric/same-size, roof on body |
| Color | end-state | 0.2 | fill types are solid + ≥4 distinct colors used |
| Structure | end-state | 0.2 | shapes inside a frame, frame has ≥5 children |
| Event | action-log | 0.2 | rectangle/ellipse/polygon tools used, correct create_* events |
| Efficiency | action-log | × | turn-count multiplier (target 30, range 0.5–1.0) |

Final score = `sum(rubric.score)` × `efficiency.multiplier`, capped at 1.0.

### Why this shape

- **Each rubric is independent** — failing one doesn't poison the others
- **Weights sum to 1.0** — easy to interpret, easy to reweight
- **Mixed signals** — end-state catches outcome, action-log catches process
- **Efficiency multiplier** — penalizes wasteful runs without binary failure

### The `WeightedRubric` wrapper

The cofounder's framework has each rubric natively at `max_score = 0.5`, so a
5-rubric task would max at 2.5. To normalize to 1.0, the comprehensive task
file defines a `WeightedRubric` wrapper that rescales any rubric's output:

```python
@dataclass
class WeightedRubric:
    rubric: Any           # any object with .run(log) -> RubricResult
    max_score: float      # the desired max for this slot

    def run(self, log):
        r = self.rubric.run(log)
        scale = self.max_score / r.max_score if r.max_score else 1.0
        return RubricResult(
            name=r.name,
            score=round(r.score * scale, 4),
            max_score=self.max_score,
            checks=r.checks,
        )
```

Wrap each rubric in `WeightedRubric(..., max_score=0.2)` and the task's base
score is naturally bounded at 1.0 without modifying any framework files.

### Custom checks

The framework's check library is rich (see
`test-verifier/verifier/checks/`), but tasks can define inline checks for
gaps. The comprehensive verifier adds one — `DistinctSolidColors` — that
counts perceptually-distinct solid fills across the document.

## Running

From the repo root:

```bash
cd test-verifier
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py --task house_task_comprehensive --log logs/house_sample.json
```

(Requires Python 3.10+.)

## Extending to the other 49 tasks

Each task in the CSV becomes a `tasks/<task_id>.py` file using the same
`WeightedRubric(..., max_score=0.2)` pattern. The five rubric categories
generalize:

- **Fundamentals** — the right shape primitives in the right counts
- **Alignment / Geometry** — task-specific spatial relationships
- **Color** — fill types and color variety where relevant
- **Structure** — frame containment, grouping, layer organization
- **Event** — which tools and creation events should appear in the log

Tasks that don't need a rubric (e.g., a single-shape task may not need
`Structure`) can either set its weight to 0.0 or omit it and redistribute
the remaining weights to sum to 1.0.

## Building a new task

See [`BUILDING_TASKS.md`](./BUILDING_TASKS.md) for the full step-by-step
guide: CSV row format, verifier file template, the 5-rubric system, the
check catalog, and a worked example walking through Task 1 end-to-end.

## Status

Branch: `cua-eval-wip`

- ✅ 50 tasks in CSV
- ✅ Reference verifier (Task 1) using comprehensive 5-rubric pattern
- ✅ Builder guide (`BUILDING_TASKS.md`)
- ⏳ Verifiers for tasks 2–50 (next)
- ⏳ Sample logs for each task
