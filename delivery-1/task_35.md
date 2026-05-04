# Task 35 — Make a 3x2 honeycomb pattern of 6 yellow hexagons.

**Difficulty:** Medium  •  **Time horizon:** 18 min

## Thorough description

Inside a frame, draw a single hexagon (Polygon tool, 6 sides) with yellow fill and thin black stroke. Right-click and duplicate, then arrange 6 hexagons in a 3x2 honeycomb tiling pattern with offset rows.

## Simplified prompt

> Make a 3x2 honeycomb pattern of 6 yellow hexagons.

## Step-by-step

1. Click Frame tool. 2. Click Polygon tool, scrub sides to 6. 3. Drag the first hexagon, pick yellow. 4. Add a 1px black stroke. 5. Right-click then Duplicate, drag adjacent. 6. Repeat for 6 total in a honeycomb arrangement.

## Verifier

File: `test-verifier/tasks/task_35_honeycomb.py`

```python
"""
Task 35 — 3x2 honeycomb pattern (IN SCOPE).

6 yellow hexagons (polygon, 6 sides) arranged in honeycomb tiling with black strokes.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import LayersSameDimensions, OffsetGridLayout
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
    id="task_35_honeycomb",
    description="3x2 honeycomb of 6 yellow hexagons (6-sided polygons) tiled together.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("polygon", equals=6),
            PolygonSidesEquals(sides=6),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=2.0),
            OffsetGridLayout(layer_type="polygon", rows=2, cols=3, tolerance=15.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("polygon", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("polygon"),
            EventTypeCount("create_polygon", equals=6),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
```
