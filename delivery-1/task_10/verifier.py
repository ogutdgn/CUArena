"""
Task 10 — Concentric squares (in-scope replacement).

4 nested squares of decreasing size, alternating two colors, all sharing the same center.
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
    LayersConcentric, SmallerLayerInsideLarger, LayerRotationEquals,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerAllSquare,
    LayerAreaRatioAtLeast,
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
    id="task_10_apple_avatar",
    description="4 nested squares of decreasing size, alternating two colors, sharing center.",
    rubrics=[
        # ── Fundamentals: exactly 4 squares ──
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),                                        # 0 ★ "4 ... nested squares"
        ], weight=0.20, critical=[0]),

        # ── Alignment / Geometry ──
        AlignmentRubric([
            LayersConcentric(layer_type="rectangle", tolerance=8.0),                  # 0 ★ "shared center"
            SmallerLayerInsideLarger(layer_type="rectangle", tolerance=2.0),          # 1 ★ "nested ... decreasing size"
            LayerAllSquare(layer_type="rectangle", tolerance=3.0),                    # 2 ★ "squares" (w≈h)
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=2.0),    # 3 ★ upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),        # 4 ★ frame upright
            LayerSizeAtLeast(layer_type="rectangle", min_w=15, min_h=15),             # 5 ★ no degenerate
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=10.0),                                     # 6 ★ inside frame
            NoLayerFlipped(layer_type="rectangle"),                                   # 7 ★ not mirrored
            LayerAreaRatioAtLeast(layer_type="rectangle", min_ratio=2.0),             # 8 ★ outer >> inner
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        # ── Color: solid alternating, ≥2 distinct ──
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                 # 0 ★ every solid
            DistinctTypedSolidColors(layer_type="rectangle", minimum=2,
                                     tolerance=0.05),                                 # 1 ★ "alternating two colors"
            FillCountAtMost("rectangle", max_count=1),                                # 2 ★ no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                         # 3 ★ visible fills
            LayerVisible("rectangle"),                                                # 4 ★ alpha+visible+opacity
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.4),         # 5 ★ no circular squares
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5]),

        # ── Structure: in one frame ──
        StructureRubric([
            LayerInsideFrame("rectangle"),                                            # 0 ★
            ChildCountAtLeast("frame", minimum=4),                                    # 1 ★ all 4 in same frame
        ], weight=0.20, critical=[0, 1]),

        # ── Event: rectangle tool used ──
        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★
            EventTypeCount("create_rectangle", equals=4),                             # 1 ★
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
