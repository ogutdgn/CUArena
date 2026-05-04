# Task 18 — Draw an eye icon: 3 nested ellipses (sclera, iris, pupil) sharing a center.

**Difficulty:** Easy  •  **Time horizon:** 8 min

## Thorough description

Draw 3 nested ellipses sharing a center: the largest white (sclera), a medium colored circle (iris), and a small black circle (pupil) on top. Use alignment buttons to share both center axes.

## Simplified prompt

> Draw an eye icon: 3 nested ellipses (sclera, iris, pupil) sharing a center.

## Step-by-step

1. Click Ellipse tool. 2. Drag the largest ellipse, pick white. 3. Right-click then Duplicate, scrub smaller, pick colored iris. 4. Duplicate, scrub even smaller, pick black for pupil. 5. Marquee all 3. 6. Click Align horizontal centers, then Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_18_donut.py`

```python
"""
Task 18 — Eye icon (in-scope replacement, no boolean).

3 nested ellipses sharing a center: outer (white sclera), middle (colored iris), inner (black pupil).
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
from verifier.checks.geometry_checks import LayersConcentric, LayerBoundsInside, LayerIsCircular
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
    id="task_18_donut",
    description="3 nested ellipses (sclera, iris, pupil) sharing a center.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=3),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersConcentric(layer_type="ellipse", tolerance=3.0),
            LayerBoundsInside(inner_type="ellipse", outer_type="ellipse", tolerance=2.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=3),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
```
