# Task 15 — Draw 4 overlapping white ellipses forming a cloud silhouette.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Draw 4 overlapping ellipses of varying sizes, all with the same white fill, arranged so their tops form a fluffy cloud silhouette. Their bottoms roughly share a horizontal line.

## Simplified prompt

> Draw 4 overlapping white ellipses forming a cloud silhouette.

## Step-by-step

1. Click Ellipse tool. 2. Drag the first ellipse, pick white. 3. Right-click then Duplicate. 4. Scrub size, drag adjacent. 5. Repeat for 4 total ellipses with sizes that form a cloud shape.

## Verifier

File: `test-verifier/tasks/task_15_cloud_union.py`

```python
"""
Task 15 — Cloud silhouette (in-scope replacement, no boolean union).

4 overlapping ellipses of varying sizes, all the same white fill,
arranged so their tops form a fluffy cloud silhouette.
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
from verifier.checks.geometry_checks import LayersAligned, LayersOverlap
from verifier.checks.fill_checks   import AllSolidColorEquals
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
    id="task_15_cloud_union",
    description="4 overlapping white ellipses forming a cloud silhouette.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=4),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=20.0),
            LayersOverlap(type_a="ellipse", type_b="ellipse"),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            AllSolidColorEquals(layer_type="ellipse",
                                expected_rgb={"r": 1.0, "g": 1.0, "b": 1.0},
                                tolerance=0.1),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=4),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
```
