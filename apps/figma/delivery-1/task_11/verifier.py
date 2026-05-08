"""
Task 11 — Triangle pyramid stack (in-scope replacement).

3 triangles of decreasing size all centered together (largest at back, smallest at front),
alternating two colors, forming a layered pyramid look.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersConcentric, SmallerLayerInsideLarger, LayerRotationEquals,
    LayerSizeAtLeast, AllLayerBoundsInside,
    LayerAreaRatioAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctTypedSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_11_pressed_button",
    description="3 triangles of decreasing size centered together, alternating two colors.",
    rubrics=[
        # ── Fundamentals: exactly 3 triangles ──
        FundamentalsRubric([
            ShapeCount("polygon", equals=3),                                          # 0 ★ "3 ... triangles"
            PolygonSidesEquals(sides=3),                                              # 1 ★ "triangles" — 3 sides
        ], weight=0.20, critical=[0, 1]),

        # ── Alignment / Geometry ──
        AlignmentRubric([
            LayersConcentric(layer_type="polygon", tolerance=10.0),                   # 0 ★ "same center"
            SmallerLayerInsideLarger(layer_type="polygon", tolerance=2.0),            # 1 ★ "nested ... decreasing size"
            LayerRotationEquals(layer_type="polygon", degrees=0, tolerance=2.0),      # 2 ★ upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),        # 3 ★ frame upright
            LayerSizeAtLeast(layer_type="polygon", min_w=20, min_h=20),               # 4 ★ no degenerate
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame",
                                 tolerance=10.0),                                     # 5 ★ inside frame
            NoLayerFlipped(layer_type="polygon"),                                     # 6 ★ not mirrored
            LayerAreaRatioAtLeast(layer_type="polygon", min_ratio=2.0),               # 7 ★ outer >> inner
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7]),

        # ── Color: solid alternating ──
        ColorRubric([
            AllFillTypeIs("polygon", kind="solid"),                                   # 0 ★ every solid
            DistinctTypedSolidColors(layer_type="polygon", minimum=2,
                                     tolerance=0.05),                                 # 1 ★ "alternating two colors"
            FillCountAtMost("polygon", max_count=1),                                  # 2 ★ no stacked fills
            FillOpacityAtLeast("polygon", min_opacity=0.5),                           # 3 ★ visible fills
            LayerVisible("polygon"),                                                  # 4 ★ alpha+visible+opacity
        ], weight=0.20, critical=[0, 1, 2, 3, 4]),

        # ── Structure: in one frame ──
        StructureRubric([
            LayerInsideFrame("polygon"),                                              # 0 ★
            ChildCountAtLeast("frame", minimum=3),                                    # 1 ★ all 3 in one frame
        ], weight=0.20, critical=[0, 1]),

        # ── Event: polygon tool used ──
        EventRubric([
            ToolUsed("polygon"),                                                      # 0 ★ "Polygon tool with 3 sides"
            EventTypeCount("create_polygon", equals=3),                               # 1 ★
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
