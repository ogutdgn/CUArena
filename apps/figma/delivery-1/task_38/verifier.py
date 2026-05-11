"""
Task 38 — Battery indicator (IN SCOPE).

Rounded outer body rectangle (gray stroke) + small terminal rectangle on right
+ 3 colored level-bar rectangles inside.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersAligned, LayerSizeAtLeast, AllLayerBoundsInside,
    LayerRotationEquals, LayerAreaRatioAtLeast,
    SmallerLayerInsideLarger, CrossTypeAreaRatioAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeWeightEquals, StrokeColorEquals, VisibleStrokeExists,
)
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, NoLayerFlipped, LayerVisible, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.structure_checks import LayerInsideFrame

GRAY = {"r": 0.5, "g": 0.5, "b": 0.5}

task = Task(
    id="task_38_battery_indicator",
    description="Battery body (rounded, gray stroke) + terminal + 3 colored bars (5 rectangles total).",
    rubrics=[
        # critical: prompt mandates body + terminal + 3 bars = 5 rectangles
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),                                # 0 ★ prompt: "body, terminal, and 3 inner level bars"
            LayerSizeAtLeast(layer_type="rectangle", min_w=4, min_h=4),       # 1 no 1×1 rects
            LayerAreaRatioAtLeast(layer_type="rectangle", min_ratio=1.5),     # 2 body bigger than other rects
            NoLayerFlipped(layer_type="rectangle"),                           # 3 no scaleX=-1
        ], weight=0.16, critical=[0]),

        # critical: prompt mandates rounded body + bars-inside-body
        AlignmentRubric([
            CornerRadiusAtLeast(layer_type="rectangle", min_value=4.0),                       # 0 ★ prompt: "rounded outer rectangle"
            SmallerLayerInsideLarger(layer_type="rectangle", tolerance=20.0),                 # 1 ★ prompt: "3 colored bar rectangles inside"

            LayerRotationEquals(layer_type="rectangle", degrees=0.0, tolerance=5.0),          # 3 no rotation

            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=80.0),           # 5 bars/body roughly aligned
            CrossTypeAreaRatioAtLeast(big_type="frame", small_type="rectangle",                # 6 body smaller than frame
                                       min_ratio=2.0),
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.6),                  # 7 no over-rounded body
        ], weight=0.18, critical=[0, 1]),

        # critical: prompt mandates 3 distinct bar colors + gray stroke on body
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                            # 0 ★ prompt: "3 colored bar rectangles" (solid fill)
            DistinctSolidColors(minimum=4, tolerance=0.15),                      # 1 ★ prompt: "green/yellow/red sequence" + body
            StrokeExists("rectangle"),                                           # 2 prompt: "gray stroke"
            StrokeWeightEquals("rectangle", weight=2.0, tolerance=1.5),          # 3 visible weight
            StrokeColorEquals("rectangle", expected_rgb=GRAY, tolerance=0.28),   # 4 ★ prompt: "gray stroke" — human-friendly
            VisibleStrokeExists("rectangle"),                                    # 5 catches alpha=0/visible=False/weight=0
            FillCountAtMost(layer_type="rectangle", max_count=1),                # 6 no stacked fills
            LayerVisible(layer_type="rectangle"),                                # 7 catches alpha=0/opacity=0
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),         # 8 visible fills
        ], weight=0.18, critical=[0, 1, 4]),

        # structure: shapes must be inside a frame (soft anchor — prompt does not say "Inside a frame")
        StructureRubric([

        ], weight=0.10, critical=[]),

        # event: rectangle tool — kept soft per playbook
        EventRubric([
            ToolUsed("rectangle"),                              # 0
            EventTypeCount("create_rectangle", equals=5),       # 1
        ], weight=0.18, critical=[]),

        # property: catch degenerate sizes
        FundamentalsRubric([
            LayerSizeAtLeast(layer_type="rectangle", min_w=10, min_h=10),  # 0 stricter min size
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
