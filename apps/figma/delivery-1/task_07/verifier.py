"""
Task 07 — Layered mountain range (IN SCOPE).

Two pen-tool paths in different gray shades — closer mountain in front,
overlapping the farther one. 1000x400 frame.
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
    LayersOverlap, FrameSizeEquals, LayerRotationEquals,
    LayerSizeAtLeast, AllLayerWidthFraction, AllLayerBoundsInside,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctTypedSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_07_mountain_range",
    description="Two overlapping pen-tool mountain paths in different gray shades.",
    rubrics=[
        # ── Fundamentals: exactly 2 vector paths ──
        FundamentalsRubric([
            ShapeCount("vector", equals=2),                                           # 0 ★ "two ... pen-tool paths"
        ], weight=0.20, critical=[0]),

        # ── Alignment / Geometry ──
        AlignmentRubric([
            LayersOverlap(type_a="vector", type_b="vector"),                          # 0 ★ "overlapping" / "layered"
            FrameSizeEquals(width=1000, height=400, tolerance=10.0),                  # 1 ★ 1000x400 frame
            LayerRotationEquals(layer_type="vector", degrees=0, tolerance=2.0),       # 2 ★ vectors upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),        # 3 ★ frame upright
            LayerSizeAtLeast(layer_type="vector", min_w=20, min_h=20),                # 4 ★ no degenerate vectors
            AllLayerWidthFraction(inner_type="vector", parent_type="frame",
                                  min_frac=0.10, max_frac=0.95),                      # 5 ★ vector size sane
            AllLayerBoundsInside(inner_type="vector", outer_type="frame",
                                 tolerance=10.0),                                     # 6 ★ vectors inside frame
            NoLayerFlipped(layer_type="vector"),                                      # 7 ★ vectors not mirrored
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7]),

        # ── Color: solid fills + 2 distinct gray shades ──
        ColorRubric([
            AllFillTypeIs("vector", kind="solid"),                                    # 0 ★ every vector solid
            DistinctTypedSolidColors(layer_type="vector", minimum=2, tolerance=0.05), # 1 ★ "different shades"
            FillCountAtMost("vector", max_count=1),                                   # 2 ★ no stacked fills
            FillOpacityAtLeast("vector", min_opacity=0.5),                            # 3 ★ visible fills
            LayerVisible("vector"),                                                   # 4 ★ alpha+visible+opacity
        ], weight=0.20, critical=[0, 1, 2, 3, 4]),

        # ── Structure: vectors in one frame ──
        StructureRubric([
            LayerInsideFrame("vector"),                                               # 0 ★
            ChildCountAtLeast("frame", minimum=2),                                    # 1 ★ both in one frame
        ], weight=0.20, critical=[0, 1]),

        # ── Event: pen tool used ──
        EventRubric([
            ToolUsed("pen"),                                                          # 0 ★ "Use the Pen tool"
            EventTypeCountAtLeast("create_vector", minimum=2),                        # 1 ★
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
