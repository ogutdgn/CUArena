"""
Task 08 — Layered water waves (IN SCOPE).

Two pen-tool wave paths with bezier handles, in different blues, with 4px stroke.
1000x300 frame.
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
    FrameSizeEquals, LayerRotationEquals, LayerSizeAtLeast,
    AllLayerWidthFraction, AllLayerBoundsInside, LayersOverlap,
)
from verifier.checks.stroke_checks import (
    StrokeExists, AllStrokeExists, StrokeWeightEquals, DistinctTypedStrokeColors,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_08_water_waves",
    description="Two pen-tool S-curve waves with bezier handles, distinct blue strokes (4px each).",
    rubrics=[
        # ── Fundamentals: exactly 2 vector paths ──
        FundamentalsRubric([
            ShapeCount("vector", equals=2),                                           # 0 ★ "two ... waves"
        ], weight=0.20, critical=[0]),

        # ── Alignment / Geometry ──
        AlignmentRubric([
            FrameSizeEquals(width=1000, height=300, tolerance=25.0),                  # 0 ★ prompt: "1000x300 frame"
            LayerRotationEquals(layer_type="vector", degrees=0, tolerance=5.0),       # 1 waves upright (sanity)
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),        # 2 frame upright (implicit)
            LayerSizeAtLeast(layer_type="vector", min_w=20, min_h=20),                # 3 no degenerate vectors (sanity)
            AllLayerWidthFraction(inner_type="vector", parent_type="frame",
                                  min_frac=0.10, max_frac=0.95),                      # 4 wave width sane
            AllLayerBoundsInside(inner_type="vector", outer_type="frame",
                                 tolerance=10.0),                                     # 5 ★ prompt: "Create a 1000x300 frame" (vectors inside)
            NoLayerFlipped(layer_type="vector"),                                      # 6 vectors not mirrored (implicit)
            LayersOverlap(type_a="vector", type_b="vector"),                          # 7 ★ prompt: "two layered water waves"
        ], weight=0.20, critical=[0, 5, 7]),

        # ── Color: 4px blue strokes, 2 distinct shades ──
        ColorRubric([
            AllStrokeExists("vector"),                                                # 0 ★ prompt: "4px blue stroke" (every wave stroked)
            StrokeWeightEquals("vector", weight=4.0, tolerance=2.5),                  # 1 ★ prompt: "4px"
            DistinctTypedStrokeColors(layer_type="vector", minimum=2,
                                      tolerance=0.12),                                # 2 ★ prompt: "different blue shades"
            LayerVisible("vector"),                                                   # 3 alpha+visible+opacity (sanity)
        ], weight=0.20, critical=[0, 1, 2]),

        # ── Structure: vectors in one frame ──
        StructureRubric([
            LayerInsideFrame("vector"),                                               # 0 ★ prompt: "Create a 1000x300 frame"
            ChildCountAtLeast("frame", minimum=2),                                    # 1 ★ both waves in one frame
        ], weight=0.20, critical=[0, 1]),

        # ── Event: pen tool used (non-critical: tool may be shortcut) ──
        EventRubric([
            ToolUsed("pen"),                                                          # 0 prompt: "Use the Pen tool" (tool may be shortcut)
            EventTypeCountAtLeast("create_vector", minimum=2),                        # 1
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
