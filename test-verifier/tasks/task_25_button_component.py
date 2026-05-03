"""
Task 25 — Purple button as a reusable component.

# BLOCKED: requires components feature (create_component + place_instance events,
# component/instance node types in outcome.document).
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
    id="task_25_button_component",
    description="Build a button (rectangle + ellipse + label rectangle), make it a component, place 2 instances.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("rectangle", minimum=2),  # at least button body + label
            ShapeCountAtLeast("ellipse", minimum=1),    # icon
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_rectangle", minimum=2),
            EventTypeCountAtLeast("create_ellipse", minimum=1),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
