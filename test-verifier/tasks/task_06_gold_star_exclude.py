"""
Task 06 — 10-point gold star via Exclude.

# BLOCKED: requires boolean Exclude operation to be emitted. Once implemented,
# check that boolean_op event with op="exclude" appears in the log.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
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
    description="Two pentagons (one rotated 36°) overlapping, boolean Exclude → 10-point star, gold fill.",
    rubrics=[
        WeightedRubric(EventRubric([
            ToolUsed("polygon"),
            EventTypeCount("create_polygon", equals=2),
        ]), max_score=1.0),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
