# Task 19 — Build a padlock with a rectangle body, a pen-tool U-shackle, and a keyhole.

**Difficulty:** Easy  •  **Time horizon:** 15 min

## Thorough description

Build a padlock icon: 1 rounded rectangle body + 1 pen-tool U-shaped shackle drawn above it + 1 small circle keyhole in the center of the body. Body is dark gray, keyhole is black.

## Simplified prompt

> Build a padlock with a rectangle body, a pen-tool U-shackle, and a keyhole.

## Step-by-step

1. Click Rectangle tool. 2. Drag the lock body, scrub corner radius to 12. 3. Pick dark gray fill. 4. Click Pen tool. 5. Click anchors to draw a U-shape above the body. 6. Press Escape. 7. Add 14px stroke, round caps. 8. Click Ellipse tool. 9. Drag the keyhole circle, pick black.

## Verifier

File: `test-verifier/tasks/task_19_padlock.py`

```python
"""
Task 19 — Padlock icon (IN SCOPE).

Rectangle body with rounded corners, pen-drawn U-shaped shackle above, small keyhole circle.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerBoundsInside, LayersOverlap, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast


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
    id="task_19_padlock",
    description="Rounded rectangle body + pen-tool U-shackle above + keyhole circle.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("rectangle", minimum=1),
            ShapeCountAtLeast("vector", minimum=1),
            ShapeCountAtLeast("ellipse", minimum=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="rectangle", tolerance=4.0),
            LayersOverlap(type_a="vector", type_b="rectangle"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("pen"),
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_rectangle", minimum=1),
            EventTypeCountAtLeast("create_vector", minimum=1),
            EventTypeCountAtLeast("create_ellipse", minimum=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
```
