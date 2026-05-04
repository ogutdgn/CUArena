# Task 37 — Draw a tilted yellow sticky note with a folded corner and 3 note lines.

**Difficulty:** Easy  •  **Time horizon:** 12 min

## Thorough description

Draw a yellow square (rotated 3°) for a sticky note. Above the body draw a small triangular fold on the top-right corner using the Pen tool with a darker yellow. Add 3 thin horizontal lines representing notes.

## Simplified prompt

> Draw a tilted yellow sticky note with a folded corner and 3 note lines.

## Step-by-step

1. Click Rectangle tool, drag a yellow square. 2. Scrub rotation to 3°. 3. Click Pen tool, draw a small triangle on the top-right corner with darker yellow fill. 4. Click Line tool, draw the first horizontal line. 5. Right-click then Duplicate, drag below. 6. Duplicate again.

## Verifier

File: `test-verifier/tasks/task_37_sticky_note.py`

```python
"""
Task 37 — Yellow sticky note (IN SCOPE).

Tilted yellow square + drop shadow + pen-tool corner fold + 3 horizontal lines.

Note: drop shadow check assumes effects are emitted in outcome.document.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerBoundsInside
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast


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
    id="task_37_sticky_note",
    description="Yellow square (rotated ~3°) + drop shadow + pen-tool fold + 3 horizontal lines.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCountAtLeast("vector", minimum=1),
            ShapeCountAtLeast("line", minimum=3),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerBoundsInside(inner_type="vector", outer_type="rectangle", tolerance=4.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("pen"),
            ToolUsed("line"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCountAtLeast("create_line", minimum=3),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
```
