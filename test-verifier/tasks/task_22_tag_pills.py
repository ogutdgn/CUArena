"""
Task 22 — Tag pill row (in-scope replacement, no auto-layout).

4 same-size rounded rectangles (radius 999) placed manually side-by-side
in a horizontal row, each filled a different pastel color.
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
from verifier.checks.geometry_checks import LayersSameDimensions, LayersAligned
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.property_checks import CornerRadiusAtLeast
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
    id="task_22_tag_pills",
    description="4 same-size rounded rectangles (radius 999) in a horizontal row, different pastel fills.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=4),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=24.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=4, tolerance=0.05),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=4),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
