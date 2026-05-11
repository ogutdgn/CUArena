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
    LayersConcentric, LayersStrictlyNested, LayerIsCircular,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerRotationEquals,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, LayersHaveColorOrder, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    AllStrokeExists, AllStrokeColorEquals, AllStrokeWeightWithinTolerance,
)
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible,
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
            LayersConcentric(layer_type="ellipse", tolerance=25.0),                     # 0 ★ prompt: "all sharing the same center"
            LayersStrictlyNested(layer_type="ellipse", equals=4,                        # 1 ★ prompt: "4 concentric circles with decreasing diameters"
                                 tolerance_px=25.0, min_size_drop_px=4.0),
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                       # 2 ★ prompt: "circles"
            LayerSizeAtLeast(layer_type="ellipse", min_w=15, min_h=15),                 # 3 no degenerate

        ], weight=0.2, critical=[0, 1, 2]),

        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                     # 0 every shape needs visible solid fill
            LayersHaveColorOrder(                                                       # 1 ★ prompt: "Alternate red and white from outermost to center"
                layer_type="ellipse",
                expected_rgbs=[RED, WHITE, RED, WHITE],
                sort_axis="size",
                tolerance=25.0,
            ),
            AllStrokeExists("ellipse"),                                                 # 2 ★ prompt: "each with a 4px black stroke"
            AllStrokeWeightWithinTolerance("ellipse", target_weight=4.0,                # 3 ★ prompt: "4px ... stroke"
                                           tolerance=2.5),
            AllStrokeColorEquals("ellipse", expected_rgb=BLACK, tolerance=0.28),        # 4 ★ prompt: "black stroke"
            FillCountAtMost("ellipse", max_count=1),                                    # 5 no stacked fills
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                             # 6 visible fills
            LayerVisible("ellipse"),                                                    # 7 alpha + visible + opacity
            NoLayerFlipped(layer_type="ellipse"),                                       # 8 no flip
        ], weight=0.2, critical=[1, 2, 3, 4]),

        StructureRubric([

            ChildCountAtLeast("frame", minimum=4),                                      # 1 implicit
        ], weight=0.2, critical=[]),

        EventRubric([
            ToolUsed("ellipse"),                                                        # 0 prompt mentions tool but keyboard-shortcut OK
            EventTypeCount("create_ellipse", equals=4),
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
