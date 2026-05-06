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
