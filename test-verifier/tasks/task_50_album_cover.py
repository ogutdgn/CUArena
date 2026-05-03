"""
Task 50 — Album cover via shape mask.

# BLOCKED: requires image fill + mask features.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCountAtLeast
from verifier.checks.event_checks import ToolUsed


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
    id="task_50_album_cover",
    description="Photo on canvas + star or hexagon over it, used as mask, with 4px white border.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("star", minimum=1),  # or polygon — agent picks
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("star"),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
