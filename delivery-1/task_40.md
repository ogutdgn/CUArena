# Task 40 — Build an iOS green toggle switch with a white circle thumb on the right.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Build an iOS-style green toggle switch: a green pill (rounded rectangle, radius 999) + a smaller white circle thumb positioned 2px from the right edge.

## Simplified prompt

> Build an iOS green toggle switch with a white circle thumb on the right.

## Step-by-step

1. Click Rectangle tool, drag the pill body, scrub corner radius to 999, pick green. 2. Click Ellipse tool, drag the white circle thumb. 3. Drag the thumb to position 2px from the right edge of the pill.

## Verifier

File: `test-verifier/tasks/task_40_toggle_switch.py`

```python
"""
Task 40 — iOS toggle switch (IN SCOPE).

Green pill (rounded rectangle, radius 999) + white circle thumb (positioned right).
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
from verifier.checks.geometry_checks import LayerBoundsInside
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.property_checks import CornerRadiusAtLeast
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
    id="task_40_toggle_switch",
    description="Green pill rectangle + white circle thumb positioned on the right.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCount("ellipse",   equals=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="rectangle", tolerance=4.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=24.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            FillTypeIs("ellipse",   kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_ellipse",   equals=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
```
