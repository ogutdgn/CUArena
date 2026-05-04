# Task 26 — Draw 5 same-size squares in a row with brand colors.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Draw 5 same-size squares in a horizontal row, each filled a different brand color (e.g., 1 primary blue + 4 supporting accent colors).

## Simplified prompt

> Draw 5 same-size squares in a row with brand colors.

## Step-by-step

1. Click Rectangle tool. 2. Drag the first square. 3. Pick a brand color. 4. Right-click then Duplicate, drag right, recolor. 5. Repeat for 5 total. 6. Marquee all. 7. Click Align top.

## Verifier

File: `test-verifier/tasks/task_26_color_variable_card.py`

```python
"""
Task 26 — Brand color row (in-scope replacement, no variables).

5 same-size squares arranged in a horizontal row, each filled a different
brand color (1 primary + 4 supports).
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
    id="task_26_color_variable_card",
    description="5 same-size squares in a horizontal row, each a different brand color.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=5),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=5, tolerance=0.05),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=5),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
```
