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
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible,
)
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

YELLOW = {"r": 1.0, "g": 0.9, "b": 0.2}

task = Task(
    id="task_31_sun_rays",
    description="Yellow center circle + 4 triangle rays rotated 90° apart (radial sun).",
    rubrics=[
        # critical: 1 circle + 4 rays inside a frame (prompt-explicit counts)
        FundamentalsRubric([
            ShapeCount("ellipse", equals=1),                                    # 0 ★ "a yellow center circle"
            ShapeCount("polygon", equals=4),                                    # 1 ★ "4 thin triangle rays"
            ShapeCountAtLeast("frame", minimum=1),                              # 2 ★ "Inside a frame"
            PolygonSidesEquals(sides=3),                                         # 3 ★ "triangle rays"
        ], weight=0.2, critical=[0, 1, 2, 3]),

        # critical: round center, rays evenly rotated 90° apart, radial layout, sane size, on-frame
        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=4.0),          # 0 ★
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),               # 1 ★ "circle"
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=10.0),  # 2 ★ "rotated 90°"
            RadialDistribution(layer_type="polygon", n=4, tolerance_deg=15.0),  # 3 ★ "around it / 12,3,6,9"
            LayerCenteredOnLayerSetCentroid(type_a="ellipse", type_b="polygon", tolerance=20.0),  # 4 ★ rays around circle
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=2.0),  # 5 ★ circle upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),    # 6 ★ frame upright
            NoLayerFlipped(layer_type="ellipse"),                                  # 7 ★ circle not flipped
            NoLayerFlipped(layer_type="polygon"),                                  # 8 ★ rays not flipped
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),            # 9 ★ no tiny circle
            LayerSizeAtLeast(layer_type="polygon", min_w=15, min_h=15),            # 10 ★ no tiny rays
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",
                                  min_frac=0.02, max_frac=0.40),                   # 11 ★ circle-vs-frame size
            AllLayerWidthFraction(inner_type="polygon", parent_type="frame",
                                  min_frac=0.02, max_frac=0.30),                   # 12 ★ rays-vs-frame size
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=4.0),  # 13 ★ circle in frame
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame", tolerance=4.0),  # 14 ★ rays in frame
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]),

        # critical: solid fills + yellow center circle + visible
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                             # 0 ★
            AllFillTypeIs("polygon", kind="solid"),                             # 1 ★
            SolidColorEquals(layer_type="ellipse", expected_rgb=YELLOW, tolerance=0.20),  # 2 ★ "yellow"
            FillCountAtMost(layer_type="ellipse", max_count=1),                 # 3 ★ no stacked fills on circle
            FillCountAtMost(layer_type="polygon", max_count=1),                 # 4 ★ no stacked fills on rays
            FillOpacityAtLeast(layer_type="ellipse", min_opacity=0.5),          # 5 ★ circle visible
            FillOpacityAtLeast(layer_type="polygon", min_opacity=0.5),          # 6 ★ rays visible
            LayerVisible(layer_type="ellipse"),                                 # 7 ★ alpha + visibility
            LayerVisible(layer_type="polygon"),                                 # 8 ★ alpha + visibility
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        # both circle and rays inside frame (structural)
        StructureRubric([
            LayerInsideFrame("ellipse"),                                        # 0 ★
            LayerInsideFrame("polygon"),                                        # 1 ★
        ], weight=0.2, critical=[0, 1]),

        # critical: ellipse + polygon tools both used
        EventRubric([
            ToolUsed("ellipse"),                                                # 0 ★
            ToolUsed("polygon"),                                                # 1 ★
            EventTypeCount("create_ellipse", equals=1),                         # 2
            EventTypeCount("create_polygon", equals=4),                         # 3
        ], weight=0.2, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
