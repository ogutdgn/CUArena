# Task 33 — Draw a 4-section pie chart with a base circle and 3 colored wedge triangles.

**Difficulty:** Medium  •  **Time horizon:** 18 min

## Thorough description

Draw a circle with a teal solid fill (the pie chart base). Then draw 3 thin pie-slice triangles from the center extending to the edge in different colors (coral, gold, lavender), rotated to different angles.

## Simplified prompt

> Draw a 4-section pie chart with a base circle and 3 colored wedge triangles.

## Step-by-step

1. Click Ellipse tool, drag the base circle, pick teal. 2. Click Polygon tool, drag a thin pie-slice triangle from center to edge, pick coral. 3. Right-click then Duplicate, scrub rotation, pick gold. 4. Duplicate, rotate, pick lavender.

## Verifier

File: `test-verifier/tasks/task_33_pie_chart.py`

```python
"""
Task 33 — 4-section pie chart (IN SCOPE).

Base circle + 3 rotated triangle wedges layered on top in different colors.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayerIsCircular
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
    id="task_33_pie_chart",
    description="Stylized pie chart: 1 base circle + 3 rotated triangle wedges in different colors.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=1),
            ShapeCount("polygon", equals=3),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
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
            EventTypeCount("create_polygon", equals=3),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=40),
)
```
