"""
Task 33 — 4-section pie chart (IN SCOPE).

Base circle + 3 rotated triangle wedges layered on top in different colors.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount


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
    id="task_33_pie_chart",
    description="Stylized pie chart: 1 base circle + 3 rotated triangle wedges in different colors.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=1),
            ShapeCount("polygon", equals=3),
        ]), max_score=0.34),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            FillTypeIs("polygon", kind="solid"),
        ]), max_score=0.33),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_ellipse", equals=1),
            EventTypeCount("create_polygon", equals=3),
        ]), max_score=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=40),
)
