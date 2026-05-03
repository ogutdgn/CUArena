"""
Task 15 — Cloud silhouette (in-scope replacement, no boolean union).

4 overlapping ellipses of varying sizes, all the same white fill,
arranged so their tops form a fluffy cloud silhouette.
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
from verifier.checks.geometry_checks import LayersAligned
from verifier.checks.fill_checks   import AllSolidColorEquals
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
    id="task_15_cloud_union",
    description="4 overlapping white ellipses forming a cloud silhouette.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("ellipse", equals=4),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=20.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            AllSolidColorEquals(layer_type="ellipse",
                                expected_rgb={"r": 1.0, "g": 1.0, "b": 1.0},
                                tolerance=0.1),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=4),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
