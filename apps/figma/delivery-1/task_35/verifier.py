"""
Task 35 — 2x2 honeycomb pattern (SIMPLIFIED Medium → Easy).

4 yellow hexagons (polygon, 6 sides) arranged in a 2×2 offset honeycomb tiling,
each with a 1px black stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersSameDimensions, OffsetGridLayout, LayerSizeAtLeast,
    LayerRotationEquals,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, AllSolidColorEquals, FillCountAtMost,
)
from verifier.checks.stroke_checks import (
    AllStrokeExists, AllStrokeColorEquals, AllStrokeWeightsEqual,
    AllLayerStrokeVisible,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

YELLOW = {"r": 1.0, "g": 0.85, "b": 0.2}
BLACK  = {"r": 0.0, "g": 0.0,  "b": 0.0}

task = Task(
    id="task_35_honeycomb",
    description="2×2 honeycomb of 4 yellow hexagons (6 sides each) with 1px black strokes.",
    rubrics=[
        # critical: prompt mandates 4 hexagons (6 sides)
        FundamentalsRubric([
            ShapeCount("polygon", equals=4),  # 0 ★ prompt: "4 yellow hexagons"
            PolygonSidesEquals(sides=6),      # 1 ★ prompt: "hexagon (Polygon tool, 6 sides)"
        ], weight=0.25, critical=[0, 1]),

        # critical: 2×2 offset honeycomb tiling — single primitive maps to prompt phrase.
        AlignmentRubric([
            OffsetGridLayout(layer_type="polygon", rows=2, cols=2, tolerance=15.0),   # 0 ★ prompt: "2×2 offset honeycomb tiling"
            LayersSameDimensions(layer_type="polygon", tolerance=25.0),                # 1
            LayerSizeAtLeast(layer_type="polygon", min_w=15, min_h=15),               # 2
            LayerRotationEquals(layer_type="polygon", degrees=0, tolerance=5.0),      # 3
            NoLayerFlipped(layer_type="polygon"),                                     # 4
            CornerRadiusFractionAtMost(layer_type="polygon", max_frac=0.5),           # 5
        ], weight=0.25, critical=[0]),

        # critical: yellow fill + 1px black stroke are prompt-explicit, all visible.
        # AllStrokeWeightsEqual maps directly to "1px ... each" (every layer must match).
        ColorRubric([
            AllFillTypeIs("polygon", kind="solid"),                                           # 0 ★ prompt: "yellow hexagons" require visible fill
            AllSolidColorEquals(layer_type="polygon", expected_rgb=YELLOW, tolerance=0.28),   # 1 ★ prompt: "yellow hexagons"
            AllStrokeExists("polygon"),                                                       # 2 ★ prompt: "1px black stroke each"
            AllStrokeWeightsEqual(layer_type="polygon", weight=1.0, tolerance=1.5),           # 3 ★ prompt: "1px ... each"
            AllStrokeColorEquals("polygon", expected_rgb=BLACK, tolerance=0.28),              # 4 ★ prompt: "black stroke"
            AllLayerStrokeVisible("polygon", min_alpha=0.5, min_weight=0.5),                  # 5
            FillCountAtMost("polygon", max_count=1),                                          # 6
            LayerVisible("polygon"),                                                          # 7
        ], weight=0.25, critical=[0, 1, 2, 4]),

        # event: must use polygon tool (kept soft per playbook)
        EventRubric([
            ToolUsed("polygon"),                          # 0
            EventTypeCount("create_polygon", equals=4),   # 1
        ], weight=0.25, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
