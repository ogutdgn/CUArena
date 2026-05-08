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
            ShapeCount("ellipse", equals=4),                                            # 0 ★ prompt: "4 concentric red and white circles"
        ], weight=0.2, critical=[0]),

        AlignmentRubric([
            LayersConcentric(layer_type="ellipse", tolerance=12.0),                     # 0 ★ prompt: "concentric ... centered"
            SmallerLayerInsideLarger(layer_type="ellipse", tolerance=2.0),              # 1 ★ prompt: "decreasing diameters"
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                       # 2 ★ prompt: "circles"
            LayerSizeAtLeast(layer_type="ellipse", min_w=15, min_h=15),                 # 3 no degenerate
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",              # 4 ★ all in frame
                                 tolerance=10.0),
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),          # 5 frame upright (implicit)
            LayerAreaRatioAtLeast(layer_type="ellipse", min_ratio=1.4),                 # 6 outermost > second-largest by ≥1.4x area
        ], weight=0.2, critical=[0, 1, 2, 4]),

        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                     # 0 ★ prompt: every shape needs visible fill
            LayersHaveColorOrder(                                                       # 1 ★ prompt: "Alternate red and white from outermost to center"
                layer_type="ellipse",
                expected_rgbs=[RED, WHITE, RED, WHITE],
                sort_axis="size",
                tolerance=0.20,
            ),
            AllStrokeExists("ellipse"),                                                 # 2 ★ prompt: "each with a 4px black stroke"
            AllStrokeWeightWithinTolerance("ellipse", target_weight=4.0,                # 3 ★ prompt: "4px ... stroke"
                                           tolerance=2.5),
            AllStrokeColorEquals("ellipse", expected_rgb=BLACK, tolerance=0.28),        # 4 ★ prompt: "black stroke"
            FillCountAtMost("ellipse", max_count=1),                                    # 5 no stacked fills
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                             # 6 visible fills
            LayerVisible("ellipse"),                                                    # 7 alpha + visible + opacity
            NoLayerFlipped(layer_type="ellipse"),                                       # 8 no flip
        ], weight=0.2, critical=[0, 1, 2, 3, 4]),

        StructureRubric([
            LayerInsideFrame("ellipse"),                                                # 0 ★ in frame
            ChildCountAtLeast("frame", minimum=4),                                      # 1 ★ prompt: "4 ... circles" all in one frame
        ], weight=0.2, critical=[0, 1]),

        EventRubric([
            ToolUsed("ellipse"),                                                        # 0 prompt mentions tool but keyboard-shortcut OK
            EventTypeCount("create_ellipse", equals=4),
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
