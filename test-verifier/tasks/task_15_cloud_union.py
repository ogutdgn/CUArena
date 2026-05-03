"""
Task 15 — Cloud shape via Union.

# BLOCKED: requires boolean Union operation. Once implemented, check that
# boolean_op event with op="union" appears.
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
    id="task_15_cloud_union",
    description="4 overlapping ellipses unioned into a cloud silhouette, white fill, light gray stroke.",
    rubrics=[
        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=4),
        ]), max_score=1.0),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
