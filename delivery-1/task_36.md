# Task 36 — Draw a vintage frame: outer rectangle + smaller inner rectangle, both centered.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Draw an outer rectangle and a smaller inner rectangle inside it. Both rectangles share the same center. Each can have its own fill color.

## Simplified prompt

> Draw a vintage frame: outer rectangle + smaller inner rectangle, both centered.

## Step-by-step

1. Click Rectangle tool. 2. Drag the outer rectangle. 3. Pick a fill. 4. Right-click then Duplicate, scrub size smaller. 5. Pick a different fill. 6. Marquee both. 7. Click Align horizontal centers, then Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_36_polaroid.py`

```python
"""
Task 36 — Vintage frame (in-scope replacement, no image fill).

1 outer rectangle (the frame border) + 1 smaller inner rectangle (the artwork area)
both sharing the same center.
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
from verifier.checks.geometry_checks import LayersConcentric, LayerBoundsInside
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
    id="task_36_polaroid",
    description="Outer rectangle frame + smaller inner rectangle artwork area, sharing center.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersConcentric(layer_type="rectangle", tolerance=3.0),
            LayerBoundsInside(inner_type="rectangle", outer_type="rectangle", tolerance=2.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=2),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
```
