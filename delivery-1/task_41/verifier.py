"""
Task 41 — Search bar (IN SCOPE).

Rounded rectangle bar + magnifying glass icon (circle stroke + diagonal line) + 2 dot placeholders.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerIsCircular
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
    id="task_41_search_bar",
    description="Rounded rectangle bar + magnifying-glass icon (circle + diagonal line) + 2 dot placeholders.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle",   equals=1),
            ShapeCountAtLeast("ellipse", minimum=3),
            ShapeCountAtLeast("line",    minimum=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayerHasNoFill(layer_type="ellipse"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            ToolUsed("line"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCountAtLeast("create_ellipse", minimum=3),
            EventTypeCountAtLeast("create_line",    minimum=1),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=40),
)
