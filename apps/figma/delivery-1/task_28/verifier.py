"""
Task 28 — Photo placeholder mockup (in-scope replacement, no image fill).

1 large rectangle (placeholder) + 2 diagonal lines drawn from corner to corner forming an X-cross.
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
    LinesOnDiagonal, LayerRotationEquals, AllLayerBoundsInside,
    LayerSizeAtLeast, AllLayerWidthFraction,
)
from verifier.checks.fill_checks   import AllFillTypeIs
from verifier.checks.property_checks import NoLayerFlipped
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.stroke_checks import AllLayerStrokeVisible

task = Task(
    id="task_28_edited_photo",
    description="Large rectangle placeholder + 2 diagonal lines crossing through it.",
    rubrics=[
        # critical: 1 rect + 2 lines (prompt-explicit counts)
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),                              # 0 ★ prompt: "a rectangle"
            ShapeCount("line",      equals=2),                              # 1 ★ prompt: "2 diagonal lines"
        ], weight=0.2, critical=[0, 1]),

        # critical: diagonals must form X-cross (single domain primitive on actual line endpoints)
        AlignmentRubric([
            LinesOnDiagonal(rect_type="rectangle", line_type="line", tolerance=15.0),  # 0 ★ prompt: "from corner to corner ... so they form an X-cross"
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),   # 1 rect upright

            NoLayerFlipped(layer_type="rectangle"),                                  # 3 rect not flipped
            LayerSizeAtLeast(layer_type="rectangle", min_w=40, min_h=40),            # 4 no degenerate rect
            AllLayerWidthFraction(inner_type="rectangle", parent_type="frame",
                                  min_frac=0.05, max_frac=0.90),                     # 5 rect-vs-frame size sane

        ], weight=0.2, critical=[0]),

        # critical: lines must visually show as the X-cross
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                       # 0 rectangle has solid fill
            AllLayerStrokeVisible(layer_type="line", min_alpha=0.1, min_weight=0.5),  # 1 ★ prompt: "two diagonal lines forming an X" (lines must render)
        ], weight=0.2, critical=[1]),

        # both rect and lines inside frame (structural)
        StructureRubric([

        ], weight=0.2, critical=[]),

        # rectangle + line tools both used
        EventRubric([
            ToolUsed("rectangle"),                                          # 0
            ToolUsed("line"),                                               # 1
            EventTypeCount("create_rectangle", equals=1),                   # 2
            EventTypeCount("create_line",      equals=2),                   # 3
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
