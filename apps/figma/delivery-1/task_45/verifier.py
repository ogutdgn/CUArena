"""
Task 45 — Layered geometric emblem (IN SCOPE).

Deep-blue 8-point star + smaller centered yellow circle on top.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals
from verifier.checks.geometry_checks import (
    LayerBoundsInside, LayerCenteredOnLayer, LayerOnTopOf,
    LayerIsCircular, FrameSizeEquals,
    AllLayerBoundsInside, LayerSizeAtLeast, LayerRotationEquals,
    LayerSmallerThanLayer, FrameCountAtMost,
    LayerInFrontOf,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, AllSolidColorEquals,
    FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.page_checks   import LayerOnPage

DEEP_BLUE = {"r": 0.10, "g": 0.20, "b": 0.60}
YELLOW    = {"r": 1.0,  "g": 0.85, "b": 0.20}

task = Task(
    id="task_45_geometric_emblem",
    description="Deep-blue 8-point star + smaller yellow circle centered on top.",
    rubrics=[
        # critical: 8-point star + 1 circle (both shape counts + star points are explicit)
        FundamentalsRubric([
            ShapeCount("star",    equals=1),    # 0 single-star count
            StarPointsEquals(points=8),         # 1 ★ prompt: "8-point ... star"
            ShapeCount("ellipse", equals=1),    # 2 ★ prompt: "smaller centered yellow circle"
        ], weight=0.20, critical=[1, 2]),

        # critical: smaller circle, centered on star, on top.
        AlignmentRubric([
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=20.0),           # 0 ★ prompt: "both centered together"
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="star", max_frac=0.85),# 1 ★ prompt: "smaller ... circle"
            LayerInFrontOf(type_a="ellipse", type_b="star"),                                 # 2 ★ prompt: "circle on top"
            LayerOnTopOf(type_a="ellipse", type_b="star"),                                   # 3 z-overlap
            LayerBoundsInside(inner_type="ellipse", outer_type="star", tolerance=10.0),      # 4 circle inside star
            LayerIsCircular(layer_type="ellipse", tolerance=4.0),                            # 5 ★ prompt: "circle"
            FrameSizeEquals(width=1280, height=832, tolerance=25.0),                         # 6 frame size
            AllLayerBoundsInside(inner_type="star", outer_type="frame", tolerance=10.0),     # 7 star inside frame
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=10.0),  # 8 ellipse inside frame
            LayerSizeAtLeast(layer_type="star",    min_w=40, min_h=40),                      # 9 no degenerate star
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),                      # 10 no degenerate circle
            LayerRotationEquals(layer_type="star",    degrees=0, tolerance=5.0),             # 11 star upright
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),             # 12 circle upright
            NoLayerFlipped(layer_type="star"),                                               # 13 star not mirrored
            NoLayerFlipped(layer_type="ellipse"),                                            # 14 circle not mirrored
            FrameCountAtMost(maximum=1),                                                     # 15 exactly one frame
        ], weight=0.20, critical=[0, 1, 2, 5]),

        # critical: deep blue star, yellow circle (specific colors)
        ColorRubric([
            AllFillTypeIs("star",    kind="solid"),                                           # 0 ★ visible solid star
            AllFillTypeIs("ellipse", kind="solid"),                                           # 1 visible solid ellipse
            AllSolidColorEquals(layer_type="star",    expected_rgb=DEEP_BLUE, tolerance=0.28),# 2 ★ prompt: "deep blue fill"
            AllSolidColorEquals(layer_type="ellipse", expected_rgb=YELLOW,    tolerance=0.28),# 3 ★ prompt: "yellow fill"
            FillCountAtMost("star", max_count=1),                                             # 4 no stacked fills
            FillOpacityAtLeast("star", min_opacity=0.5),                                      # 5 visible fill
            LayerVisible("star"),                                                             # 6 alpha+visible+opacity
        ], weight=0.20, critical=[0, 2, 3]),

        # structural: shapes in same frame on page 0
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="star",    minimum=1),  # 0 ★ shapes share one frame
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=1),  # 1 ellipse in same frame
            LayerOnPage(layer_type="star",    page_index=0),            # 2 star on page 0
            LayerOnPage(layer_type="ellipse", page_index=0),            # 3 ellipse on page 0
        ], weight=0.20, critical=[0]),

        # critical: star + ellipse tools used
        EventRubric([
            ToolUsed("star"),                               # 0 ★ prompt: "Click Star tool"
            ToolUsed("ellipse"),                            # 1 ★ prompt: "Click Ellipse tool"
            EventTypeCount("create_star",    equals=1),     # 2
            EventTypeCount("create_ellipse", equals=1),     # 3
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
