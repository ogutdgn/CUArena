# Task 14 — Make a dartboard target with 4 concentric red and white circles, centered, each with a 4px black stroke.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Draw 4 concentric circles with decreasing diameters (e.g., 240, 180, 120, 60 px), all sharing the same center. Alternate red and white from outermost to center: red, white, red, white. Add a 4px black stroke to each.

## Simplified prompt

> Make a dartboard target with 4 concentric red and white circles, centered, each with a 4px black stroke.

## Step-by-step

1. Click Ellipse tool. 2. Drag the largest circle, pick red. 3. Add 4px black stroke. 4. Right-click then Duplicate, scrub to 180px square, pick white. 5. Duplicate, scrub to 120px, pick red. 6. Duplicate, scrub to 60px, pick white. 7. Marquee all. 8. Click Align horizontal centers, then Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_14_concentric_target.py`

```python
"""
Task 14 — Concentric ring target / dartboard (IN SCOPE).

4 concentric circles, alternating red/white, all centered on each other.
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
from verifier.checks.geometry_checks import LayersConcentric, LayerBoundsInside, LayerIsCircular
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
    id="task_14_concentric_target",
    description="4 concentric ellipses (240/180/120/60 px) alternating red/white, "
                "all sharing the same center, with 4px black strokes.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=4),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersConcentric(layer_type="ellipse", tolerance=2.0),
            LayerBoundsInside(inner_type="ellipse", outer_type="ellipse", tolerance=2.0),
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
