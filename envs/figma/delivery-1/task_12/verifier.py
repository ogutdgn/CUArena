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
    LayerRotationEquals,
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
            ShapeCount("rectangle", equals=4),                                          # 0 ★ prompt: "4 same-size rectangles"
        ], weight=0.2, critical=[0]),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=25.0),                # 0 ★ prompt: "4 same-size rectangles"
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=25.0),     # 1 ★ prompt: "horizontal row"
            LayersDistributed(layer_type="rectangle", axis="x", tolerance=25.0),         # 2 ★ prompt: "consistent spacing"
            LayersAllShareEdge(layer_type="rectangle", edge="top", tolerance=15.0),     # 3 ★ prompt: "tops and bottoms align"
            LayersAllShareEdge(layer_type="rectangle", edge="bottom", tolerance=15.0),  # 4 ★ prompt: "tops and bottoms align"
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),      # 5 rects upright (implicit)
            LayerSizeAtLeast(layer_type="rectangle", min_w=15, min_h=15),               # 7 no degenerate
            AllLayerWidthFraction(inner_type="rectangle", parent_type="frame",          # 8 rect-vs-frame size sane
                                  min_frac=0.04, max_frac=0.40),
            LayersHaveConsistentGap(layer_type="rectangle", axis="x",                   # 10 reinforces "consistent spacing" via gap-variance
                                    min_gap=1.0, variance_tolerance=12.0),
        ], weight=0.2, critical=[0, 1, 2, 3, 4]),

        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                   # 0 ★ prompt: "any solid fill"
            FillCountAtMost("rectangle", max_count=1),                                  # 1 no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                           # 2 visible fills
            LayerVisible("rectangle"),                                                  # 3 alpha + visible + layer opacity
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),           # 4 no pill/circle rects
            NoLayerFlipped(layer_type="rectangle"),                                     # 5 no mirror/flip
        ], weight=0.2, critical=[0]),

        StructureRubric([
            ChildCountAtLeast("frame", minimum=4),                                      # 1 all 4 rects in one frame (implicit, not in prompt)
        ], weight=0.2, critical=[]),

        EventRubric([
            ToolUsed("rectangle"),                                                       # 0 prompt mentions tool but keyboard-shortcut OK
            EventTypeCount("create_rectangle", equals=4),
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
