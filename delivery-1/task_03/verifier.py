"""
Task 03 — Radial flower with petals (in-scope replacement).

1 yellow center circle + 8 elliptical petals arranged radially around it,
each petal a different color.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import RadialDistributionExcludeCentral
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors, CentermostLayerHasColor
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
    id="task_03_glowing_orb",
    description="1 yellow center circle + 8 elliptical petals arranged radially around it.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=9),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            RadialDistributionExcludeCentral(layer_type="ellipse", n=8, tolerance_deg=15.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            DistinctSolidColors(minimum=8, tolerance=0.05),
            CentermostLayerHasColor(layer_type="ellipse",
                                    expected_rgb={"r": 1.0, "g": 0.9, "b": 0.2},
                                    tolerance=0.20),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=9),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
