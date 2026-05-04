# Task 27 — Draw 3 same-size squares centered together, rotated to different angles.

**Difficulty:** Easy  •  **Time horizon:** 12 min

## Thorough description

Draw 3 same-size squares all sharing the same center point but rotated to different angles (e.g., 0°, 30°, 60°). Each square a different color, layered to form a star-burst diamond pattern.

## Simplified prompt

> Draw 3 same-size squares centered together, rotated to different angles.

## Step-by-step

1. Click Rectangle tool. 2. Drag the first square. 3. Pick color A. 4. Right-click then Duplicate, scrub rotation to 30°. 5. Pick color B. 6. Duplicate again, scrub rotation to 60°. 7. Pick color C. 8. Marquee all. 9. Click Align horizontal centers and Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_27_neumorphic_button.py`

```python
"""
Task 27 — Layered diamond (in-scope replacement, no shadows).

3 squares each rotated at a different angle (0°, 30°, 60°) and centered together,
forming a layered star-burst pattern. Each square a different color.
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
from verifier.checks.geometry_checks import LayersConcentric, LayersSameDimensions, LayersEvenlyRotated
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
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
    id="task_27_neumorphic_button",
    description="3 same-size squares rotated at different angles, all sharing the same center.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=3),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersConcentric(layer_type="rectangle", tolerance=3.0),
            LayersEvenlyRotated(layer_type="rectangle", n=3, step_deg=30.0, tolerance_deg=8.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=3, tolerance=0.05),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=3),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
```
