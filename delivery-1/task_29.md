# Task 29 — Draw a 2x2 polka dot grid using Tidy up to align 4 circles.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Inside a frame with off-white fill, draw 4 same-size circles arranged in a 2x2 grid pattern. Use Tidy up after marquee-selecting all 4. Each circle the same color (or all different).

## Simplified prompt

> Draw a 2x2 polka dot grid using Tidy up to align 4 circles.

## Step-by-step

1. Click Frame tool, drag a frame, pick off-white fill. 2. Click Ellipse tool. 3. Drag the first circle, pick a color. 4. Right-click then Duplicate three times. 5. Position the 4 circles in a rough 2x2 layout. 6. Marquee all 4. 7. Click Tidy up.

## Verifier

File: `test-verifier/tasks/task_29_polka_dot_grid.py`

```python
"""
Task 29 — Polka dot grid (IN SCOPE).

Frame with off-white fill, 4 circles arranged in a 2x2 grid via duplicate + Tidy up.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayersSameDimensions, LayersInGrid, LayerIsCircular
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
    id="task_29_polka_dot_grid",
    description="2x2 polka-dot grid: 4 same-size circles with consistent spacing inside a frame.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=4),
            ShapeCountAtLeast("frame", minimum=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="ellipse", tolerance=2.0),
            LayersInGrid(layer_type="ellipse", rows=2, cols=2, tolerance=10.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=4),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
```
