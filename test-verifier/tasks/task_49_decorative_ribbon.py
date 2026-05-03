"""
Task 49 — Decorative gradient ribbon.

# BLOCKED: requires (a) custom dash pattern on stroke, (b) outline-stroke conversion,
# (c) linear gradient fill on the resulting vector. Multiple env features.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCountAtLeast
from verifier.checks.event_checks import ToolUsed, EventTypeCountAtLeast


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
    id="task_49_decorative_ribbon",
    description="Pen-tool S-curve, dashed stroke, outlined to vector, filled with horizontal gradient.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=1),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("pen"),
            EventTypeCountAtLeast("create_vector", minimum=1),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=50),
)
