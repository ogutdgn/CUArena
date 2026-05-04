# Task 17 — Build an hourglass: 2 triangles point-to-point + 2 horizontal cap rectangles.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Build an hourglass: 2 triangles meeting point-to-point at the center (one pointing down, one pointing up below it), plus 2 horizontal rectangles as caps at the top and bottom. All shapes share a center x.

## Simplified prompt

> Build an hourglass: 2 triangles point-to-point + 2 horizontal cap rectangles.

## Step-by-step

1. Click Polygon tool. 2. Drag the upper triangle, scrub rotation to 180° (point down). 3. Right-click then Duplicate, scrub rotation to 0° (point up), drag below the first. 4. Click Rectangle tool. 5. Drag the top cap rectangle. 6. Drag the bottom cap rectangle. 7. Marquee all. 8. Click Align horizontal centers.

## Verifier

File: `test-verifier/tasks/task_17_play_button.py`

```python
"""
Task 17 — Hourglass shape (in-scope replacement, no boolean).

2 triangles point-to-point at the center + 2 horizontal rectangle caps (top and bottom).
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
from verifier.checks.geometry_checks import LayersAligned, LayersHaveRotations
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
    id="task_17_play_button",
    description="2 triangles point-to-point + 2 horizontal rectangle caps top and bottom.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("polygon",   equals=2),
            ShapeCount("rectangle", equals=2),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersAligned(layer_type="polygon",   axis="center_x", tolerance=5.0),
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=5.0),
            LayersHaveRotations(layer_type="polygon", expected=[0, 180], count_per=1, tolerance_deg=8.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("polygon",   kind="solid"),
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("polygon"),
            ToolUsed("rectangle"),
            EventTypeCount("create_polygon",   equals=2),
            EventTypeCount("create_rectangle", equals=2),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
```
