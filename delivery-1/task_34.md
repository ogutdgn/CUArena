# Task 34 — Make a 6-fold symmetric snowflake by duplicating one branch group and rotating 60° five times.

**Difficulty:** Medium  •  **Time horizon:** 18 min

## Thorough description

Inside a navy frame, draw a vertical white line through the center plus 2 short diagonal branches off the upper portion (forming one snowflake arm). Group the arm. Duplicate the group and rotate 60°. Repeat to make 6 branches.

## Simplified prompt

> Make a 6-fold symmetric snowflake by duplicating one branch group and rotating 60° five times.

## Step-by-step

1. Click Frame tool, navy fill. 2. Click Line tool, draw a vertical center line, white. 3. Draw 2 short diagonal branch lines off the upper portion. 4. Marquee the branch lines, right-click then Group. 5. Right-click then Duplicate, scrub rotation +60°. 6. Repeat duplicate-and-rotate for 5 more branches (120°, 180°, 240°, 300°).

## Verifier

File: `test-verifier/tasks/task_34_snowflake.py`

```python
"""
Task 34 — 6-fold symmetric snowflake (IN SCOPE).

Navy frame + 6 line-tool branches rotated 60° each around the center.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast


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
    id="task_34_snowflake",
    description="6-fold symmetric snowflake: 6 white line branches rotated 60° each on a navy frame.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCountAtLeast("line", minimum=6),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("frame", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("line"),
            EventTypeCountAtLeast("create_line", minimum=6),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=35),
)
```
