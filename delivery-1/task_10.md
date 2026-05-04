# Task 10 — Make 4 nested squares with shared center, alternating two colors.

**Difficulty:** Easy  •  **Time horizon:** 8 min

## Thorough description

Draw 4 same-style nested squares of decreasing size, all sharing the same center, alternating two colors (outermost color A, next color B, next A, innermost B). Use alignment buttons to center them perfectly.

## Simplified prompt

> Make 4 nested squares with shared center, alternating two colors.

## Step-by-step

1. Click Rectangle tool. 2. Drag the largest square, pick color A. 3. Right-click then Duplicate. 4. Scrub width and height to ~75% of original, pick color B. 5. Duplicate again, scrub to ~50%, pick A. 6. Duplicate again, scrub to ~25%, pick B. 7. Marquee all 4. 8. Click Align horizontal centers, then Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_10_apple_avatar.py`

```python
"""
Task 10 — Concentric squares (in-scope replacement).

4 nested squares of decreasing size, alternating two colors, all sharing the same center.
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
    id="task_10_apple_avatar",
    description="4 nested squares of decreasing size, alternating two colors, sharing center.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=4),
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
            EventTypeCount("create_rectangle", equals=4),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
```
