"""
Task 21 — Vertical button stack with auto-layout.

# BLOCKED: requires auto-layout feature emission. Once implemented, check that
# the parent container has auto-layout enabled with vertical direction, gap=16, padding=24.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCount
from verifier.checks.fill_checks import FillTypeIs
from verifier.checks.event_checks import ToolUsed, EventTypeCount


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
    id="task_21_button_stack",
    description="3 differently-colored 240x48 rectangles stacked vertically in an auto-layout frame.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=3),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=3),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
