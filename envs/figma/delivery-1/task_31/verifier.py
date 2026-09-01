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
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersEvenlyRotated, RadialDistribution, LayerIsCircular,
    LayerRotationEquals, AllLayerBoundsInside, LayerSizeAtLeast,
    AllLayerWidthFraction, LayerCenteredOnLayerSetCentroid,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals,
)
from verifier.checks.property_checks import NoLayerFlipped
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

YELLOW = {"r": 1.0, "g": 0.9, "b": 0.2}

task = Task(
    id="task_31_sun_rays",
    description="Yellow center circle + 4 triangle rays rotated 90° apart (radial sun).",
    rubrics=[
        # critical: 1 circle + 4 triangle rays inside a frame (prompt-explicit counts + shape)
        FundamentalsRubric([
            ShapeCount("ellipse", equals=1),                                    # 0 ★ prompt: "a yellow center circle"
            ShapeCount("polygon", equals=4),                                    # 1 ★ prompt: "4 thin triangle rays"
            ShapeCountAtLeast("frame", minimum=1),                              # 2 ★ prompt: "Inside a frame"
            PolygonSidesEquals(sides=3),                                         # 3 ★ prompt: "triangle rays"
        ], weight=0.2, critical=[0, 1, 3]),

        # critical: round center, rays evenly rotated 90° apart, radial layout around circle
        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=25.0),          # 0 same-size rays
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),               # 1 ★ prompt: "circle"
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=10.0),  # 2 ★ prompt: "rotated 90° apart"
            RadialDistribution(layer_type="polygon", n=4, tolerance_deg=15.0),  # 3 ★ prompt: "around it ... 12 o'clock, 3 o'clock, 6 o'clock, 9 o'clock"
            LayerCenteredOnLayerSetCentroid(type_a="ellipse", type_b="polygon", tolerance=20.0),  # 4 ★ prompt: "rays around it"
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),  # 5

            NoLayerFlipped(layer_type="ellipse"),                                  # 7
            NoLayerFlipped(layer_type="polygon"),                                  # 8
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),            # 9
            LayerSizeAtLeast(layer_type="polygon", min_w=15, min_h=15),            # 10
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",
                                  min_frac=0.02, max_frac=0.40),                   # 11
            AllLayerWidthFraction(inner_type="polygon", parent_type="frame",
                                  min_frac=0.02, max_frac=0.30),                   # 12

        ], weight=0.2, critical=[1, 2, 3, 4]),

        # critical: yellow center circle
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                             # 0 solid fill
            AllFillTypeIs("polygon", kind="solid"),                             # 1 solid fill
            SolidColorEquals(layer_type="ellipse", expected_rgb=YELLOW, tolerance=0.28),  # 2 ★ prompt: "yellow ... circle"
        ], weight=0.2, critical=[2]),

        # both circle and rays inside frame (structural)
        StructureRubric([

        ], weight=0.2, critical=[0]),

        # ellipse + polygon tools both used
        EventRubric([
            ToolUsed("ellipse"),                                                # 0
            ToolUsed("polygon"),                                                # 1
            EventTypeCount("create_ellipse", equals=1),                         # 2
            EventTypeCount("create_polygon", equals=4),                         # 3
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
