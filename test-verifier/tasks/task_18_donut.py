"""
Task 18 — Donut via Subtract + sprinkles.

# BLOCKED: requires boolean Subtract. Sprinkle ellipses can be checked already.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCountAtLeast
from verifier.checks.fill_checks import FillTypeIs
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
    id="task_18_donut",
    description="Pink donut (large circle minus small) + 5 sprinkle ellipses in different colors at different angles.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("ellipse", minimum=7),  # 2 for donut + 5 sprinkles
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_ellipse", minimum=7),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
