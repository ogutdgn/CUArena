# Task 25 — Draw 3 identical rectangles in a horizontal row with consistent spacing.

**Difficulty:** Easy  •  **Time horizon:** 8 min

## Thorough description

Draw 3 identical rectangles (same size, same color) placed in a horizontal row with consistent spacing. All share the same y-baseline.

## Simplified prompt

> Draw 3 identical rectangles in a horizontal row with consistent spacing.

## Step-by-step

1. Click Rectangle tool. 2. Drag the first rectangle. 3. Pick a fill color. 4. Right-click then Duplicate, drag right. 5. Duplicate again, drag right. 6. Marquee all 3. 7. Click Align top, then Distribute horizontal spacing.

## Verifier

File: `test-verifier/tasks/task_25_button_component.py`

```python
"""
Task 25 — Identical button row (in-scope replacement, no components).

3 identical 160x40 rectangles placed manually in a horizontal row,
all the same fill color and dimensions.
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
from verifier.checks.geometry_checks import LayersSameDimensions, LayersAligned
from verifier.checks.fill_checks   import AllSolidColorEquals, FillTypeIs
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
    id="task_25_button_component",
    description="3 identical rectangles (same size, same color) placed in a horizontal row.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=3),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=3),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
```
