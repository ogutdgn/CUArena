"""
Task 19 — Padlock icon (IN SCOPE).

Rectangle body (rounded corner radius 12, dark gray) + pen-drawn U-shaped
shackle (14px stroke) above + small black keyhole circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayerBoundsInside, LayerIsCircular,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerRotationEquals,
    FrameCountAtMost, LayerSmallerThanLayer, LayerNextTo,
    LayerCenteredOnLayer,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost,
)
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeWeightEquals, StrokeColorEquals,
    AllLayerStrokeVisible, StrokeRendersVisible,
)
from verifier.checks.property_checks import (
    CornerRadiusEquals, LayerVisible, NoLayerFlipped,
    CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import (
    LayerInsideFrame, LayerGroupAllInSameFrame, LayerTotalCount,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

DARK_GRAY = {"r": 0.30, "g": 0.30, "b": 0.30}
BLACK     = {"r": 0.0,  "g": 0.0,  "b": 0.0}

task = Task(
    id="task_19_padlock",
    description="Rounded rectangle body (radius 12, dark gray) + pen U-shackle (14px stroke) + black keyhole circle.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),                                          # 0 ★ prompt: "rectangle body"
            ShapeCount("vector",    equals=1),                                          # 1 ★ prompt: "pen-tool U-shackle"
            ShapeCount("ellipse",   equals=1),                                          # 2 ★ prompt: "keyhole" (small circle)
            LayerTotalCount(equals=4),                                                  # 3 1 rect + 1 vec + 1 ell + 1 frame = 4
        ], weight=0.20, critical=[0, 1, 2]),

        AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="rectangle",             # 0 ★ prompt: "keyhole in the center of the body"
                              tolerance=10.0),
            LayerCenteredOnLayer(type_a="ellipse", type_b="rectangle",                  # 1 ★ prompt: "keyhole in the center of the body"
                                 tolerance=20.0, axis="both"),
            LayerNextTo(type_a="vector", type_b="rectangle", side="above",              # 2 ★ prompt: "drawn above" the body
                        tolerance=30.0),
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                       # 3 prompt: "small circle keyhole"
            CornerRadiusEquals(layer_type="rectangle", radius=12.0, tolerance=4.0),     # 4 prompt: "scrub corner radius to 12"
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="rectangle",      # 5 keyhole "small" ≤ 0.4 of body
                                  max_frac=0.85),
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),      # 6 body not rotated
            LayerRotationEquals(layer_type="ellipse",   degrees=0, tolerance=5.0),      # 7 keyhole not rotated
            LayerRotationEquals(layer_type="vector",    degrees=0, tolerance=10.0),     # 8 shackle U-shape not flipped
        ], weight=0.20, critical=[0, 1, 2]),

        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                   # 0 ★ every shape needs a visible solid fill
            FillCountAtMost(layer_type="rectangle", max_count=1),                       # 1 stacked-fill blocked
            FillCountAtMost(layer_type="ellipse",   max_count=1),                       # 2 stacked-fill blocked
            SolidColorEquals(layer_type="rectangle", expected_rgb=DARK_GRAY,            # 3 ★ prompt: "Body is dark gray"
                             tolerance=0.28),
            SolidColorEquals(layer_type="ellipse",   expected_rgb=BLACK,                # 4 ★ prompt: "keyhole is black"
                             tolerance=0.28),
            StrokeExists("vector"),                                                     # 5 prompt: "14px stroke"
            StrokeWeightEquals("vector", weight=14.0, tolerance=2.5),                   # 6 prompt: "14px"
            StrokeRendersVisible(layer_type="vector", min_alpha=0.5),                   # 7 shackle stroke must render
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),       # 8 body visible
            LayerVisible(layer_type="ellipse",   min_opacity=0.5, min_alpha=0.5),       # 9 keyhole visible
        ], weight=0.20, critical=[0, 3, 4]),

        StructureRubric([
            LayerInsideFrame(layer_type="rectangle"),                                   # 0 ★ rectangle in frame
            LayerInsideFrame(layer_type="vector"),                                      # 1 vector in frame
            LayerInsideFrame(layer_type="ellipse"),                                     # 2 ellipse in frame
            LayerGroupAllInSameFrame(layer_type="rectangle", minimum=1),                # 3
            LayerGroupAllInSameFrame(layer_type="vector",    minimum=1),                # 4
            LayerGroupAllInSameFrame(layer_type="ellipse",   minimum=1),                # 5
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",            # 6
                                 tolerance=10.0),
            AllLayerBoundsInside(inner_type="ellipse",   outer_type="frame",            # 7
                                 tolerance=10.0),
            LayerSizeAtLeast(layer_type="rectangle", min_w=80, min_h=60),               # 8 body sized for icon
            LayerSizeAtLeast(layer_type="ellipse",   min_w=8,  min_h=8),                # 9
            LayerSizeAtLeast(layer_type="vector",    min_w=40, min_h=40),               # 10
            NoLayerFlipped(layer_type="rectangle"),                                     # 11
            NoLayerFlipped(layer_type="ellipse"),                                       # 12
            FrameCountAtMost(maximum=1),                                                # 13
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),          # 14
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),           # 15 body not pill-shaped
        ], weight=0.20, critical=[0]),

        EventRubric([
            ToolUsed("rectangle"),                                                      # 0 rectangle tool used
            ToolUsed("pen"),                                                            # 1 pen tool used
            ToolUsed("ellipse"),                                                        # 2 ellipse tool used
            EventTypeCount("create_rectangle", equals=1),                               # 3 exact count
            EventTypeCount("create_vector",    equals=1),                               # 4
            EventTypeCount("create_ellipse",   equals=1),                               # 5
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
