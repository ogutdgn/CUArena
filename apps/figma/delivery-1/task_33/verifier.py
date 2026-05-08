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
    LayerIsCircular, LayerOnTopOf, LayerInFrontOf, LayersOverlap,
    AllLayersAreCircular, LayerSizeAtLeast, LayerSmallerThanLayer,
    LayerRotationEquals, LayersHaveDistinctRotations,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, DistinctSolidColors,
    FillCountAtMost, FillOpacityAtLeast,
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
            ShapeCount("polygon", equals=2),  # 1 ★ prompt: "2 colored wedge triangles"
            PolygonSidesEquals(sides=3),      # 2 prompt: "triangles" → 3 sides
        ], weight=0.25, critical=[0, 1]),

        # critical: prompt mandates round base + wedges layered on top, with
        # wedges visually overlapping base, base non-degenerate, base larger than
        # wedges (wedges are slices, not the whole pie).
        AlignmentRubric([
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                    # 0 ★ prompt: "circle"
            AllLayersAreCircular(layer_type="ellipse", tolerance=8.0),               # 1
            LayerOnTopOf(type_a="polygon", type_b="ellipse"),                        # 2 ★ prompt: "layered on top of the teal circle"
            LayerInFrontOf(type_a="polygon", type_b="ellipse"),                      # 3 ★ prompt: "both layered on top"
            LayersOverlap(type_a="polygon", type_b="ellipse"),                       # 4 ★ prompt: "from the center extending to the edge"
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),              # 5
            LayerSizeAtLeast(layer_type="polygon", min_w=10, min_h=10),              # 6
            LayerSmallerThanLayer(smaller_type="polygon", larger_type="ellipse",     # 7
                                  max_frac=0.95),
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),     # 8
            NoLayerFlipped(layer_type="polygon"),                                    # 9
            NoLayerFlipped(layer_type="ellipse"),                                    # 10
            LayersHaveDistinctRotations(layer_type="polygon", minimum=2,             # 11 ★ prompt: "rotated to different angles"
                                        tolerance_deg=10.0),
        ], weight=0.25, critical=[0, 2, 3, 4, 11]),

        # critical: prompt mandates teal base + distinct wedge colors,
        # all visible solid fills (no transparency tricks, no stacked fills).
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                       # 0 ★ every shape needs visible solid fill
            AllFillTypeIs("polygon", kind="solid"),                                       # 1
            SolidColorEquals(layer_type="ellipse", expected_rgb=TEAL, tolerance=0.28),    # 2 ★ prompt: "teal solid fill"
            DistinctSolidColors(minimum=3, tolerance=0.15),                               # 3 ★ prompt: "teal" + "2 ... in different colors"
            FillCountAtMost("ellipse", max_count=1),                                      # 4
            FillCountAtMost("polygon", max_count=1),                                      # 5
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                               # 6
            FillOpacityAtLeast("polygon", min_opacity=0.5),                               # 7
            LayerVisible("ellipse"),                                                      # 8
            LayerVisible("polygon"),                                                      # 9
        ], weight=0.25, critical=[0, 2, 3]),

        # critical: must use both ellipse and polygon tools
        EventRubric([
            ToolUsed("ellipse"),                          # 0
            ToolUsed("polygon"),                          # 1
            EventTypeCount("create_ellipse", equals=1),   # 2
            EventTypeCount("create_polygon", equals=2),   # 3
        ], weight=0.25, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
