# Task 23 — Draw a left sidebar rectangle inside an outer frame.

**Difficulty:** Easy  •  **Time horizon:** 8 min

## Thorough description

Inside an outer frame, draw a tall narrow rectangle filling roughly the left 17% of the frame width, full height, with a dark gray fill (the sidebar).

## Simplified prompt

> Draw a left sidebar rectangle inside an outer frame.

## Step-by-step

1. Click Frame tool, drag the outer frame. 2. Click Rectangle tool. 3. Drag the sidebar rectangle covering the left side, full height. 4. Pick dark gray fill.

## Verifier

File: `test-verifier/tasks/task_23_stretchy_sidebar.py`

```python
"""
Task 23 — Sidebar layout (in-scope replacement, no constraints).

1 outer frame + 1 sidebar rectangle filling the left ~17% of the frame width,
dark gray fill.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerAspectRatioGreaterThan, LayerWidthFraction
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount


@dataclass
class WeightedRubric:
    rubric: Any
    max_score: float
    def run(self, log):
        r = self.rubric.run(log)
        scale = self.max_score / r.max_score if r.max_score else 1.0
        return RubricResult(name=r.name, score=round(r.score * scale, 4),
                            max_score=self.max_score, checks=r.checks)


task = Task(
    id="task_23_stretchy_sidebar",
    description="Outer frame + dark gray sidebar rectangle on the left edge.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("rectangle", equals=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="vertical"),
            LayerWidthFraction(inner_type="rectangle", parent_type="frame",
                               min_frac=0.08, max_frac=0.30),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("frame"),
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
```
