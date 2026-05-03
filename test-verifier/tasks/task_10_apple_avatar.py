"""
Task 10 — Circular apple avatar via image mask.

# BLOCKED: requires image fill emission (image kind) + mask feature in outcome.document.
# Once implemented, add ImageFillExists("ellipse") and a mask check.
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
    id="task_10_apple_avatar",
    description="Image dropped onto canvas + circle drawn over it + circle used as mask.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=1),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=1),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
