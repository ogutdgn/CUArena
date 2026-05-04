"""
Task 07 — Layered mountain range (IN SCOPE).

Two pen-tool paths in different gray shades — closer mountain in front of farther one.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
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
    id="task_07_mountain_range",
    description="Two overlapping pen-tool mountain paths in different gray shades.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=2),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("vector", kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.05),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("pen"),
            EventTypeCountAtLeast("create_vector", minimum=2),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
