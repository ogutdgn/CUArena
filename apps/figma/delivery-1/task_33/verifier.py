"""
Task 33 — 3-section pie chart (SIMPLIFIED Medium → Easy).

Teal base circle + 2 rotated triangle wedges layered on top in different colors.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayerIsCircular, LayerInFrontOf, LayersOverlap,
    LayerSizeAtLeast, LayerSmallerThanLayer,
    LayersHaveDistinctRotations,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, DistinctSolidColors,
    FillCountAtMost,
)
from verifier.checks.property_checks import LayerVisible, NoLayerFlipped
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

TEAL = {"r": 0.0, "g": 0.6, "b": 0.6}

task = Task(
    id="task_33_pie_chart",
    description="Teal base circle + 2 colored triangle wedges layered on top.",
    rubrics=[
        # critical: prompt mandates 1 base circle + 2 wedge triangles
        FundamentalsRubric([
            ShapeCount("ellipse", equals=1),  # 0 ★ prompt: "a teal base circle"
            ShapeCount("polygon", equals=2),  # 1 ★ prompt: "2 ... pie-slice triangles"
            PolygonSidesEquals(sides=3),      # 2 prompt: "triangles" → 3 sides
        ], weight=0.25, critical=[0, 1]),

        # critical: round base + wedges visually layered on top with overlap,
        # wedges rotated differently. Non-prompt geometry kept as soft anchors.
        AlignmentRubric([
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                    # 0 ★ prompt: "Draw a circle"
            LayerInFrontOf(type_a="polygon", type_b="ellipse"),                      # 1 ★ prompt: "both layered on top of the teal circle"
            LayersOverlap(type_a="polygon", type_b="ellipse"),                       # 2 ★ prompt: "from the center extending to the edge"
            LayersHaveDistinctRotations(layer_type="polygon", minimum=2,             # 3 ★ prompt: "rotated to different angles"
                                        tolerance_deg=10.0),
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),              # 4 no degenerate base
            LayerSizeAtLeast(layer_type="polygon", min_w=10, min_h=10),              # 5 no degenerate wedge
            LayerSmallerThanLayer(smaller_type="polygon", larger_type="ellipse",     # 6 wedges thinner than base
                                  max_frac=0.95),
            NoLayerFlipped(layer_type="polygon"),                                    # 7
            NoLayerFlipped(layer_type="ellipse"),                                    # 8
        ], weight=0.25, critical=[0, 1, 2, 3]),

        # critical: teal solid fill on base + 2 different wedge colors are
        # prompt-explicit ("teal solid fill" + "in different colors").
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                       # 0 ★ prompt: "teal solid fill"
            AllFillTypeIs("polygon", kind="solid"),                                       # 1
            SolidColorEquals(layer_type="ellipse", expected_rgb=TEAL, tolerance=0.28),    # 2 ★ prompt: "teal solid fill"
            DistinctSolidColors(minimum=3, tolerance=0.15),                               # 3 ★ prompt: "teal" base + "2 ... in different colors"
            FillCountAtMost("ellipse", max_count=1),                                      # 4
            FillCountAtMost("polygon", max_count=1),                                      # 5
            LayerVisible("ellipse"),                                                      # 6
            LayerVisible("polygon"),                                                      # 7
        ], weight=0.25, critical=[0, 2, 3]),

        # event: must use both ellipse and polygon tools (kept soft per playbook)
        EventRubric([
            ToolUsed("ellipse"),                          # 0
            ToolUsed("polygon"),                          # 1
            EventTypeCount("create_ellipse", equals=1),   # 2
            EventTypeCount("create_polygon", equals=2),   # 3
        ], weight=0.25, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
