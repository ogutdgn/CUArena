"""
Task 04 — Color hexagon ring (in-scope replacement).

6 squares arranged in a hexagonal ring, each filled a different rainbow color
(red, yellow, green, cyan, blue, magenta).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, RadialDistribution, LayerAllSquare,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerRotationEquals,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors,
    FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import LayerInsideFrame, LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_04_color_wheel",
    description="6 same-size squares arranged in a hexagonal ring, each filled a different rainbow color.",
    rubrics=[
        # critical: exactly 6 squares — prompt-explicit
        FundamentalsRubric([
            ShapeCount("rectangle", equals=6),                                        # 0 ★ "6 same-size squares"
        ], weight=0.25, critical=[0]),

        # critical: same size, hexagonal ring (radial), squares — all prompt-explicit
        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),              # 0 ★ "same-size"
            RadialDistribution(layer_type="rectangle", n=6, tolerance_deg=10.0),      # 1 ★ "hexagonal ring"
            LayerAllSquare(layer_type="rectangle", tolerance=3.0),                    # 2 ★ "squares" (every one)
            LayerSizeAtLeast(layer_type="rectangle", min_w=20.0, min_h=20.0),         # 3 ★ non-degenerate
            LayerInsideFrame("rectangle"),                                            # 4 ★ "Inside a frame"
            LayerGroupAllInSameFrame("rectangle", minimum=6),                         # 5 ★ all 6 in one frame
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=4.0),  # 6 ★ fits in frame
            LayerRotationEquals(layer_type="rectangle", degrees=0.0, tolerance=2.0),  # 7 ★ no rotation
            NoLayerFlipped(layer_type="rectangle"),                                   # 8 ★ no flips
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=2.0),      # 9 ★ frame not rotated
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.3),         # 10 ★ no extreme rounding
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),

        # critical: solid fills + 6 distinct rainbow colors — prompt-explicit
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                 # 0 ★
            DistinctSolidColors(minimum=6, tolerance=0.05),                           # 1 ★ "rainbow colors"
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),     # 2 ★ visible
            FillCountAtMost(layer_type="rectangle", max_count=1),                     # 3 ★ no stacked fills
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),              # 4 ★ near-invisible catch
        ], weight=0.25, critical=[0, 1, 2, 3, 4]),

        # critical: rectangle tool used — prompt-explicit
        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★ "Click Rectangle tool"
            EventTypeCount("create_rectangle", equals=6),                             # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
