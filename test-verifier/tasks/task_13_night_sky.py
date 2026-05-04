"""
Task 13 — Cross-hatch hashtag (in-scope replacement).

2 vertical lines + 2 horizontal lines forming a # symbol.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayersHaveRotations
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
    id="task_13_night_sky",
    description="2 vertical + 2 horizontal lines crossing to form a # (hashtag) symbol.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("line", equals=4),
        ]), max_score=0.34),

        WeightedRubric(AlignmentRubric([
            LayersHaveRotations(layer_type="line", expected=[0, 90], count_per=2, tolerance_deg=8.0),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("line"),
            EventTypeCount("create_line", equals=4),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
