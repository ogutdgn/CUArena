# Task 44 — Draw an avatar circle + a small status badge circle at bottom-right.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Draw 1 large avatar circle and 1 smaller circle (badge) overlapping the bottom-right of the larger one, with a white stroke around the badge.

## Simplified prompt

> Draw an avatar circle + a small status badge circle at bottom-right.

## Step-by-step

1. Click Ellipse tool, drag the avatar circle. 2. Pick a fill. 3. Drag a smaller circle. 4. Pick green fill. 5. Add 2px white stroke. 6. Drag the smaller circle to overlap the bottom-right of the avatar.

## Verifier

File: `test-verifier/tasks/task_44_avatar_status.py`

```python
"""
Task 44 — Avatar with badge (in-scope replacement, no image fill).

1 large circle (avatar placeholder) + 1 smaller circle (status badge) at the bottom-right
of the avatar, both solid fills.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersOverlap, LayerOnTopOf, LayerIsCircular
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
    id="task_44_avatar_status",
    description="1 large avatar circle + 1 smaller status badge circle at bottom-right.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=2),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersOverlap(type_a="ellipse", type_b="ellipse"),
            LayerOnTopOf(type_a="ellipse", type_b="ellipse"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=2),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
```
