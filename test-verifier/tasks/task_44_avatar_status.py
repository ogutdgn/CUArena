"""
Task 44 — Avatar with online status indicator.

# BLOCKED: requires image fill emission. Once implemented, check that the larger
# circle has an image fill and the smaller green circle has a 2px white stroke.
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
    id="task_44_avatar_status",
    description="64px circle (image fill) + 16px green circle with white stroke at bottom-right.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=2),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=2),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
