# test-verifier

Outcome-based verifier framework for evaluating CUA (Computer Use Agent) runs against the Figma mock app.

The verifier reads the log produced by the app after an agent finishes a task and scores how well the task was completed — what ended up on the canvas, not how the agent got there.

---

## How it works

```
task prompt → agent interacts with figma-mock → export log → run verifier → score
```

**Scoring:**
- Each task defines a set of **rubrics** (e.g. Fundamentals, Alignment). Each rubric scores 0–0.5.
- All rubric scores are summed into a `base_score`.
- An **efficiency multiplier** (0.5–1.0) scales the base score based on how many semantic events the agent used vs. the target turn count.
- `final_score = base_score × multiplier`

---

## Setup

```bash
cd test-verifier
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

---

## Running a verifier

```bash
.venv/bin/python run.py --task house_task --log logs/house_sample.json
```

Save result to JSON:

```bash
.venv/bin/python run.py --task house_task --log logs/house_sample.json --output scores/result.json
```

Example output:

```
Task : house_task
Log  : logs/house_sample.json
────────────────────────────────────────────────────────
  fundamentals     0.5000 / 0.5   (100%)
    ✓ polygon: expected 1, got 1
    ✓ ellipse: expected 2, got 2
    ✓ rectangle: expected 2, got 2
  alignment        0.3750 / 0.5   (75%)
    ✓ ellipse aligned on center_y: max diff 0.0px (tolerance 8.0px)
    ✓ All ellipse same size (72×63)
    ✓ ellipse symmetric on X: max deviation 0.0px (tolerance 15.0px)
    ✗ No polygon.bottom aligns with any rectangle.top (tolerance 10.0px)
────────────────────────────────────────────────────────
  base_score       0.8750 / 1.0
  efficiency       ×0.7362  (45 turns used, target 30, λ=0.05 → multiplier 0.7362)
  FINAL            0.6442 / 1.0
```

---

## Exporting a log from the app

The app must be running in dev mode. After completing a task, open the browser console and run:

```javascript
__exportLog()
```

This downloads a single `figma-mock-log-<sessionId>.json` file containing all three streams (`raw`, `semantic`, `outcome`). Place it in `logs/` and pass it to `run.py`.

> **`logs/house_sample.json`** is a real log exported from the app — a human completed the house task (1 polygon, 2 ellipses, 2 rectangles) using the actual Figma mock interface.

---

## Adding a new task verifier

1. Find the task in `task-docs/tasks.csv` (filter `Scope = in_scope`)
2. Ask Claude Code: *"write the verifier for `<task_id>` from tasks.csv"*
3. Claude Code reads `CLAUDE.md` / `AGENTS.md` and writes `tasks/<task_id>.py`
4. Run it against a log

See `CLAUDE.md` (or `AGENTS.md`) for the full check primitive catalog and rules.

---

## Structure

```
test-verifier/
├── verifier/
│   ├── checks/        ← 10 check categories (shape, geometry, fill, stroke, ...)
│   └── rubrics/       ← 10 rubric types + efficiency multiplier
├── tasks/             ← one .py file per task
├── task-docs/
│   └── tasks.csv      ← 50 tasks (23 in_scope, 5 planned, 22 out_of_scope)
├── logs/              ← log JSON files from the app
├── scores/            ← verifier output (git-ignored)
├── run.py             ← CLI
├── config.yaml        ← λ and tolerance defaults
└── CLAUDE.md          ← instructions for writing task verifiers
```
