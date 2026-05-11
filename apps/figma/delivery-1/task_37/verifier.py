"""
Task 37 — Yellow sticky note (IN SCOPE).

Yellow square (rotated ~3°) + drop shadow + pen-tool corner fold + 3 horizontal lines.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayerBoundsInside, LayerRotationEquals, AllLayerBoundsInside,
    LayerSizeAtLeast, LayerAspectRatioGreaterThan, LayerCenteredOnLayer,
    LayerIsSquare, LayersStacked, LayerInFrontOf, LayerEdgesAligned,
    CrossTypeAreaRatioAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost,
)
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, AllLayerStrokeVisible
from verifier.checks.effect_checks import DropShadowExists, VisibleDropShadowExists
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast
from verifier.checks.structure_checks import LayerInsideFrame

YELLOW = {"r": 1.0, "g": 0.92, "b": 0.6}

task = Task(
    id="task_37_sticky_note",
    description="Yellow square (rotated ~3°) + drop shadow + pen-tool fold + 3 horizontal lines.",
    rubrics=[
        # critical: prompt mandates 1 sticky body + pen-tool fold + 3 lines + sizes
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),                       # 0 ★ prompt: "yellow square"
            ShapeCountAtLeast("vector", minimum=1),                  # 1 prompt: "Pen tool" fold
            ShapeCountAtLeast("line", minimum=3),                    # 2 ★ prompt: "3 thin horizontal lines"
            LayerSizeAtLeast(layer_type="rectangle", min_w=40, min_h=40),  # 3 no degenerate body
            LayerSizeAtLeast(layer_type="vector",    min_w=4,  min_h=4),   # 4 no 1x1 fold
            LayerSizeAtLeast(layer_type="line",      min_w=10, min_h=0),   # 5 no 1x1 lines
            LayerIsSquare(layer_type="rectangle", tolerance=40.0),         # 6 ★ prompt: "yellow square"
            NoLayerFlipped(layer_type="rectangle"),                        # 7 no scaleX=-1
        ], weight=0.16, critical=[0, 2]),

        # critical: rotation 3° is prompt-explicit; fold-over-rect prompt-explicit
        AlignmentRubric([
            LayerBoundsInside(inner_type="vector", outer_type="rectangle", tolerance=20.0),    # 0 ★ prompt: "Above the body draw a small triangular fold"
            LayerRotationEquals(layer_type="rectangle", degrees=3.0, tolerance=2.5),           # 1 ★ prompt: "rotated 3°"
            LayerRotationEquals(layer_type="line",      degrees=0.0, tolerance=8.0),           # 2 ★ prompt: "3 thin horizontal lines"

            LayerAspectRatioGreaterThan(layer_type="line", ratio=4.0, axis="horizontal"),      # 6 thin horizontal
            LayerCenteredOnLayer(type_a="line", type_b="rectangle", tolerance=60.0, axis="x"), # 7 lines on rect x
            LayerCenteredOnLayer(type_a="line", type_b="rectangle", tolerance=180.0, axis="y"),# 8 lines on rect y

            LayersStacked(layer_type="line", axis="y", gap_px=20.0, tolerance=20.0),           # 10 lines stacked w/ gap
            LayerEdgesAligned(type_a="vector", edge_a="right",                                 # 11 ★ prompt: "fold on the top-right corner"
                              type_b="rectangle", edge_b="right", tolerance=80.0),
            CrossTypeAreaRatioAtLeast(big_type="rectangle", small_type="vector",               # 12 fold smaller than rect
                                       min_ratio=4.0),
        ], weight=0.18, critical=[0, 1, 2, 11]),

        # critical: yellow fill is prompt-explicit; fold must also be yellow-ish
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                          # 0 ★ prompt: "yellow square" (solid fill)
            SolidColorEquals(layer_type="rectangle", expected_rgb=YELLOW, tolerance=0.09),     # 1 ★ prompt: "yellow square"
            FillCountAtMost(layer_type="rectangle", max_count=1),                              # 2 no stacked fills
            LayerVisible(layer_type="rectangle"),                                              # 3 catches alpha=0/opacity=0
            AllFillTypeIs("vector", kind="solid"),                                             # 4 ★ prompt: "darker yellow" fold
            SolidColorEquals(layer_type="vector", expected_rgb=YELLOW, tolerance=0.18),        # 5 prompt: "darker yellow" fold
            StrokeExists(layer_type="line"),                                                   # 6 lines must be drawn
            StrokeWeightEquals(layer_type="line", weight=1.5, tolerance=2.5),                  # 7 visible weight
            AllLayerStrokeVisible(layer_type="line", min_alpha=0.5, min_weight=0.5),           # 8 lines render visibly
        ], weight=0.18, critical=[0, 1]),

        # effect: drop shadow not in simplified prompt — soft only
        EffectRubric([], weight=0.10, critical=[]),

        # structure: shapes inside the frame ("Click Frame tool" is step 1) — soft.
        StructureRubric([

            LayerInFrontOf(type_a="line", type_b="rectangle"),                                 # 3 lines drawn on top
            LayerInFrontOf(type_a="vector", type_b="rectangle"),                               # 4 fold drawn on top
        ], weight=0.10, critical=[]),

        # event: tool-used checks kept soft per playbook (agent may use shortcuts)
        EventRubric([
            ToolUsed("rectangle"),                                # 0
            ToolUsed("pen"),                                      # 1 prompt: "Pen tool"
            ToolUsed("line"),                                     # 2 prompt: "Line tool"
            EventTypeCount("create_rectangle", equals=1),         # 3
            EventTypeCountAtLeast("create_line", minimum=3),      # 4
            EventTypeCountAtLeast("create_vector", minimum=1),    # 5 ★ prompt: "triangular fold ... using the Pen tool"
        ], weight=0.18, critical=[5]),

        # property: catches stacked-trick fills, etc.
        FundamentalsRubric([
            FillCountAtMost(layer_type="vector", max_count=1),                                 # 0 no stacked fills
            LayerVisible(layer_type="vector"),                                                 # 1 fold actually visible
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
