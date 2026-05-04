# Task 24 — Draw a centered modal rectangle inside an outer frame using align tool.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Inside an outer frame, draw a smaller rounded rectangle and use the Align tool to center it horizontally and vertically inside the parent frame.

## Simplified prompt

> Draw a centered modal rectangle inside an outer frame using align tool.

## Step-by-step

1. Click Frame tool, drag the outer frame. 2. Click Rectangle tool. 3. Drag a smaller rectangle inside. 4. Scrub corner radius to ~16. 5. Pick white fill. 6. Marquee modal and frame. 7. Click Align horizontal centers, then Align vertical centers.

## Verifier

File: `test-verifier/tasks/task_24_centered_modal.py`

```python
"""
Task 24 — Centered modal panel (in-scope replacement, no constraints).

1 outer frame + 1 white rounded rectangle visually centered inside it
using alignment buttons (align_layers events).
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
from verifier.checks.geometry_checks import LayerCenteredInFrame
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, AlignToolUsed


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
    id="task_24_centered_modal",
    description="Outer frame + white rounded rectangle centered inside it via align tool.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("rectangle", equals=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerCenteredInFrame(layer_type="rectangle", tolerance=12.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=8.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=1),
            AlignToolUsed(),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
```
