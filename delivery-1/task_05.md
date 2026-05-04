# Task 5 — Build a plus sign from 2 perpendicular rectangles centered together.

**Difficulty:** Easy  •  **Time horizon:** 8 min

## Thorough description

Build a plus-sign emblem from 2 rectangles. The horizontal rectangle is wide and short; the vertical rectangle is narrow and tall. Place them so they cross at the center, with their center points aligned.

## Simplified prompt

> Build a plus sign from 2 perpendicular rectangles centered together.

## Step-by-step

1. Click Rectangle tool. 2. Drag a wide horizontal rectangle. 3. Drag a tall narrow vertical rectangle. 4. Pick same color for both. 5. Marquee both. 6. Click Align horizontal centers. 7. Click Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_05_red_heart_union.py`

```python
"""
Task 05 — Plus-sign emblem (in-scope replacement).

2 perpendicular rectangles crossed at center to form a + shape.
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
from verifier.checks.geometry_checks import LayersAligned, LayersHaveAspectMix
from verifier.checks.fill_checks   import FillTypeIs, AllSolidColorEquals
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
    id="task_05_red_heart_union",
    description="2 perpendicular rectangles crossed at center forming a plus sign, both red fill.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=5.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
            LayersHaveAspectMix(layer_type="rectangle",
                                horizontal_count=1, vertical_count=1, ratio=2.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            AllSolidColorEquals(layer_type="rectangle",
                                expected_rgb={"r": 1.0, "g": 0.1, "b": 0.1},
                                tolerance=0.20),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=2),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
```
