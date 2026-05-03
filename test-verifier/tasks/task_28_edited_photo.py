"""
Task 28 — Edited photo with adjustments.

# BLOCKED: requires image fill emission + image adjustment events
# (contrast, saturation, exposure sliders).
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric


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
    id="task_28_edited_photo",
    description="Photo dropped on canvas + image controls adjusted: contrast +20, saturation +30, exposure -10.",
    rubrics=[
        # No checks possible until image fill + adjustment events are emitted
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
