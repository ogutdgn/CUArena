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
    AllFillTypeIs, AllSolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    AllStrokeExists, AllStrokeColorEquals, AllStrokeWeightWithinTolerance,
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
            ShapeCount("polygon", equals=4),  # 0 ★ "4 ... hexagons"
            PolygonSidesEquals(sides=6),      # 1 ★ "hexagon" (6 sides)
        ], weight=0.25, critical=[0, 1]),

        # critical: prompt mandates 2x2 honeycomb arrangement, plus same-size,
        # non-degenerate, upright, not flipped, no corner-radius transforms.
        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=2.0),                # 0 ★ "duplicate it three times"
            OffsetGridLayout(layer_type="polygon", rows=2, cols=2, tolerance=15.0),   # 1 ★ "2×2 offset honeycomb"
            LayerSizeAtLeast(layer_type="polygon", min_w=15, min_h=15),               # 2 ★ no degenerate hexagons
            LayerRotationEquals(layer_type="polygon", degrees=0, tolerance=5.0),      # 3 ★ hexagons upright
            NoLayerFlipped(layer_type="polygon"),                                     # 4 ★ no mirrored hexagons
            CornerRadiusFractionAtMost(layer_type="polygon", max_frac=0.1),           # 5 ★ no rounded corners
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5]),

        # critical: yellow fill + 1px black stroke are prompt-explicit, all visible
        ColorRubric([
            AllFillTypeIs("polygon", kind="solid"),                                           # 0 ★ all solid
            AllSolidColorEquals(layer_type="polygon", expected_rgb=YELLOW, tolerance=0.20),   # 1 ★ "yellow"
            AllStrokeExists("polygon"),                                                       # 2 ★ all hexagons have visible stroke
            AllStrokeWeightWithinTolerance("polygon", target_weight=1.0, tolerance=1.0),      # 3 ★ every hexagon "1px"
            AllStrokeColorEquals("polygon", expected_rgb=BLACK, tolerance=0.20),              # 4 ★ "black stroke" (every hex)
            AllLayerStrokeVisible("polygon", min_alpha=0.5, min_weight=0.5),                  # 5 ★ no transparent strokes
            FillCountAtMost("polygon", max_count=1),                                          # 6 ★ no stacked fills
            FillOpacityAtLeast("polygon", min_opacity=0.5),                                   # 7 ★ visible fills
            LayerVisible("polygon"),                                                          # 8 ★ visible layers
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        # critical: must use polygon tool
        EventRubric([
            ToolUsed("polygon"),                          # 0 ★
            EventTypeCount("create_polygon", equals=4),   # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
