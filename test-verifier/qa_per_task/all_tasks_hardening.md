# All-tasks hardening pass

Applied the `reinforce-verifier` skill across tasks 02–50 (49 tasks) to bring them in line with task_01's hardening level.

## What was applied universally

### 1. Bulk primitive swaps
- **`FillTypeIs("X", "solid")` → `AllFillTypeIs("X", "solid")`** in 42 task files. Catches "1 of N layers has a solid fill, the rest don't" — the most common false-positive pattern.
- **`LayerBoundsInside(X, X)` → `SmallerLayerInsideLarger(X)`** in 5 task files (task_10, 11, 14, 18, 36). Eliminates the trivial-self-containment bug (`body fits inside body`).

### 2. Critical-flag pass (5 parallel agents, 49 tasks)
Each agent read `delivery-1/task_NN/prompt.md`, identified prompt-explicit requirements, and added `critical=[indices]` to the relevant rubrics. Density: 30–80% of checks per rubric flagged critical (per-task variance based on prompt strictness).

Anti-patterns avoided:
- Did NOT flag exact `EventTypeCount` (legitimate variance with extra create+delete events).
- Did NOT flag every check (defeats the halving mechanism).
- Did NOT flag color/stroke checks where the prompt was loose (e.g., task_29 "same color (or all different)").

### 3. Rubric factory updates
All 9 rubric factories (`fundamentals`, `alignment`, `color`, `effect`, `event`, `page`, `property`, `structure`, `text`) now accept `critical=` parameter, mirroring the existing `_base.Rubric.run()` halving logic.

### 4. Harness handlers added/extended (qa_verifiers.py)
To keep the synthetic perfect log scoring 1.000 across all 50 tasks:
- `LayersAligned` — aligns same-type layers on the requested axis.
- `LayersStacked` (re-run in final pass) — re-stacks after sizing.
- `LayerAspectRatioGreaterThan` (re-run in final pass) — re-applies aspect after width-fraction sizing.
- `LayerSizeEquals` — sets exact dimensions in the final pass.
- `PolygonSidesEquals` / `StarPointsEquals` — sets shape-specific properties.
- `SmallerLayerInsideLarger` — branches between concentric (center-aligned) and door-on-body (bottom-aligned + x-centered) based on whether `LayersConcentric` is also required for the same type.

## Per-task task-specific fixes

| Task | Issue | Fix |
|------|-------|-----|
| task_32 | `LayersAlternatingColors(sort_axis="x")` doesn't fit radial pinwheel — two blades share same x | Removed from critical (kept for partial credit) |

## Final state

```
Harness:     50 OK | 0 STRICT | 0 LENIENT | 0 CRASH | total 50
Per-task:    50/50 batteries report 0 bug(s)
Perfect-log: 1.000 across all 50 tasks
Empty-log:   0.000 across all 50 tasks
```

All 50 task verifiers now use critical-fail halving on prompt-explicit requirements. Agent-driven false positives that previously scored 1.0 will now drop to ~0.85–0.90 per failed critical check, surfacing real defects.

## Recommended follow-up

The universal hardening only marks **existing checks** critical. Per-task **deep hardening** (round-3-style novel edge cases per the skill methodology) is still pending for tasks 02–50. Each task likely has 5–10 task-specific FPs that would require new primitives. Sequential or batch-parallel approach via the `reinforce-verifier` skill recommended.
