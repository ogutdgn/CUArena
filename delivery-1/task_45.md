# Task 45 — Build an emblem: 8-point blue star + smaller centered yellow circle.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Build an emblem: an 8-point star (Star tool) with a deep blue fill + a smaller circle on top with a yellow fill, both centered together.

## Simplified prompt

> Build an emblem: 8-point blue star + smaller centered yellow circle.

## Step-by-step

1. Click Star tool, scrub points to 8. 2. Drag the star, pick deep blue. 3. Click Ellipse tool, drag a smaller circle, pick yellow. 4. Marquee both. 5. Click Align horizontal centers and Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_45_geometric_emblem.py`

```python
"""
Task 45 — Layered geometric emblem (IN SCOPE).

8-point deep blue star + smaller centered yellow circle on top.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals
from verifier.checks.geometry_checks import LayerBoundsInside, LayerCenteredOnLayer, LayerIsCircular
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
    id="task_45_geometric_emblem",
    description="8-point blue star + smaller yellow circle perfectly centered on top.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("star",    equals=1),
            StarPointsEquals(points=8),
            ShapeCount("ellipse", equals=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="star", tolerance=4.0),
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=8.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("star",    kind="solid"),
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("star"),
            ToolUsed("ellipse"),
            EventTypeCount("create_star",    equals=1),
            EventTypeCount("create_ellipse", equals=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
```
