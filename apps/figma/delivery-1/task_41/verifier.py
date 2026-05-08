"""
Task 41 — Search bar (SIMPLIFIED Medium → Easy).

320×48 rounded light-gray bar + magnifying-glass icon (small stroked circle +
diagonal line) + 2 placeholder dots.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayerIsCircular, LayerSizeEquals, LayerSizeAtLeast,
    AllLayerBoundsInside, LayerRotationEquals, LayerBoundsInside,
    LayerCenteredOnLayer, LayerAspectRatioGreaterThan, CrossTypeAreaRatioAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeWeightEquals, VisibleStrokeExists, AllLayerStrokeVisible,
)
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, NoLayerFlipped, LayerVisible,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast
from verifier.checks.structure_checks import LayerInsideFrame

LIGHT_GRAY = {"r": 0.95, "g": 0.95, "b": 0.95}

task = Task(
    id="task_41_search_bar",
    description="320×48 rounded light-gray bar + small magnifier (stroked circle + line) + dots.",
    rubrics=[
        # critical: prompt mandates 1 bar + magnifier + dots + diagonal line, no degenerate
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),                            # 0 ★ "rounded rectangle bar"
            ShapeCountAtLeast("ellipse", minimum=2),                      # 1 ★ magnifier ring + ≥1 dot
            ShapeCountAtLeast("line", minimum=1),                         # 2 ★ "thin diagonal line"
            LayerSizeAtLeast(layer_type="rectangle", min_w=20, min_h=10), # 3 ★ no degenerate bar
            LayerSizeAtLeast(layer_type="ellipse",   min_w=4,  min_h=4), # 4 ★ no 1×1 ellipse
            LayerSizeAtLeast(layer_type="line",      min_w=4,  min_h=0), # 5 ★ no 1px line
            NoLayerFlipped(layer_type="rectangle"),                      # 6 ★ bar not mirrored
        ], weight=0.16, critical=[0, 1, 2, 3, 4, 5, 6]),

        # critical: rounded bar + circular magnifier ring; everything inside frame
        AlignmentRubric([
            LayerSizeEquals(layer_type="rectangle", width=320, height=48, tolerance=12.0),  # 0
            CornerRadiusAtLeast(layer_type="rectangle", min_value=20.0),                    # 1 ★ "rounded rectangle"
            LayerIsCircular(layer_type="ellipse", tolerance=4.0),                            # 2 ★ "small circle"
            LayerRotationEquals(layer_type="rectangle", degrees=0.0, tolerance=2.0),         # 3 ★ bar upright
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=2.0),             # 4 ★ frame upright
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=8.0), # 5 ★ bar inside frame
            AllLayerBoundsInside(inner_type="ellipse",   outer_type="frame", tolerance=8.0), # 6 ★ ellipses in frame
            AllLayerBoundsInside(inner_type="line",      outer_type="frame", tolerance=8.0), # 7 ★ line inside frame
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="horizontal"),# 8 ★ bar wider than tall
            CrossTypeAreaRatioAtLeast(big_type="frame", small_type="rectangle",              # 9 ★ bar smaller than frame
                                       min_ratio=2.0),
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),

        # critical: light-gray bar + stroked magnifier ring are prompt-explicit
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                              # 0 ★
            SolidColorEquals(layer_type="rectangle", expected_rgb=LIGHT_GRAY, tolerance=0.10),     # 1 ★ "light-gray"
            StrokeExists("ellipse"),                                                                # 2 ★ "circle with stroke"
            StrokeWeightEquals("ellipse", weight=2.0, tolerance=1.0),                               # 3 ★ "2px"
            VisibleStrokeExists("ellipse"),                                                         # 4 ★ stroke visible
            AllLayerStrokeVisible(layer_type="ellipse", min_alpha=0.1, min_weight=0.5),             # 5 ★ ALL ellipses have stroke (dots+glass)
            FillCountAtMost(layer_type="rectangle", max_count=1),                                   # 6 ★ no stacked fills
            LayerVisible(layer_type="rectangle"),                                                   # 7 ★ bar visible
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),                            # 8 ★
            VisibleStrokeExists("line"),                                                            # 9 ★ line stroke visible
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),

        # structure: shapes inside a frame
        StructureRubric([
            LayerInsideFrame(layer_type="rectangle"),                                          # 0 ★
            LayerInsideFrame(layer_type="ellipse"),                                            # 1 ★
            LayerInsideFrame(layer_type="line"),                                               # 2 ★
        ], weight=0.10, critical=[0, 1, 2]),

        # critical: must use rectangle, ellipse, and line tools
        EventRubric([
            ToolUsed("rectangle"),                                # 0 ★
            ToolUsed("ellipse"),                                  # 1 ★
            ToolUsed("line"),                                     # 2 ★
            EventTypeCount("create_rectangle", equals=1),         # 3
            EventTypeCountAtLeast("create_ellipse", minimum=2),   # 4
            EventTypeCountAtLeast("create_line", minimum=1),      # 5
        ], weight=0.18, critical=[0, 1, 2]),

        # property: catch ellipses/lines inside the bar (or near)
        FundamentalsRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="rectangle", tolerance=40.0),  # 0 ★ ≥1 ellipse near bar
            LayerCenteredOnLayer(type_a="ellipse", type_b="rectangle",                        # 1 ★ ellipse y-centered on bar
                                  tolerance=40.0, axis="y"),
        ], weight=0.16, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
