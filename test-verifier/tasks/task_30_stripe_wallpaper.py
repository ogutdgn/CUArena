"""
Task 30 — Vertical stripe wallpaper (IN SCOPE).

6 vertical stripe rectangles alternating two colors, filling a 600x600 frame.
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
    LayersSameDimensions, LayersAligned, LayersStacked, LayerAspectRatioGreaterThan
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
    id="task_30_stripe_wallpaper",
    description="6 vertical stripes alternating two colors, all same size, in a frame.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=6),
            ShapeCountAtLeast("frame", minimum=1),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
            LayersStacked(layer_type="rectangle", axis="x", gap_px=0.0, tolerance=8.0),
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="vertical"),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=6),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
