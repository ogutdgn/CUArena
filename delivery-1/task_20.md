# Task 20 — Draw 2 overlapping bright-colored circles inside a dark navy frame.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Inside an 800x600 frame with dark navy fill, draw 2 overlapping circles in different bright colors (e.g., magenta and cyan). Position them so they overlap by ~30%.

## Simplified prompt

> Draw 2 overlapping bright-colored circles inside a dark navy frame.

## Step-by-step

1. Click Frame tool, drag 800x600 frame, pick dark navy. 2. Click Ellipse tool. 3. Drag the first circle, pick magenta. 4. Drag the second circle adjacent, pick cyan. 5. Position the second circle so it overlaps the first.

## Verifier

File: `test-verifier/tasks/task_20_glow_blob.py`

```python
"""
Task 20 — Glow blob backdrop (IN SCOPE).

Frame with dark navy fill, two overlapping circles with layer blur (magenta + cyan).

Note: Layer blur is checked via effect_checks if the env emits effects in outcome.document.
If layer blur isn't emitted yet, the corresponding check will fail; structure + counts still verify.
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
from verifier.checks.geometry_checks import LayersOverlap, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.page_checks   import PageBackgroundColorEquals
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
    id="task_20_glow_blob",
    description="Dark navy frame with 2 overlapping blurred circles (magenta + cyan).",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("ellipse", equals=2),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersOverlap(type_a="ellipse", type_b="ellipse"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            FillTypeIs("frame",   kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.05),
            PageBackgroundColorEquals(expected_rgb={"r": 0.05, "g": 0.05, "b": 0.2}, tolerance=0.4),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("frame"),
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=2),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
```
