"""
Task 39 — Wifi signal icon (SIMPLIFIED Medium → Easy).

2 concentric pen-tool arcs (6px navy stroke) above a small navy filled circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayerSizeAtLeast, AllLayerBoundsInside, LayerRotationEquals,
    LayerCenteredOnLayer, LayerInFrontOf, LayerIsCircular,
    LayerEdgesAligned, CrossTypeAreaRatioAtLeast,
    VectorsCurvedCountAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    AllStrokeExists, AllStrokeColorEquals, AllStrokeWeightsEqual,
    AllLayerStrokeVisible,
)
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast, EventTypeCount
from verifier.checks.structure_checks import LayerInsideFrame

NAVY = {"r": 0.05, "g": 0.10, "b": 0.45}

task = Task(
    id="task_39_wifi_icon",
    description="2 pen-tool arcs (6px navy stroke) above 1 small navy circle.",
    rubrics=[
        # critical: prompt mandates 2 pen arcs + 1 circle
        FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=2),                      # 0 ★ prompt: "2 ... arcs"
            ShapeCount("ellipse", equals=1),                             # 1 ★ prompt: "small ... circle"
            VectorsCurvedCountAtLeast(minimum=2),                        # 2 ★ prompt: "arcs" — pen-tool curves, not straight lines
            LayerSizeAtLeast(layer_type="vector", min_w=20, min_h=10),   # 3 no 1×1 arcs
            LayerSizeAtLeast(layer_type="ellipse", min_w=8, min_h=8),    # 4 no degenerate dot
            NoLayerFlipped(layer_type="vector"),                         # 5 arcs not flipped
            NoLayerFlipped(layer_type="ellipse"),                        # 6 dot not flipped
        ], weight=0.20, critical=[0, 1, 2]),

        # critical: arcs above dot, dot circular, dot below arcs
        AlignmentRubric([
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                         # 0 ★ prompt: "small ... circle"
            LayerEdgesAligned(type_a="ellipse", edge_a="top",                             # 1 ★ prompt: "circle below the arcs"
                              type_b="vector", edge_b="bottom", tolerance=100.0),
            AllLayerBoundsInside(inner_type="vector",  outer_type="frame", tolerance=8.0),# 2 arcs in frame
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=8.0),# 3 dot in frame
            LayerCenteredOnLayer(type_a="ellipse", type_b="vector", tolerance=120.0,      # 4 dot centered on arcs (x)
                                  axis="x"),
            LayerRotationEquals(layer_type="vector", degrees=0.0, tolerance=10.0),        # 5 arcs upright
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=5.0),          # 6 frame upright
            CrossTypeAreaRatioAtLeast(big_type="vector", small_type="ellipse",            # 7 ★ prompt: "small ... circle"
                                       min_ratio=1.0),
            CrossTypeAreaRatioAtLeast(big_type="frame", small_type="ellipse",             # 8 dot smaller than frame
                                       min_ratio=10.0),
        ], weight=0.20, critical=[0, 1]),

        # critical: navy fill on circle + 6px navy stroke on arcs are prompt-explicit.
        # AllStrokeWeightsEqual maps directly to "Apply a 6px navy stroke" applied
        # uniformly to both arcs.
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                          # 0 ★ prompt: "navy ... circle" (solid)
            SolidColorEquals(layer_type="ellipse", expected_rgb=NAVY, tolerance=0.35),       # 1 ★ prompt: "navy ... circle" — loose tol for modifier+color
            AllStrokeExists("vector"),                                                       # 2 ★ prompt: "Apply a 6px navy stroke"
            AllStrokeWeightsEqual(layer_type="vector", weight=6.0, tolerance=2.0),           # 3 ★ prompt: "6px ... stroke"
            AllStrokeColorEquals(layer_type="vector", expected_rgb=NAVY, tolerance=0.35),    # 4 ★ prompt: "navy stroke" — loose tol for modifier+color
            AllLayerStrokeVisible(layer_type="vector", min_alpha=0.5, min_weight=0.5),       # 5 stroke renders visibly
            FillCountAtMost(layer_type="ellipse", max_count=1),                              # 6 no stacked fills on dot
            LayerVisible(layer_type="ellipse"),                                              # 7 dot visible
            FillOpacityAtLeast(layer_type="ellipse", min_opacity=0.5),                       # 8 dot fill opacity
            LayerVisible(layer_type="vector"),                                                # 9 arcs not invisible
        ], weight=0.22, critical=[0, 1, 3, 4]),

        # structure: arcs and dot must be inside a frame
        StructureRubric([
            LayerInsideFrame(layer_type="vector"),                       # 0 ★ shapes inside frame ("Click Frame tool" step 1)
            LayerInsideFrame(layer_type="ellipse"),                      # 1 dot inside frame
        ], weight=0.10, critical=[]),

        # event: tool-used checks kept soft per playbook
        EventRubric([
            ToolUsed("pen"),                                          # 0 prompt: "Pen tool"
            ToolUsed("ellipse"),                                      # 1 prompt: "Ellipse tool"
            EventTypeCountAtLeast("create_vector_with_pen", minimum=1), # 2 ★ mock event name; prompt says draw 1st arc with pen then "Duplicate"
            EventTypeCount("create_ellipse", equals=1),               # 3
        ], weight=0.18, critical=[]),

        # property: extra structural anchors
        FundamentalsRubric([
            LayerInFrontOf(type_a="ellipse", type_b="vector"),                              # 0 dot drawn after arcs (z)
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
