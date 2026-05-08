"""
Task 14 — Concentric ring target / dartboard (IN SCOPE).

4 concentric circles, alternating red/white outermost-to-center,
all centered on each other, each with a 4px black stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersConcentric, SmallerLayerInsideLarger, LayerIsCircular,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerRotationEquals,
    LayersSameDimensions, LayerAreaRatioAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, LayersHaveColorOrder, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeWeightEquals, StrokeColorEquals,
    AllStrokeExists, AllStrokeColorEquals, AllStrokeWeightWithinTolerance,
)
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible, LayerRendersStrokeOrFill,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

RED   = {"r": 0.9, "g": 0.15, "b": 0.15}
WHITE = {"r": 1.0, "g": 1.0,  "b": 1.0}
BLACK = {"r": 0.0, "g": 0.0,  "b": 0.0}

task = Task(
    id="task_14_concentric_target",
    description="4 concentric ellipses alternating red/white outermost→center, each with 4px black stroke.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),                                            # 0 ★ "4 concentric ... circles"
        ], weight=0.2, critical=[0]),

        AlignmentRubric([
            LayersConcentric(layer_type="ellipse", tolerance=2.0),                      # 0 ★ "concentric"
            SmallerLayerInsideLarger(layer_type="ellipse", tolerance=2.0),              # 1 ★ "decreasing diameters"
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),                       # 2 ★ "circles"
            LayerSizeAtLeast(layer_type="ellipse", min_w=15, min_h=15),                 # 3 ★ no degenerate
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",              # 4 ★ all in frame
                                 tolerance=4.0),
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),          # 5 ★ frame upright
            LayerAreaRatioAtLeast(layer_type="ellipse", min_ratio=1.4),                 # 6 ★ outermost > second-largest by ≥1.4x area
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6]),

        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                     # 0 ★ solid fills
            LayersHaveColorOrder(                                                       # 1 ★ "Alternate red and white from outermost to center"
                layer_type="ellipse",
                expected_rgbs=[RED, WHITE, RED, WHITE],
                sort_axis="size",
                tolerance=0.20,
            ),
            AllStrokeExists("ellipse"),                                                 # 2 ★ EVERY ellipse has stroke ("each with...")
            AllStrokeWeightWithinTolerance("ellipse", target_weight=4.0,                # 3 ★ EVERY ellipse stroke=4px
                                           tolerance=1.0),
            AllStrokeColorEquals("ellipse", expected_rgb=BLACK, tolerance=0.20),        # 4 ★ EVERY ellipse stroke is black
            FillCountAtMost("ellipse", max_count=1),                                    # 5 ★ no stacked fills
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                             # 6 ★ visible fills
            LayerVisible("ellipse"),                                                    # 7 ★ alpha + visible + opacity
            NoLayerFlipped(layer_type="ellipse"),                                       # 8 ★ no flip
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        StructureRubric([
            LayerInsideFrame("ellipse"),                                                # 0 ★ in frame
            ChildCountAtLeast("frame", minimum=4),                                      # 1 ★ all 4 in one frame
        ], weight=0.2, critical=[0, 1]),

        EventRubric([
            ToolUsed("ellipse"),                                                        # 0 ★ ellipse tool mandated
            EventTypeCount("create_ellipse", equals=4),
        ], weight=0.2, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
