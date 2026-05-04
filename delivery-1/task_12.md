# Task 12 — Arrange 4 same-size rectangles in a horizontal row with consistent spacing.

**Difficulty:** Easy  •  **Time horizon:** 8 min

## Thorough description

Draw 4 same-size rectangles arranged in a horizontal row. Each rectangle has the same height (so their tops and bottoms align), with consistent horizontal spacing between them. Each can have any solid fill.

## Simplified prompt

> Arrange 4 same-size rectangles in a horizontal row with consistent spacing.

## Step-by-step

1. Click Rectangle tool. 2. Drag the first rectangle. 3. Right-click then Duplicate, drag adjacent right. 4. Repeat for 4 total. 5. Pick a fill for each. 6. Marquee all then click Align top, then Distribute horizontal spacing.

## Verifier

File: `test-verifier/tasks/task_12_shadowed_cards.py`

```python
"""
Task 12 — Card row (in-scope replacement).

4 same-size rectangles arranged in a horizontal row with consistent spacing,
all sharing the same y baseline.
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
    id="task_12_shadowed_cards",
    description="4 same-size rectangles in a horizontal row, sharing the same y baseline.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=4),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=4),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
```
