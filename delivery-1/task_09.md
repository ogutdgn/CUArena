# Task 9 — Arrange 12 same-size colored squares in a 4x3 grid using Tidy up.

**Difficulty:** Easy  •  **Time horizon:** 16 min

## Thorough description

Inside a frame, arrange 12 same-size squares in a 4x3 grid. Each square is filled a different color. Use Tidy up to lock the grid arrangement.

## Simplified prompt

> Arrange 12 same-size colored squares in a 4x3 grid using Tidy up.

## Step-by-step

1. Click Frame tool. 2. Click Rectangle tool. 3. Drag the first square. 4. Right-click then Duplicate, drag right. 5. Repeat to fill the first row. 6. Continue duplicating to fill rows 2 and 3 for 12 total. 7. Pick distinct colors for each. 8. Marquee all then click Tidy up.

## Verifier

File: `test-verifier/tasks/task_09_brand_palette.py`

```python
"""
Task 09 — 12-color swatch grid (in-scope replacement).

12 same-size squares arranged in a 4x3 grid, each filled a different color.
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
from verifier.checks.geometry_checks import LayersSameDimensions, LayersInGrid
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
    id="task_09_brand_palette",
    description="4x3 grid of 12 same-size squares, each filled a different color.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=12),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersInGrid(layer_type="rectangle", rows=3, cols=4, tolerance=10.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=12, tolerance=0.05),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=12),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
```
