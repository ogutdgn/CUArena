"""
Task 13 — Night sky with crescent moon.

# BLOCKED: requires boolean Subtract operation. Once implemented, check that
# boolean_op event with op="subtract" appears, and the resulting vector has yellow fill.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
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
    id="task_13_night_sky",
    description="Dark navy frame + crescent moon (via subtract) + 6 small white star circles.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame",   minimum=1),
            ShapeCountAtLeast("ellipse", minimum=8),  # 2 for moon (pre-subtract) + 6 stars
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_ellipse", minimum=8),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=28),
)
