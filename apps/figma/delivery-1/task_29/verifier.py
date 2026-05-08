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
    FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible,
)
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, AlignToolUsed

OFF_WHITE = {"r": 0.97, "g": 0.95, "b": 0.92}

task = Task(
    id="task_29_polka_dot_grid",
    description="Off-white frame + 4 same-color circles in a 2×2 grid via Tidy up.",
    rubrics=[
        # critical: 4 circles in a frame
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),                                # 0 ★ "4 circles"
            ShapeCountAtLeast("frame", minimum=1),                          # 1 ★ "Inside a frame"
        ], weight=0.2, critical=[0, 1]),

        # critical: same-size, 2x2 grid, circular, upright, sane size, on-frame
        AlignmentRubric([
            LayersSameDimensions(layer_type="ellipse", tolerance=2.0),      # 0 ★ "same-size"
            LayersInGrid(layer_type="ellipse", rows=2, cols=2, tolerance=10.0),  # 1 ★ "2x2 grid"
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),           # 2 ★ "circles"
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=2.0),  # 3 ★ upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),    # 4 ★ frame upright
            NoLayerFlipped(layer_type="ellipse"),                           # 5 ★ not flipped
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),     # 6 ★ no degenerate
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",
                                  min_frac=0.02, max_frac=0.40),             # 7 ★ dots-vs-frame size sane
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",
                                 tolerance=4.0),                             # 8 ★ on-frame
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        # critical: solid + off-white frame + visible
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                         # 0 ★
            LayersAllSameColor(layer_type="ellipse", tolerance=0.05),       # 1   (optional per prompt)
            SolidColorEquals(layer_type="frame", expected_rgb=OFF_WHITE, tolerance=0.15),  # 2 ★ "off-white"
            FillCountAtMost(layer_type="ellipse", max_count=1),             # 3 ★ no stacked fills
            FillOpacityAtLeast(layer_type="ellipse", min_opacity=0.5),      # 4 ★ visible fill
            LayerVisible(layer_type="ellipse"),                             # 5 ★ alpha + visibility
        ], weight=0.2, critical=[0, 2, 3, 4, 5]),

        # all dots in same frame (structural)
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=4),      # 0 ★ all 4 in same frame
        ], weight=0.2, critical=[0]),

        # critical: ellipse tool + Tidy up (AlignToolUsed)
        EventRubric([
            ToolUsed("ellipse"),                                            # 0 ★
            EventTypeCount("create_ellipse", equals=4),                     # 1
            AlignToolUsed(),                                                # 2 ★ "Tidy up"
        ], weight=0.2, critical=[0, 2]),
    ],
    efficiency=EfficiencyRubric(target_turns=16),
)
