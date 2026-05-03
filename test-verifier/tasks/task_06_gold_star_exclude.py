"""
Task 06 — Asterisk burst (in-scope replacement).

8 lines radiating from a single center point at 45° intervals, gold stroke.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
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
    id="task_06_gold_star_exclude",
    description="8 lines radiating from a center point at 45° intervals.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("line", equals=8),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("line"),
            EventTypeCount("create_line", equals=8),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
