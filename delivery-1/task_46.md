# Task 46 — Draw 8 vertical rectangles of varying heights sharing a bottom baseline.

**Difficulty:** Medium  •  **Time horizon:** 18 min

## Thorough description

Draw 8 thin vertical rectangles of varying heights placed side-by-side with consistent gap, all sharing a common bottom baseline (like a histogram).

## Simplified prompt

> Draw 8 vertical rectangles of varying heights sharing a bottom baseline.

## Step-by-step

1. Click Rectangle tool, drag the first bar. 2. Right-click then Duplicate, drag adjacent right. 3. Scrub height to a different value. 4. Repeat for 8 bars total with varying heights. 5. Marquee all. 6. Click Align bottom.

## Verifier

File: `test-verifier/tasks/task_46_audio_waveform.py`

```python
"""
Task 46 — Histogram bars (in-scope replacement, no auto-layout).

8 thin vertical rectangles of varying heights, all solid-filled, placed manually
side-by-side with consistent gap, all sharing a common bottom baseline.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
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
    id="task_46_audio_waveform",
    description="8 vertical rectangles of varying heights placed side-by-side, sharing a bottom baseline.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=8),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=8),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
```
