# Task 31 — Draw a sun: yellow circle + 8 triangle rays rotated radially around it.

**Difficulty:** Medium  •  **Time horizon:** 15 min

## Thorough description

Inside a frame, draw a 100px yellow center circle and 8 thin triangle rays around it, each rotated 45° from the last (so 12 o'clock, 1:30, 3:00, 4:30, 6:00, 7:30, 9:00, 10:30 directions).

## Simplified prompt

> Draw a sun: yellow circle + 8 triangle rays rotated radially around it.

## Step-by-step

1. Click Frame tool. 2. Click Ellipse tool, drag the center circle, pick yellow. 3. Click Polygon tool, drag a thin triangle pointing up. 4. Right-click then Duplicate, scrub rotation +45°. 5. Repeat the duplicate-rotate pattern 6 more times for 8 rays total.

## Verifier

File: `test-verifier/tasks/task_31_sun_rays.py`

```python
"""
Task 31 — Sun with 8 rotated triangle rays (IN SCOPE).

Yellow circle in center + 8 thin triangles arranged radially at 45° intervals.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayersSameDimensions, LayerIsCircular
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
    id="task_31_sun_rays",
    description="Yellow circle center + 8 triangle rays rotated radially around it.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=1),
            ShapeCount("polygon", equals=8),
            ShapeCountAtLeast("frame", minimum=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=2.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            FillTypeIs("polygon", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_ellipse", equals=1),
            EventTypeCount("create_polygon", equals=8),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
```
