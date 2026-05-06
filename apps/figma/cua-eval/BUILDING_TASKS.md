# Building a Task — Step by Step

How to add a new task to the eval set, from blank page to runnable verifier.

A complete task is two artifacts:

| Artifact | Where it lives | Purpose |
|---|---|---|
| **CSV row** | `cua-eval/figma_tasks_WIP.csv` | Task spec: prompt the agent sees + step-by-step + time horizon |
| **Verifier file** | `verifier/tasks/<task_name>.py` | Python file that scores agent runs |

The agent only ever sees the CSV's `Simplified Prompt` column. Everything else is for us: design context, time-budgeting, and verifier construction.

---

## Step 1 — Design the task

Pick a recognizable visual outcome that meets these constraints:

- **Mouse-only**: no keyboard typing, no shortcuts (modifier keys during clicks are fine)
- **Time horizon**: 8–25 minutes for a new user; 3–8 atomic actions per logical step
- **Single deliverable**: one clear visual artifact, not a multi-frame design
- **Tests something specific**: a tool, a feature, a geometric relationship, a pattern

Good task examples:
- "Build a 3-section pie chart by intersecting wedges with a circle"
- "Make a polka-dot pattern with 9 circles arranged in a 3×3 grid"
- "Build a glassmorphism card with backdrop blur over a colorful background"

Bad task examples (skip these):
- "Build a complete design system" (too big)
- "Make something pretty" (no objective verifier)
- "Create a button with a hover state" (requires keyboard for variant naming)

---

## Step 2 — Write the CSV row

Add one row to `cua-eval/figma_tasks_WIP.csv` with these 5 columns:

```csv
"Difficulty","Thorough Description","Simplified Prompt","Time (minutes)","Step-by-step"
"Medium","Use the Frame tool... [full spec]","Make a sunset sky as...",12,"1. Click Frame tool\n2. ..."
```

| Column | Rules |
|---|---|
| `Difficulty` | `Easy` (8–15 min) or `Medium` (15–25 min) |
| `Thorough Description` | Full English spec including dimensions, colors, what each shape is. Used for verifier construction. |
| `Simplified Prompt` | One sentence. Names the tools and end-state but no recipe. This is what the agent sees. |
| `Time (minutes)` | Estimate for a new mouse-only user. Used to set efficiency target later. |
| `Step-by-step` | Numbered atomic mouse actions. Each step = one discrete log event. Used as ground truth when choosing checks. |

Format guide for `Step-by-step`:
- One action per line, numbered
- "Click X tool" / "Drag to draw Y" / "Click Z and pick color"
- Right-click menu actions: "Right-click X, click Duplicate"
- Numerical scrubs: "Scrub corner radius to 16"
- No keyboard typing; for renames, write "(skip — keyboard required)"

---

## Step 3 — Plan the verifier

Decide which of the 5 rubrics apply:

| Rubric | What it checks | When to include |
|---|---|---|
| **Fundamentals** | Shape primitive counts | Almost always — what shapes should exist? |
| **Alignment** | Geometric relationships | When position/spacing matters (alignment, symmetry, overlap) |
| **Color** | Fill types + color variety | When the task asks for specific colors or palette diversity |
| **Structure** | Frame containment, grouping | When task requires a frame, group, or nested layout |
| **Event** | Action-log: tools + creation events | Almost always — proves the agent used the right tools |

Plus the **Efficiency** multiplier (always include, set `target_turns` from your time estimate).

Then for each included rubric, list the specific checks:

```
Task: Pie chart
Fundamentals: ShapeCount("ellipse", equals=1), ShapeCount("polygon", equals=3)
Alignment:    LayersAligned(layer_type="polygon", axis="center_x", tolerance=10)  # all wedges centered
Color:        DistinctSolidColors(minimum=4, tolerance=0.05)                       # 4 different colors
Event:        ToolUsed("ellipse"), ToolUsed("polygon"),
              EventTypeCount("create_polygon", equals=3),
              EventTypeCount("boolean_op", equals=3)  # 3 intersect operations
Efficiency:   target_turns = time_minutes * 2.5  → 22 minutes × 2.5 ≈ 55 turns
```

If you only need 4 rubrics, set each `max_score=0.25` instead of `0.20`. If 3 rubrics, `0.33`. Always sum to 1.0.

---

## Step 4 — Write the verifier file

Copy the template into `verifier/tasks/<task_name>.py`:

```python
"""
Task NN — <name>
"""
from dataclasses import dataclass
from typing import Any
from verifier.types  import Task, CheckResult, RubricResult
from verifier.math_utils import find_all_layers

from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric

# Import only the checks you actually use
from verifier.checks.shape_checks    import ShapeCount
from verifier.checks.event_checks    import ToolUsed, EventTypeCount
# ...


# ── WeightedRubric — same in every task ─────────────────────────────
@dataclass
class WeightedRubric:
    rubric: Any
    max_score: float
    def run(self, log):
        r = self.rubric.run(log)
        scale = self.max_score / r.max_score if r.max_score else 1.0
        return RubricResult(name=r.name, score=round(r.score * scale, 4),
                            max_score=self.max_score, checks=r.checks)


# ── (Optional) Custom checks for gaps in the library ────────────────
# Define inline if a single check is needed; contribute back to
# verifier/checks/ if the check is reusable across tasks.


# ── Task definition ─────────────────────────────────────────────────
task = Task(
    id="<task_name>",
    description="<plain-English goal>",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            # ShapeCount(...) entries
        ]), max_score=0.2),

        WeightedRubric(AlignmentRubric([
            # LayersAligned, LayersSymmetricX, LayerEdgesAligned, ...
        ]), max_score=0.2),

        WeightedRubric(ColorRubric([
            # FillTypeIs, SolidColorEquals, DistinctSolidColors, ...
        ]), max_score=0.2),

        WeightedRubric(StructureRubric([
            # LayerInsideFrame, ChildCountAtLeast, IsGrouped, ...
        ]), max_score=0.2),

        WeightedRubric(EventRubric([
            # ToolUsed, EventTypeCount, EventTypeUsed, ...
        ]), max_score=0.2),
    ],
    efficiency=EfficiencyRubric(target_turns=<N>),
)
```

Drop rubrics that don't apply and redistribute the weights so they sum to 1.0.

---

## Step 5 — Test the verifier

```bash
cd verifier
python run.py --task <task_name> --log logs/<sample_run>.json
```

The output shows a per-rubric breakdown:
```
  fundamentals    0.2000 / 0.2   (100%)   ← all checks pass
  alignment       0.1500 / 0.2   ( 75%)   ← 3 of 4 pass
  ...
  base_score        0.7000 / 1.0
  efficiency        ×0.7362
  FINAL             0.5153 / 1.0     (52%)
```

Iterate:
- A check failing on a clearly-correct run → loosen its tolerance
- A check passing on a clearly-incorrect run → tighten its constraint or pick a stricter check
- A whole rubric scoring 0% → re-examine whether you're checking the right thing

---

## Check catalog

What's available in `verifier/verifier/checks/`:

### Shape checks (`shape_checks.py`)
- `ShapeCount(layer_type, equals)` — exact count of a shape type
- `ShapeCountAtLeast(layer_type, minimum)` — at least N of a shape
- `PolygonSidesEquals(sides)` — all polygons have N sides
- `StarPointsEquals(points)` — all stars have N points
- `StarInnerRatioEquals(ratio, tolerance)` — star inner-radius matches ratio

### Geometry checks (`geometry_checks.py`)
- `LayersAligned(layer_type, axis, tolerance)` — same coordinate on axis
- `LayersSymmetricX(layer_type, tolerance)` — symmetric around horizontal center
- `LayersSameDimensions(layer_type, tolerance)` — all instances same w×h
- `LayerEdgesAligned(type_a, edge_a, type_b, edge_b, tolerance)` — edge of A near edge of B
- `LayerSizeEquals(layer_type, width, height, tolerance)` — specific dimensions
- `LayerPosition(layer_type, x, y, tolerance)` — specific position
- `LayerRotationEquals(layer_type, degrees, tolerance)` — rotation matches

### Fill checks (`fill_checks.py`)
- `SolidColorEquals(layer_type, expected_rgb, tolerance)` — at least one matches
- `AllSolidColorEquals(layer_type, expected_rgb, tolerance)` — all match
- `FillTypeIs(layer_type, kind)` — fill is `solid` / `image` / etc.
- `FillCount(layer_type, equals)` — exact number of fills per layer
- `ImageFillExists(layer_type)` — at least one has image fill
- `FillOpacityEquals(layer_type, opacity, tolerance)` — fill-level opacity

### Stroke checks (`stroke_checks.py`)
- `StrokeExists(layer_type)`, `StrokeWeightEquals`, `StrokeColorEquals`, etc.

### Effect checks (`effect_checks.py`)
- `DropShadowExists`, `LayerBlurExists`, `OpacityEquals`, etc.

### Property checks (`property_checks.py`)
- `CornerRadiusEquals`, `IsLocked`, `IsVisible`, etc.

### Structure checks (`structure_checks.py`)
- `LayerInsideFrame(layer_type)` — direct child of a frame
- `ChildCount(parent_type, equals)` / `ChildCountAtLeast(parent_type, minimum)`
- `IsGrouped(layer_type)` — inside a group
- `ZOrderIsFirst(layer_type)` / `ZOrderIsLast(layer_type)`
- `LayerTotalCount(equals)` — total layers across pages

### Page checks (`page_checks.py`)
- `PageCount(equals)`, `LayerOnPage(layer_type, page_name)`

### Text checks (`text_checks.py`)
- `TextContent`, `FontSizeEquals` — typically not used (no keyboard)

### Event checks (`event_checks.py`)
- `EventTypeUsed(event_name)` — fired at least once
- `EventTypeCount(event_name, equals)` — exact count
- `EventTypeCountAtLeast(event_name, minimum)` — at least N
- `ToolUsed(tool_id)` — agent switched to this tool
- `AlignToolUsed()`, `UndoUsed()` — common shortcuts

Common semantic event names: `tool_change`, `create_rectangle`, `create_ellipse`, `create_polygon`, `create_star`, `create_line`, `create_text`, `create_frame`, `move_layer`, `resize_layer`, `set_fill`, `set_stroke`, `boolean_op`, `align_layers`, `group_selection`, `delete_layer`.

---

## When the library doesn't have what you need

Add a custom check inline in your task file:

```python
@dataclass
class MyCustomCheck:
    threshold: float
    def run(self, log):
        # do whatever inspection of log["outcome"]["document"] or log["semantic"]
        passed = ...
        return CheckResult(passed=passed,
                           score=1.0 if passed else 0.0,
                           max_score=1.0,
                           message="<human-readable result>")
```

If the check is reusable across tasks, contribute it back to `verifier/verifier/checks/<category>.py` so the next task can import it.

---

## Worked example — Task 1 (Two-Story House)

**CSV row** (already in `figma_tasks_WIP.csv` line 2):
- Difficulty: `Easy`
- Thorough description: "Use Frame tool, MacBook Air preset, build body rectangle..."
- Simplified prompt: "Build a two-story house inside a MacBook Air frame with a body, triangle roof, chimney, door, and 2 windows."
- Time: `10`
- Step-by-step: 19 atomic actions (Click Frame tool, click MacBook Air preset, click Rectangle tool, drag, ...)

**Rubric plan**:
| Rubric | Checks | Why |
|---|---|---|
| Fundamentals | `ShapeCount("rectangle", 2)`, `ShapeCount("ellipse", 2)`, `ShapeCount("polygon", 1)` | House has body+door (rect), 2 windows (ellipse), 1 roof (polygon) |
| Alignment | `LayersAligned(ellipse, center_y)`, `LayersSameDimensions(ellipse)`, `LayersSymmetricX(ellipse)`, `LayerEdgesAligned(polygon bottom, rectangle top)` | Windows on a line, roof sits on body |
| Color | `FillTypeIs(rectangle, solid)`, `FillTypeIs(polygon, solid)`, `FillTypeIs(ellipse, solid)`, `DistinctSolidColors(min=4)` | At least 4 different colors used |
| Structure | `LayerInsideFrame(rectangle/polygon/ellipse)`, `ChildCountAtLeast(frame, 5)` | Everything inside one frame |
| Event | `ToolUsed(rectangle/ellipse/polygon)`, `EventTypeCount(create_rectangle, 2)`, etc. | Right tools used; right shapes created |
| Efficiency | `target_turns=30` | 10-min task ≈ 30 turns |

**File**: `verifier/tasks/house_task_comprehensive.py` (~70 lines, see file).

**Run**: `python run.py --task house_task_comprehensive --log logs/house_sample.json` → produces 5-rubric breakdown × efficiency multiplier in `[0, 1]`.

---

## Tips & gotchas

- **Tolerances matter**: too tight and clean runs fail; too loose and broken runs pass. Start at the values in the comprehensive house task and adjust based on test runs.
- **Don't over-strict shape counts**: `equals=N` catches duplicates. `minimum=N` accepts but doesn't catch overshoot. If overshoot is a real failure mode (e.g., agent built two houses), use `equals` or define a custom range check.
- **Action log is brittle to schema changes**: when mock adds a new semantic event name, existing event checks may break. Test new tasks against a sample log first.
- **Rubric weights are tunable per task**: not every task needs 5 rubrics. A simple icon task might only need Fundamentals + Color (max_score=0.5 each).
- **The `id` field must be unique** — it's used as the import name and as the JSON filename in `scores/`.
- **Log file format**: any agent log must conform to the schema in `verifier/loader.py`'s `_validate` function (must have `raw`, `semantic`, `outcome.document`, `outcome.summary.shapeCounts`).

---

## Quick reference

```bash
# Add a CSV row, then:
cp verifier/tasks/house_task_comprehensive.py verifier/tasks/<task_name>.py
# edit imports, rubric contents, target_turns

# Test:
cd verifier
python run.py --task <task_name> --log logs/<sample>.json
```

That's the whole loop. Start with the comprehensive house task as your reference, copy and modify, run, iterate on tolerances. Tasks 2–50 should each take 30–60 minutes once you have the pattern.
