"""
Task 04 — Rainbow color wheel.

# BLOCKED: requires angular (conic) gradient fill emission. Once implemented,
# add ColorRubric checking FillTypeIs(kind="gradient_angular") and ≥6 stops.
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
    id="task_04_color_wheel",
    description="400x400 frame containing 1 circle with angular (conic) gradient cycling through 6 rainbow colors.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("ellipse", equals=1),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("frame"),
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=1),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
