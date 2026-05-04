"""
Task 47 — Sunburst stamp badge (IN SCOPE).

16-point star with inner radius ~70% (soft sunburst look) + smaller centered cream circle.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals, StarInnerRatioEquals
from verifier.checks.geometry_checks import LayerCenteredOnLayer
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
    id="task_47_sunburst_badge",
    description="16-point star with inner radius ~70% + smaller cream circle centered on top.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("star",    equals=1),
            StarPointsEquals(points=16),
            StarInnerRatioEquals(ratio=0.70, tolerance=0.05),
            ShapeCount("ellipse", equals=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=8.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("star",    kind="solid"),
            FillTypeIs("ellipse", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("star"),
            ToolUsed("ellipse"),
            EventTypeCount("create_star",    equals=1),
            EventTypeCount("create_ellipse", equals=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
