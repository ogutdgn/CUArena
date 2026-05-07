"""
Task 31 — Simple sun (SIMPLIFIED Medium → Easy).

Yellow center circle + 4 triangle rays evenly rotated at 90° intervals around it.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersEvenlyRotated, RadialDistribution, LayerIsCircular
)
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

YELLOW = {"r": 1.0, "g": 0.9, "b": 0.2}

task = Task(
    id="task_31_sun_rays",
    description="Yellow center circle + 4 triangle rays rotated 90° apart (radial sun).",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=1),
            ShapeCount("polygon", equals=4),
            ShapeCountAtLeast("frame", minimum=1),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=4.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=10.0),
            RadialDistribution(layer_type="polygon", n=4, tolerance_deg=15.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            FillTypeIs("polygon", kind="solid"),
            SolidColorEquals(layer_type="ellipse", expected_rgb=YELLOW, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_ellipse", equals=1),
            EventTypeCount("create_polygon", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
