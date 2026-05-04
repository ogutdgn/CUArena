# Task 39 — Build a wifi icon: 3 pen-tool arcs + small filled circle below.

**Difficulty:** Medium  •  **Time horizon:** 18 min

## Thorough description

Inside a 200x200 frame, draw 3 concentric arcs above a center point using the Pen tool. Apply a 6px navy stroke with rounded caps. Add a small filled navy circle below the arcs.

## Simplified prompt

> Build a wifi icon: 3 pen-tool arcs + small filled circle below.

## Step-by-step

1. Click Frame tool. 2. Click Pen tool, draw the first arc above center. 3. Press Escape, add 6px navy stroke, round caps. 4. Right-click then Duplicate, scrub larger, drag above. 5. Duplicate again, larger. 6. Click Ellipse tool, draw the small filled circle below the arcs.

## Verifier

File: `test-verifier/tasks/task_39_wifi_icon.py`

```python
"""
Task 39 — Wifi signal icon (IN SCOPE).

3 concentric pen-tool arcs (navy stroke with rounded caps) + small filled circle below.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast, EventTypeCount


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
    id="task_39_wifi_icon",
    description="3 concentric pen-tool arcs above 1 small filled circle.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=3),
            ShapeCount("ellipse", equals=1),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("pen"),
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_vector", minimum=3),
            EventTypeCount("create_ellipse", equals=1),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
```
