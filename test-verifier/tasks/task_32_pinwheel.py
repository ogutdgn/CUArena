"""
Task 32 — 4-blade pinwheel (IN SCOPE).

4 triangles rotated radially (alternating two colors) + small center pivot circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersSameDimensions, RadialDistribution, LayersEvenlyRotated,
    LayerIsCircular, LayersAlternatingColors,
)
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_32_pinwheel",
    description="4 triangles rotated 90° apart, alternating two colors, around a small center circle.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon", equals=4),
            ShapeCount("ellipse", equals=1),
            ShapeCountAtLeast("frame", minimum=1),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=3.0),
            RadialDistribution(layer_type="polygon", n=4, tolerance_deg=15.0),
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=8.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("polygon", kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.10),
            LayersAlternatingColors(layer_type="polygon", n_colors=2, sort_axis="x", tolerance=0.15),
        ], weight=0.25),

        EventRubric([
            ToolUsed("polygon"),
            EventTypeCount("create_polygon", equals=4),
            EventTypeCount("create_ellipse", equals=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
