"""
Task 09 — 12-color swatch grid (in-scope replacement).

12 same-size squares arranged in a 4x3 grid, each filled a different color.
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
    LayersSameDimensions, LayersInGrid, LayerRotationEquals,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerAllSquare,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctTypedSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_09_brand_palette",
    description="4x3 grid of 12 same-size squares, each filled a different color.",
    rubrics=[
        # ── Fundamentals: exactly 12 squares ──
        FundamentalsRubric([
            ShapeCount("rectangle", equals=12),                                       # 0 ★ "12 same-size squares"
        ], weight=0.20, critical=[0]),

        # ── Alignment / Geometry ──
        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),              # 0 ★ "same-size"
            LayersInGrid(layer_type="rectangle", rows=3, cols=4, tolerance=10.0),     # 1 ★ "4x3 grid"
            LayerAllSquare(layer_type="rectangle", tolerance=3.0),                    # 2 ★ "squares" (w≈h)
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=2.0),    # 3 ★ squares upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),        # 4 ★ frame upright
            LayerSizeAtLeast(layer_type="rectangle", min_w=15, min_h=15),             # 5 ★ no degenerate
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=10.0),                                     # 6 ★ inside frame
            NoLayerFlipped(layer_type="rectangle"),                                   # 7 ★ not mirrored
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.4),         # 8 ★ no circular squares
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        # ── Color: solid fills + 12 distinct colors ──
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                 # 0 ★ every solid
            DistinctTypedSolidColors(layer_type="rectangle", minimum=12,
                                     tolerance=0.05),                                 # 1 ★ "each different color"
            FillCountAtMost("rectangle", max_count=1),                                # 2 ★ no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                         # 3 ★ visible fills
            LayerVisible("rectangle"),                                                # 4 ★ alpha+visible+opacity
        ], weight=0.20, critical=[0, 1, 2, 3, 4]),

        # ── Structure: squares in one frame ──
        StructureRubric([
            LayerInsideFrame("rectangle"),                                            # 0 ★
            ChildCountAtLeast("frame", minimum=12),                                   # 1 ★ all 12 in one frame
        ], weight=0.20, critical=[0, 1]),

        # ── Event: rectangle tool used ──
        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★ "Click Rectangle tool"
            EventTypeCount("create_rectangle", equals=12),                            # 1 ★
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
