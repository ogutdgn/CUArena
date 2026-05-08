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
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals
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
            ShapeCount("rectangle", equals=1),                       # 0 ★ "yellow square"
            ShapeCountAtLeast("vector", minimum=1),                  # 1 ★ "Pen tool" fold
            ShapeCountAtLeast("line", minimum=3),                    # 2 ★ "3 ... horizontal lines"
            LayerSizeAtLeast(layer_type="rectangle", min_w=40, min_h=40),  # 3 ★ no degenerate body
            LayerSizeAtLeast(layer_type="vector",    min_w=4,  min_h=4),   # 4 ★ no 1x1 fold
            LayerSizeAtLeast(layer_type="line",      min_w=10, min_h=0),   # 5 ★ no 1x1 lines
            LayerIsSquare(layer_type="rectangle", tolerance=40.0),         # 6 ★ "yellow SQUARE"
            NoLayerFlipped(layer_type="rectangle"),                        # 7 ★ no scaleX=-1
        ], weight=0.16, critical=[0, 1, 2, 3, 4, 5, 6, 7]),

        # critical: rotation 3° is prompt-explicit; everything must fit inside frame
        AlignmentRubric([
            LayerBoundsInside(inner_type="vector", outer_type="rectangle", tolerance=20.0),    # 0 ★ fold over rect
            LayerRotationEquals(layer_type="rectangle", degrees=3.0, tolerance=0.9),           # 1 ★ "rotated 3°"
            LayerRotationEquals(layer_type="line",      degrees=0.0, tolerance=2.5),           # 2 ★ "horizontal" lines
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=8.0),   # 3 ★ rect inside frame
            AllLayerBoundsInside(inner_type="vector",    outer_type="frame", tolerance=8.0),   # 4 ★ fold inside frame
            AllLayerBoundsInside(inner_type="line",      outer_type="frame", tolerance=8.0),   # 5 ★ lines inside frame
            LayerAspectRatioGreaterThan(layer_type="line", ratio=4.0, axis="horizontal"),      # 6 ★ thin horizontal
            LayerCenteredOnLayer(type_a="line", type_b="rectangle", tolerance=60.0, axis="x"), # 7 ★ lines on rect x
            LayerCenteredOnLayer(type_a="line", type_b="rectangle", tolerance=180.0, axis="y"),# 8 ★ lines on rect y
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=2.0),               # 9 ★ frame not rotated
            LayersStacked(layer_type="line", axis="y", gap_px=20.0, tolerance=20.0),           # 10 ★ lines stacked w/ gap (catches overlap)
            LayerEdgesAligned(type_a="vector", edge_a="right",                                 # 11 ★ fold at TOP-RIGHT corner
                              type_b="rectangle", edge_b="right", tolerance=80.0),
            CrossTypeAreaRatioAtLeast(big_type="rectangle", small_type="vector",               # 12 ★ fold smaller than rect
                                       min_ratio=4.0),
        ], weight=0.18, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),

        # critical: yellow fill is prompt-explicit; fold must also be a yellow shade
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                          # 0 ★
            SolidColorEquals(layer_type="rectangle", expected_rgb=YELLOW, tolerance=0.09),     # 1 ★ "yellow"
            FillCountAtMost(layer_type="rectangle", max_count=1),                              # 2 ★ no stacked fills
            LayerVisible(layer_type="rectangle"),                                              # 3 ★ catches alpha=0/opacity=0
            AllFillTypeIs("vector", kind="solid"),                                             # 4 ★ fold must be solid
            SolidColorEquals(layer_type="vector", expected_rgb=YELLOW, tolerance=0.18),        # 5 ★ "darker yellow" fold
            StrokeExists(layer_type="line"),                                                   # 6 ★ lines must be drawn
            StrokeWeightEquals(layer_type="line", weight=1.5, tolerance=1.0),                  # 7 ★ visible weight (>=0.5)
        ], weight=0.18, critical=[0, 1, 2, 3, 4, 5, 6, 7]),

        EffectRubric([
            DropShadowExists("rectangle"),                                                     # 0 ★ "drop shadow"
            VisibleDropShadowExists("rectangle"),                                              # 1 ★ shadow alpha>0, visible
        ], weight=0.10, critical=[0, 1]),

        # structure: rectangle must be inside a frame
        StructureRubric([
            LayerInsideFrame(layer_type="rectangle"),                                          # 0 ★ "inside frame"
            LayerInsideFrame(layer_type="vector"),                                             # 1 ★ fold inside frame
            LayerInsideFrame(layer_type="line"),                                               # 2 ★ lines inside frame
            LayerInFrontOf(type_a="line", type_b="rectangle"),                                 # 3 ★ lines drawn on top
            LayerInFrontOf(type_a="vector", type_b="rectangle"),                               # 4 ★ fold drawn on top
        ], weight=0.10, critical=[0, 1, 2, 3, 4]),

        # critical: must use rectangle, pen, and line tools (all explicit)
        EventRubric([
            ToolUsed("rectangle"),                                # 0 ★
            ToolUsed("pen"),                                      # 1 ★ "Pen tool"
            ToolUsed("line"),                                     # 2 ★ "Line tool"
            EventTypeCount("create_rectangle", equals=1),         # 3
            EventTypeCountAtLeast("create_line", minimum=3),      # 4
            EventTypeCountAtLeast("create_vector", minimum=1),    # 5 ★ pen creates vector
        ], weight=0.18, critical=[0, 1, 2, 5]),

        # property: catches stacked-trick fills, etc.
        FundamentalsRubric([
            FillCountAtMost(layer_type="vector", max_count=1),                                 # 0 ★ no stacked fills
            LayerVisible(layer_type="vector"),                                                 # 1 ★ fold actually visible
        ], weight=0.10, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
