"""
Task 05 — Red heart via Union.

# BLOCKED: requires boolean operations to be emitted. Once implemented,
# add EventRubric with EventTypeUsed("boolean_op") and check the resulting
# vector node has a red solid fill.
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
    id="task_05_red_heart_union",
    description="2 circles + 1 inverted triangle, marquee-selected and unioned into a heart, red fill.",
    rubrics=[
        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_ellipse", equals=2),
            EventTypeCount("create_polygon", equals=1),
        ]), max_score=1.0),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
