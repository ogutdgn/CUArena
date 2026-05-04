# Task 38 — Build a battery indicator with body, terminal, and 3 inner level bars.

**Difficulty:** Easy  •  **Time horizon:** 12 min

## Thorough description

Build a battery indicator: a rounded outer rectangle (the body, no fill, gray stroke), a smaller rectangle attached on the right (the terminal), and 3 colored bar rectangles inside in green/yellow/red sequence.

## Simplified prompt

> Build a battery indicator with body, terminal, and 3 inner level bars.

## Step-by-step

1. Click Rectangle tool, drag the body rectangle, scrub corner radius to 8. 2. Remove fill, add gray stroke. 3. Drag a small rectangle attached on the right (terminal). 4. Drag 3 colored bars inside the body, picking green, yellow, red.

## Verifier

File: `test-verifier/tasks/task_38_battery_indicator.py`

```python
"""
Task 38 — Battery indicator (IN SCOPE).

Rounded outer rectangle (no fill, gray stroke) + small terminal rectangle on right
+ 3 colored bar rectangles inside (green, yellow, red).
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
from verifier.checks.fill_checks   import FillTypeIs, LayerHasNoFill
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
    id="task_38_battery_indicator",
    description="Battery body + terminal + 3 colored bars (5 rectangles total).",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=5),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerHasNoFill(layer_type="rectangle"),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=5),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
```
