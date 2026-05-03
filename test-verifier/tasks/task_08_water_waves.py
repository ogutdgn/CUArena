"""
Task 08 — Layered water waves (IN SCOPE).

Two pen-tool wave paths with bezier handles, in different blues, with rounded stroke caps.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
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
    id="task_08_water_waves",
    description="Two pen-tool S-curve waves with bezier handles in different blue shades.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=2),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("pen"),
            EventTypeCountAtLeast("create_vector", minimum=2),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=40),
)
