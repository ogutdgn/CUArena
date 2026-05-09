"""
Task 26 — Brand color row (in-scope replacement, no variables).

5 same-size squares arranged in a horizontal row, each filled a different
brand color (1 primary + 4 supports).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.property     import PropertyRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersAligned, LayersStacked,
    LayerIsSquare, LayerSizeAtLeast, LayerRotationEquals,
    AllLayerBoundsInside,
)
from verifier.checks.fill_checks   import AllFillTypeIs, DistinctSolidColors
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_26_color_variable_card",
    description="5 same-size squares in a horizontal row, each a different brand color.",
    rubrics=[
        # critical: exactly 5 rectangles
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),                                  # 0 ★ prompt: "5 same-size squares"
        ], weight=0.20, critical=[0]),

        # critical: same-size SQUARES, row alignment, stacked horizontally
        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=8.0),         # 0 ★ prompt: "5 same-size squares"
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=12.0),  # 1 ★ prompt: "in a horizontal row"
            LayerIsSquare(layer_type="rectangle", tolerance=8.0),                # 2 ★ prompt: "squares"
            LayersStacked(layer_type="rectangle", axis="x", gap_px=16.0,
                          tolerance=12.0),                                        # 3 ★ prompt: "in a row"
            LayerSizeAtLeast(layer_type="rectangle", min_w=20.0, min_h=20.0),    # 4 non-degenerate
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=10.0),                                 # 5 inside frame
        ], weight=0.25, critical=[0, 1, 2, 3]),

        # critical: solid + distinct brand colors
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                           # 0   structural: solid fill required for color check
            DistinctSolidColors(minimum=5, tolerance=0.12),                     # 1 ★ prompt: "different brand color"
            LayerVisible(layer_type="rectangle", min_opacity=0.5,
                         min_alpha=0.5),                                        # 2 visible
        ], weight=0.20, critical=[1]),

        # squares look like squares (unrotated, unflipped, not pill)
        PropertyRubric([
            LayerRotationEquals(layer_type="rectangle", degrees=0.0,
                                tolerance=5.0),                                 # 0 unrotated
            NoLayerFlipped(layer_type="rectangle"),                             # 1 no flips
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),   # 2 not full circle
        ], weight=0.15, critical=[]),

        # rectangle tool used
        EventRubric([
            ToolUsed("rectangle"),                                              # 0
            EventTypeCount("create_rectangle", equals=5),                       # 1
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
