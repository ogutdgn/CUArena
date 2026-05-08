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
    LayerIsCircular, AllLayersAreCircular, FrameSizeEquals,
    AllLayerBoundsInside, LayerSizeAtLeast, LayerRotationEquals,
    AllLayerWidthFraction, LayerSmallerThanLayer, FrameCountAtMost,
    LayerInFrontOf,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, AllSolidColorEquals,
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
        # critical: 1 star with 8 points + 1 circle (all explicit)
        FundamentalsRubric([
            ShapeCount("star",    equals=1),    # 0 ★
            StarPointsEquals(points=8),         # 1 ★ 8-point star
            ShapeCount("ellipse", equals=1),    # 2 ★
        ], weight=0.20, critical=[0, 1, 2]),

        # critical: circle inside + centered on star, on top, circular, sane sizing.
        AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="star", tolerance=4.0),       # 0 ★ inside star
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=8.0),            # 1 ★ centered
            LayerOnTopOf(type_a="ellipse", type_b="star"),                                   # 2 ★ on top (overlap)
            LayerInFrontOf(type_a="ellipse", type_b="star"),                                 # 3 ★ z-order
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),                            # 4 ★ at-least-one round
            AllLayersAreCircular(layer_type="ellipse", tolerance=4.0),                       # 5 ★ EVERY ellipse circular
            FrameSizeEquals(width=1280, height=832, tolerance=10.0),                         # 6 ★ frame size
            AllLayerBoundsInside(inner_type="star", outer_type="frame", tolerance=4.0),      # 7 ★ star in frame
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=4.0),   # 8 ★ ellipse in frame
            LayerSizeAtLeast(layer_type="star",    min_w=40, min_h=40),                      # 9 ★ no degenerate star
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),                      # 10 ★ no degenerate circle
            AllLayerWidthFraction(inner_type="star", parent_type="frame",                    # 11 ★ star sane size
                                  min_frac=0.05, max_frac=0.50),
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",                 # 12 ★ circle sane
                                  min_frac=0.02, max_frac=0.40),
            LayerRotationEquals(layer_type="star",    degrees=0, tolerance=2.0),             # 13 ★ star upright
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=2.0),             # 14 ★ circle upright
            LayerRotationEquals(layer_type="frame",   degrees=0, tolerance=2.0),             # 15 ★ frame upright
            NoLayerFlipped(layer_type="star"),                                               # 16 ★ star not mirrored
            NoLayerFlipped(layer_type="ellipse"),                                            # 17 ★ circle not mirrored
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="star", max_frac=0.85), # 18 ★ circle smaller than star
            FrameCountAtMost(maximum=1),                                                     # 19 ★ exactly one frame
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]),

        # critical: deep blue star, yellow circle (specific colors)
        ColorRubric([
            AllFillTypeIs("star",    kind="solid"),                                          # 0 ★
            AllFillTypeIs("ellipse", kind="solid"),                                          # 1 ★
            AllSolidColorEquals(layer_type="star",    expected_rgb=DEEP_BLUE, tolerance=0.20),# 2 ★ deep blue
            AllSolidColorEquals(layer_type="ellipse", expected_rgb=YELLOW,    tolerance=0.20),# 3 ★ yellow
            FillCountAtMost("star",    max_count=1),                                         # 4 ★ no stacked fills
            FillCountAtMost("ellipse", max_count=1),                                         # 5 ★ no stacked fills
            FillOpacityAtLeast("star",    min_opacity=0.5),                                  # 6 ★ visible
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                                  # 7 ★ visible
            LayerVisible("star"),                                                             # 8 ★ alpha+visible+opacity
            LayerVisible("ellipse"),                                                          # 9 ★
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),

        # critical: shapes in same frame on page 0
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="star",    minimum=1),  # 0 ★
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=1),  # 1 ★
            LayerOnPage(layer_type="star",    page_index=0),            # 2 ★
            LayerOnPage(layer_type="ellipse", page_index=0),            # 3 ★
        ], weight=0.20, critical=[0, 1, 2, 3]),

        # critical: star + ellipse tools used
        EventRubric([
            ToolUsed("star"),                               # 0 ★
            ToolUsed("ellipse"),                            # 1 ★
            EventTypeCount("create_star",    equals=1),     # 2
            EventTypeCount("create_ellipse", equals=1),     # 3
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
