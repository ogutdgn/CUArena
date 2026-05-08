"""
Task 16 — Speech bubble visual (in-scope replacement, no boolean).

Rounded rectangle (light gray) + small triangle tail (same fill), both with
a 2px dark-gray stroke. Body and tail overlap to form a speech bubble.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersOverlap, LayerSizeAtLeast, AllLayerBoundsInside,
    LayerRotationEquals, LayerAreaRatioAtLeast, AllLayerWidthFraction,
    CrossTypeAreaRatioAtLeast,
)
from verifier.checks.fill_checks   import (
    AllSolidColorEquals, SameColorAcrossTypes, AllFillTypeIs,
    FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeWeightEquals, StrokeColorEquals,
    AllStrokeExists, AllStrokeColorEquals, AllStrokeWeightWithinTolerance,
)
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, NoLayerFlipped, LayerVisible,
    CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

LIGHT_GRAY = {"r": 0.85, "g": 0.85, "b": 0.85}
DARK_GRAY  = {"r": 0.30, "g": 0.30, "b": 0.30}

task = Task(
    id="task_16_speech_bubble",
    description="Rounded rectangle bubble + small triangle tail, both light gray with 2px dark-gray stroke.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),                                          # 0 ★ "rounded rectangle"
            ShapeCount("polygon",   equals=1),                                          # 1 ★ "small triangle tail"
            PolygonSidesEquals(sides=3),                                                # 2 ★ "triangle"
        ], weight=0.2, critical=[0, 1, 2]),

        AlignmentRubric([
            LayersOverlap(type_a="rectangle", type_b="polygon"),                        # 0 ★ prompt: "slightly overlapping"
            CornerRadiusAtLeast(layer_type="rectangle", min_value=8.0),                 # 1 ★ prompt: "rounded rectangle"
            LayerSizeAtLeast(layer_type="rectangle", min_w=40, min_h=40),               # 2 no degenerate bubble
            LayerSizeAtLeast(layer_type="polygon", min_w=15, min_h=15),                 # 3 no degenerate tail
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",            # 4 rect in frame
                                 tolerance=10.0),
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame",              # 5 tail in frame
                                 tolerance=10.0),
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),      # 6 bubble upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),          # 7 frame upright
            AllLayerWidthFraction(inner_type="rectangle", parent_type="frame",          # 8 rect-vs-frame size sane
                                  min_frac=0.05, max_frac=0.80),
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),           # 9 no full pill
            CrossTypeAreaRatioAtLeast(big_type="rectangle", small_type="polygon",       # 10 ★ prompt: "small triangle tail" (bubble dominates)
                                      min_ratio=2.0),
            LayerRotationEquals(layer_type="polygon", degrees=0, tolerance=5.0),        # 11 tail upright
        ], weight=0.2, critical=[0, 1, 10]),

        ColorRubric([
            AllSolidColorEquals(layer_type="rectangle", expected_rgb=LIGHT_GRAY,        # 0 ★ prompt: "light gray"
                                tolerance=0.28),
            AllSolidColorEquals(layer_type="polygon",   expected_rgb=LIGHT_GRAY,        # 1 ★ prompt: "light gray"
                                tolerance=0.28),
            SameColorAcrossTypes(types=["rectangle", "polygon"], tolerance=0.15),       # 2 ★ prompt: "Both filled the same"
            AllFillTypeIs("rectangle", kind="solid"),                                   # 3 ★ no image/gradient
            AllFillTypeIs("polygon",   kind="solid"),                                   # 4 ★ no image/gradient
            FillCountAtMost("rectangle", max_count=1),                                  # 5 no stacked fills
            FillCountAtMost("polygon",   max_count=1),                                  # 6
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                           # 7
            FillOpacityAtLeast("polygon",   min_opacity=0.5),                           # 8
            LayerVisible("rectangle"),                                                  # 9 alpha + visible
            LayerVisible("polygon"),                                                    # 10
            NoLayerFlipped(layer_type="rectangle"),                                     # 11
            NoLayerFlipped(layer_type="polygon"),                                       # 12
            AllStrokeExists("rectangle"),                                               # 13
            AllStrokeExists("polygon"),                                                 # 14
            AllStrokeWeightWithinTolerance("rectangle", target_weight=2.0,              # 15
                                            tolerance=2.5),
            AllStrokeWeightWithinTolerance("polygon", target_weight=2.0,                # 16
                                            tolerance=2.5),
            AllStrokeColorEquals("rectangle", expected_rgb=DARK_GRAY, tolerance=0.28),  # 17
            AllStrokeColorEquals("polygon", expected_rgb=DARK_GRAY, tolerance=0.28),    # 18
        ], weight=0.2, critical=[0, 1, 2, 3, 4]),

        StructureRubric([
            LayerInsideFrame("rectangle"),                                              # 0 ★ rect in frame
            LayerInsideFrame("polygon"),                                                # 1 ★ poly in frame
            ChildCountAtLeast("frame", minimum=2),                                      # 2 both inside one frame
        ], weight=0.2, critical=[0, 1]),

        EventRubric([
            ToolUsed("rectangle"),                                                      # 0 rectangle tool used
            ToolUsed("polygon"),                                                        # 1 polygon tool used
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_polygon",   equals=1),
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
