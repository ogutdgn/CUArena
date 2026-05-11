"""
Task 29 — Polka dot grid (IN SCOPE).

Off-white frame + 4 same-color circles in a 2×2 grid, aligned via Tidy up
(align_layers / distribute_layers events).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersInGrid, LayerIsCircular,
    LayerRotationEquals, AllLayerBoundsInside, LayerSizeAtLeast,
    AllLayerWidthFraction,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, LayersAllSameColor, SolidColorEquals,
)
from verifier.checks.property_checks import NoLayerFlipped
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, AlignToolUsed

OFF_WHITE = {"r": 0.97, "g": 0.95, "b": 0.92}

task = Task(
    id="task_29_polka_dot_grid",
    description="Off-white frame + 4 same-color circles in a 2×2 grid via Tidy up.",
    rubrics=[
        # critical: 4 circles inside a frame
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),                                # 0 ★ prompt: "4 same-size circles"
            ShapeCountAtLeast("frame", minimum=1),                          # 1 ★ prompt: "Inside a frame with off-white fill"
        ], weight=0.2, critical=[0, 1]),

        # critical: same-size, 2x2 grid, circular
        AlignmentRubric([
            LayersSameDimensions(layer_type="ellipse", tolerance=25.0),      # 0 ★ prompt: "4 same-size circles"
            LayersInGrid(layer_type="ellipse", rows=2, cols=2, tolerance=25.0),  # 1 ★ prompt: "arranged in a 2x2 grid pattern"
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),           # 2 ★ prompt: "circles"
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),  # 3 upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),    # 4 frame upright
            NoLayerFlipped(layer_type="ellipse"),                           # 5 not flipped
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),     # 6 no degenerate
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",
                                  min_frac=0.02, max_frac=0.40),             # 7 dots-vs-frame size sane
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",
                                 tolerance=10.0),                            # 8 on-frame
        ], weight=0.2, critical=[0, 1, 2]),

        # critical: off-white frame fill
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                         # 0 circle solid fill
            LayersAllSameColor(layer_type="ellipse", tolerance=25.0),       # 1 (optional per prompt)
            SolidColorEquals(layer_type="frame", expected_rgb=OFF_WHITE, tolerance=0.25),  # 2 ★ prompt: "off-white fill"
        ], weight=0.2, critical=[2]),

        # all dots in same frame (structural)
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=4),      # 0 ★ prompt: "Inside a frame ... draw 4 ... circles"
        ], weight=0.2, critical=[0]),

        # critical: Tidy up (AlignToolUsed)
        EventRubric([
            ToolUsed("ellipse"),                                            # 0
            EventTypeCount("create_ellipse", equals=4),                     # 1
            AlignToolUsed(),                                                # 2 ★ prompt: "Use Tidy up"
        ], weight=0.2, critical=[2]),
    ],
    efficiency=EfficiencyRubric(target_turns=16),
)
