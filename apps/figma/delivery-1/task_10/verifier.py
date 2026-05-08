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
            LayersConcentric(layer_type="rectangle", tolerance=12.0),                 # 0 ★ prompt: "shared center"
            SmallerLayerInsideLarger(layer_type="rectangle", tolerance=10.0),         # 1 ★ prompt: "nested ... decreasing size"
            LayerAllSquare(layer_type="rectangle", tolerance=8.0),                    # 2 ★ prompt: "4 ... squares" (w≈h)
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),    # 3 upright (sanity)
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),        # 4 frame upright (implicit)
            LayerSizeAtLeast(layer_type="rectangle", min_w=15, min_h=15),             # 5 no degenerate (sanity)
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=10.0),                                     # 6 inside frame (sanity)
            NoLayerFlipped(layer_type="rectangle"),                                   # 7 not mirrored (implicit)
            LayerAreaRatioAtLeast(layer_type="rectangle", min_ratio=1.5),             # 8 ★ prompt: "decreasing size" (outer >> inner)
        ], weight=0.20, critical=[0, 1, 2, 8]),

        # ── Color: solid alternating, ≥2 distinct ──
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                 # 0 ★ prompt: "color A ... color B" (every solid)
            DistinctTypedSolidColors(layer_type="rectangle", minimum=2,
                                     tolerance=0.12),                                 # 1 ★ prompt: "alternating two colors"
            FillCountAtMost("rectangle", max_count=1),                                # 2 no stacked fills (sanity)
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                         # 3 visible fills (sanity)
            LayerVisible("rectangle"),                                                # 4 alpha+visible+opacity (sanity)
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),         # 5 no circular squares (sanity)
        ], weight=0.20, critical=[0, 1]),

        # ── Structure: in one frame ──
        StructureRubric([
            LayerInsideFrame("rectangle"),                                            # 0 ★ all in one frame
            ChildCountAtLeast("frame", minimum=4),                                    # 1 ★ all 4 in same frame
        ], weight=0.20, critical=[0, 1]),

        # ── Event: rectangle tool used (non-critical: tool may be shortcut) ──
        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 prompt: "Click Rectangle tool" (tool may be shortcut)
            EventTypeCount("create_rectangle", equals=4),                             # 1
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
