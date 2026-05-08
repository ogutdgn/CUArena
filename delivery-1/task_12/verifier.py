"""
Task 12 — Card row (in-scope replacement).

4 same-size rectangles arranged in a horizontal row with consistent spacing,
all sharing the same y baseline.
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
    LayersSameDimensions, LayersAligned, LayersDistributed, LayersAllShareEdge,
    LayersHaveConsistentGap,
    LayerSizeAtLeast, AllLayerWidthFraction, AllLayerBoundsInside,
    LayerRotationEquals, LayerAspectRatioGreaterThan,
)
from verifier.checks.fill_checks   import AllFillTypeIs, FillCountAtMost, FillOpacityAtLeast
from verifier.checks.property_checks import (
    NoLayerFlipped, CornerRadiusFractionAtMost, LayerVisible,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_12_shadowed_cards",
    description="4 same-size rectangles in a horizontal row, sharing the same y baseline, evenly spaced.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),                                          # 0 ★ "4" rectangles
        ], weight=0.2, critical=[0]),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),                # 0 ★ "same-size"
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),      # 1 ★ "horizontal row" → tops/bottoms align
            LayersDistributed(layer_type="rectangle", axis="x", tolerance=8.0),         # 2 ★ "consistent spacing"
            LayersAllShareEdge(layer_type="rectangle", edge="top", tolerance=5.0),      # 3 ★ "horizontal row" tops align
            LayersAllShareEdge(layer_type="rectangle", edge="bottom", tolerance=5.0),   # 4 ★ "row" bottoms align
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=2.0),      # 5 ★ rects upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),          # 6 ★ frame upright
            LayerSizeAtLeast(layer_type="rectangle", min_w=15, min_h=15),               # 7 ★ no degenerate
            AllLayerWidthFraction(inner_type="rectangle", parent_type="frame",          # 8 ★ rect-vs-frame size sane
                                  min_frac=0.04, max_frac=0.40),
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",            # 9 ★ rects in frame bounds
                                 tolerance=4.0),
            LayersHaveConsistentGap(layer_type="rectangle", axis="x",                   # 10 ★ "consistent spacing" with positive gaps
                                    min_gap=1.0, variance_tolerance=10.0),
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),

        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                   # 0 ★ every rect solid
            FillCountAtMost("rectangle", max_count=1),                                  # 1 ★ no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                           # 2 ★ visible fills
            LayerVisible("rectangle"),                                                  # 3 ★ alpha + visible + layer opacity
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.4),           # 4 ★ no pill/circle rects
            NoLayerFlipped(layer_type="rectangle"),                                     # 5 ★ no mirror/flip
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5]),

        StructureRubric([
            LayerInsideFrame("rectangle"),                                              # 0 ★ rects inside frame
            ChildCountAtLeast("frame", minimum=4),                                      # 1 ★ all 4 rects in one frame
        ], weight=0.2, critical=[0, 1]),

        EventRubric([
            ToolUsed("rectangle"),                                                       # 0 ★ rectangle tool mandated
            EventTypeCount("create_rectangle", equals=4),
        ], weight=0.2, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
