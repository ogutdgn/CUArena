"""
Task 42 — Notification bell with badge (IN SCOPE).

Pen-tool bell silhouette (yellow-gold) + small clapper circle + red badge circle on upper-right.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.fill_checks   import FillTypeIs
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
    id="task_42_bell_icon",
    description="Pen-tool bell silhouette + clapper circle + red badge on upper-right.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("vector",  minimum=1),  # bell
            ShapeCountAtLeast("ellipse", minimum=2),  # clapper + badge
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("vector",  kind="solid"),
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("pen"),
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_vector",  minimum=1),
            EventTypeCountAtLeast("create_ellipse", minimum=2),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
