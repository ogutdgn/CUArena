"""
Task 29 — Polka dot grid (IN SCOPE).

Prompt: "Inside a frame with off-white fill, draw 4 same-size circles
arranged in a 2x2 grid pattern. Make each circle the same color."

Off-white frame + 4 same-color same-size circles in a 2×2 grid.
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
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

OFF_WHITE = {"r": 0.97, "g": 0.95, "b": 0.92}

task = Task(
    id="task_29_polka_dot_grid",
    description="Off-white frame + 4 same-color same-size circles in a 2×2 grid.",
    rubrics=[
        # critical: 4 circles inside a frame
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),                                # 0 ★ prompt: "4 same-size circles"
            ShapeCountAtLeast("frame", minimum=1),                          # 1 ★ prompt: "Inside a frame with off-white fill"
        ], weight=0.2, critical=[0, 1]),

        # critical: same-size, 2x2 grid, circular
        AlignmentRubric([
            LayersSameDimensions(layer_type="ellipse", tolerance=10.0),      # 0 ★ prompt: "4 same-size circles"  (tightened 25 → 10; same-size should be visually obvious)
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

        # critical: same-color circles AND off-white frame fill
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                         # 0 circles have a solid fill
            LayersAllSameColor(layer_type="ellipse", tolerance=0.05),       # 1 ★ prompt: "Make each circle the same color"
            SolidColorEquals(layer_type="frame", expected_rgb=OFF_WHITE, tolerance=0.35),  # 2 ★ prompt: "off-white fill" (loose tol so the model has wiggle room hitting the swatch)
        ], weight=0.2, critical=[1, 2]),

        # critical: all 4 circles share one frame
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=4),      # 0 ★ prompt: "Inside a frame ... draw 4 ... circles"
        ], weight=0.2, critical=[0]),

        # critical: 4 ellipse-create events
        EventRubric([
            ToolUsed("ellipse"),                                            # 0
            EventTypeCount("create_ellipse", equals=4),                     # 1 ★ prompt: "draw 4 ... circles"
        ], weight=0.2, critical=[1]),
    ],
    # 25 turns is the efficient-agent path without Tidy up: draw 1 circle +
    # color it, duplicate ×3, drag into rough 2×2 layout, then row-align +
    # distribute-horizontal × 2 rows and col-align × 2 cols.
    efficiency=EfficiencyRubric(target_turns=25),
)
