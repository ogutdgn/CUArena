"""
Task 48 — Spiderweb pattern (IN SCOPE).

Navy frame + 6 white radial lines (rotated 60° each) + 3 concentric stroked hexagons.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast, PolygonSidesEquals
from verifier.checks.fill_checks   import FillTypeIs, LayerHasNoFill
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast


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
    id="task_48_spiderweb",
    description="6 radial lines (white) + 3 concentric hexagons (6-sided polygons) on a navy frame.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame",   minimum=1),
            ShapeCountAtLeast("line",    minimum=6),
            ShapeCount("polygon", equals=3),
            PolygonSidesEquals(sides=6),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerHasNoFill(layer_type="polygon"),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("frame", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("line"),
            ToolUsed("polygon"),
            EventTypeCountAtLeast("create_line", minimum=6),
            EventTypeCount("create_polygon", equals=3),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
