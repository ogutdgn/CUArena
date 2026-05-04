# Task 16 — Draw a speech bubble: rounded rectangle + small triangle tail at bottom-left.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Draw a rounded rectangle (the speech bubble body) and a small triangle (the tail) positioned at the bottom-left corner of the rectangle, slightly overlapping. Both filled the same light gray color.

## Simplified prompt

> Draw a speech bubble: rounded rectangle + small triangle tail at bottom-left.

## Step-by-step

1. Click Rectangle tool. 2. Drag the bubble body, scrub corner radius to 16. 3. Pick light gray fill. 4. Click Polygon tool. 5. Drag the small triangle below-left of the bubble. 6. Pick the same light gray fill. 7. Position the triangle so its top edge slightly overlaps the bubble bottom-left corner.

## Verifier

File: `test-verifier/tasks/task_16_speech_bubble.py`

```python
"""
Task 16 — Speech bubble visual (in-scope replacement, no boolean).

1 rounded rectangle (bubble body) + 1 small triangle (tail) positioned
at the bottom-left, both filled the same light gray color.
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
from verifier.checks.geometry_checks import LayersOverlap
from verifier.checks.fill_checks   import FillTypeIs, SameColorAcrossTypes
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
    id="task_16_speech_bubble",
    description="Rounded rectangle bubble + small triangle tail positioned at bottom-left.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCount("polygon",   equals=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersOverlap(type_a="rectangle", type_b="polygon"),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=8.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            FillTypeIs("polygon",   kind="solid"),
            SameColorAcrossTypes(types=["rectangle", "polygon"], tolerance=0.05),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("polygon"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_polygon",   equals=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
```
