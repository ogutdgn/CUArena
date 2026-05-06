"""
Task 32 — 4-blade pinwheel (IN SCOPE).

4 triangles rotated radially (alternating two colors) + small center pivot circle.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersSameDimensions, RadialDistribution, LayersEvenlyRotated, LayerIsCircular
)
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
    id="task_32_pinwheel",
    description="4 triangles rotated radially around a small center circle, alternating two colors.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("polygon", equals=4),
            ShapeCount("ellipse", equals=1),
            ShapeCountAtLeast("frame", minimum=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=3.0),
            RadialDistribution(layer_type="polygon", n=4, tolerance_deg=15.0),
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=8.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("polygon", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("polygon"),
            EventTypeCount("create_polygon", equals=4),
            EventTypeCount("create_ellipse", equals=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=25),
)
