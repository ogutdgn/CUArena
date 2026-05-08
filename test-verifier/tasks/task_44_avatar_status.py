"""
Task 44 — Avatar with status badge (in-scope replacement, no image fill).

Large avatar circle + smaller green status badge circle with 2px white stroke,
overlapping at the bottom-right.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersOverlap, LayerOnTopOf, LayerIsCircular, AllLayersAreCircular,
    FrameSizeEquals, AllLayerBoundsInside, LayerSizeAtLeast,
    LayerRotationEquals, AllLayerWidthFraction, LayerSmallerThanLayer,
    FrameCountAtMost, LayerAreaRatioAtLeast,
    SmallerLayerCenteredOnLargerEdge,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, DistinctTypedSolidColors,
    SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeWeightEquals, StrokeColorEquals, StrokeRendersVisible,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.page_checks   import LayerOnPage

GREEN = {"r": 0.06, "g": 0.72, "b": 0.50}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_44_avatar_status",
    description="1 avatar circle + 1 smaller green status circle with 2px white stroke at bottom-right.",
    rubrics=[
        # critical: 2 circles required (avatar + badge)
        FundamentalsRubric([
            ShapeCount("ellipse", equals=2),    # 0 ★ avatar + badge
        ], weight=0.20, critical=[0]),

        # critical: badge overlaps avatar at bottom-right, both circles, smaller-than, etc.
        AlignmentRubric([
            LayersOverlap(type_a="ellipse", type_b="ellipse"),                                   # 0 ★ overlap
            LayerOnTopOf(type_a="ellipse", type_b="ellipse"),                                    # 1 ★ badge on top
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),                                # 2 ★ at least one circle
            AllLayersAreCircular(layer_type="ellipse", tolerance=4.0),                           # 3 ★ EVERY ellipse circular
            FrameSizeEquals(width=1280, height=832, tolerance=10.0),                             # 4 ★ frame size
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=4.0),       # 5 ★ ellipses inside frame
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),                          # 6 ★ no degenerate ellipse
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",                     # 7 ★ sane size
                                  min_frac=0.01, max_frac=0.50),
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=2.0),                 # 8 ★ ellipses upright
            LayerRotationEquals(layer_type="frame",   degrees=0, tolerance=2.0),                 # 9 ★ frame upright
            NoLayerFlipped(layer_type="ellipse"),                                                # 10 ★ not flipped
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="ellipse", max_frac=0.6),   # 11 ★ badge much smaller
            LayerAreaRatioAtLeast(layer_type="ellipse", min_ratio=2.0),                          # 12 ★ avatar dominates
            SmallerLayerCenteredOnLargerEdge(                                                    # 13 ★ badge at bottom-right
                layer_type="ellipse", edge="bottom",
                edge_tolerance=40.0, axis_tolerance=200.0),
            FrameCountAtMost(maximum=1),                                                         # 14 ★ exactly one frame
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]),

        # critical: distinct colors, green badge, white stroke, sane fills
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                          # 0 ★
            DistinctSolidColors(minimum=2, tolerance=0.10),                                  # 1 ★ avatar vs badge
            DistinctTypedSolidColors(layer_type="ellipse", minimum=2, tolerance=0.10),       # 2 ★ ellipses themselves distinct
            SolidColorEquals(layer_type="ellipse", expected_rgb=GREEN, tolerance=0.25),      # 3 ★ green status
            FillCountAtMost("ellipse", max_count=1),                                         # 4 ★ no stacked fills
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                                  # 5 ★ visible fill
            LayerVisible("ellipse"),                                                          # 6 ★ alpha+visible+opacity
            StrokeExists("ellipse"),                                                         # 7 ★ stroke around badge
            StrokeWeightEquals("ellipse", weight=2.0, tolerance=1.0),                        # 8 ★ 2px weight
            StrokeColorEquals("ellipse", expected_rgb=WHITE, tolerance=0.20),                # 9 ★ white stroke
            StrokeRendersVisible("ellipse"),                                                  # 10 ★ stroke renders
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),

        # critical: avatar + badge in same frame on page 0
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=2),  # 0 ★
            LayerOnPage(layer_type="ellipse", page_index=0),            # 1 ★
        ], weight=0.20, critical=[0, 1]),

        # critical: ellipse tool mandated
        EventRubric([
            ToolUsed("ellipse"),                            # 0 ★
            EventTypeCount("create_ellipse", equals=2),     # 1
        ], weight=0.20, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
