"""
Task 21 — Vertical icon column (in-scope replacement, no auto-layout).

3 same-size rectangles stacked vertically with 16px gap, each a different color,
aligned on the same x center.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersAligned, LayersStacked,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerRotationEquals,
    FrameCountAtMost, LayerAspectRatioGreaterThan,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, FillCountAtMost,
    DistinctTypedSolidColors,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import (
    LayerInsideFrame, LayerGroupAllInSameFrame, LayerTotalCount,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_21_button_stack",
    description="3 same-size rectangles stacked vertically (16px gap), different colors, aligned on x.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=3),                                          # 0 * "3 ... rectangles"
            LayerTotalCount(equals=4),                                                  # 1 * 3 rects + 1 frame (no extras)
        ], weight=0.20, critical=[0, 1]),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),                # 0 * "same-size" (tightened)
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=2.0),      # 1 * "aligned on x" (tightened)
            LayersStacked(layer_type="rectangle", axis="y", gap_px=16.0, tolerance=8.0),# 2 * "stacked vertically"
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=1.0),      # 3 * not rotated (tightened)
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=1.5,              # 4 * "horizontal" buttons (wider than tall)
                                        axis="horizontal"),
        ], weight=0.20, critical=[0, 1, 2, 3, 4]),

        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                   # 0 *
            FillCountAtMost(layer_type="rectangle", max_count=1),                       # 1 *
            DistinctTypedSolidColors(layer_type="rectangle", minimum=3, tolerance=0.05),# 2 * each rect distinct color (frame excluded)
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),       # 3 * rects must render
        ], weight=0.20, critical=[0, 1, 2, 3]),

        StructureRubric([
            LayerInsideFrame(layer_type="rectangle"),                                   # 0 * rects in a frame
            LayerGroupAllInSameFrame(layer_type="rectangle", minimum=3),                # 1 * all 3 in same frame
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",            # 2 * fit inside frame
                                 tolerance=4.0),
            LayerSizeAtLeast(layer_type="rectangle", min_w=30, min_h=20),               # 3 * not 1×1 degenerate
            NoLayerFlipped(layer_type="rectangle"),                                     # 4 * not flipped
            FrameCountAtMost(maximum=1),                                                # 5 * one frame
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),          # 6 * frame not rotated
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.45),          # 7 * rects not pill-shaped (tightened)
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7]),

        EventRubric([
            ToolUsed("rectangle"),                                                      # 0 * rectangle tool mandated
            EventTypeCount("create_rectangle", equals=3),
        ], weight=0.20, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
