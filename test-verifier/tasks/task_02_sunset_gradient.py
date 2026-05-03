"""
Task 02 — Sunset gradient sky.

# BLOCKED: requires linear gradient fill emission in outcome.document.
# Once implemented, add ColorRubric with FillTypeIs(kind="gradient_linear")
# and a custom check for ≥5 gradient stops.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
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
    id="task_02_sunset_gradient",
    description="800x400 frame containing 1 rectangle filled with a 5-stop vertical linear gradient.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("rectangle", equals=1),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("frame"),
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=1),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
