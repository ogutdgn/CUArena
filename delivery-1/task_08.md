# Task 8 — Make two layered water waves drawn with smooth Bezier curves in different blue shades.

**Difficulty:** Easy  •  **Time horizon:** 15 min

## Thorough description

Create a 1000x300 frame. Use the Pen tool to draw a smooth horizontal wave with 2 peaks and 3 troughs using bezier handles (click and drag at each anchor). Apply a 4px blue stroke with rounded line caps. Duplicate the path, shift down, recolor in a different blue.

## Simplified prompt

> Make two layered water waves drawn with smooth Bezier curves in different blue shades.

## Step-by-step

1. Click Frame tool. 2. Click Pen tool. 3. Click and drag at anchor 1 to set bezier handles. 4. Repeat at peak 1, trough 1, peak 2, trough 2. 5. Press Escape. 6. Add 4px blue stroke, round caps. 7. Right-click then Duplicate. 8. Drag down. 9. Recolor in a different blue.

## Verifier

File: `test-verifier/tasks/task_08_water_waves.py`

```python
"""
Task 08 — Layered water waves (IN SCOPE).

Two pen-tool wave paths with bezier handles, in different blues, with rounded stroke caps.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.stroke_checks import DistinctStrokeColors
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
    id="task_08_water_waves",
    description="Two pen-tool S-curve waves with bezier handles in different blue shades.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=2),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            DistinctStrokeColors(minimum=2, tolerance=0.05),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("pen"),
            EventTypeCountAtLeast("create_vector", minimum=2),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=40),
)
```
