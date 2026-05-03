"""
Task 27 — Neumorphic button with paired drop shadows.

# BLOCKED: requires drop shadow effect emission. Once implemented, check that
# the button has 2 drop shadows (one with negative offset white, one with positive offset dark).
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCount, ShapeCountAtLeast
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
    id="task_27_neumorphic_button",
    description="Light gray frame + 200x200 rounded rectangle with two drop shadows + small placeholder icon.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("rectangle", equals=1),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=1),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
