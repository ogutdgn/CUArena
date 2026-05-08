"""
Task 03 — Radial flower with petals (in-scope replacement).

1 yellow center circle + 8 elliptical petals arranged radially around it,
each petal a different color.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    RadialDistributionExcludeCentral, LayerAllCircular, LayerSizeAtLeast,
    AllLayerBoundsInside, LayerRotationEquals,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, CentermostLayerHasColor,
    FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import LayerInsideFrame, LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_03_glowing_orb",
    description="1 yellow center circle + 8 elliptical petals arranged radially around it.",
    rubrics=[
        # critical: 9 ellipses (1 center + 8 petals) — prompt-explicit
        FundamentalsRubric([
            ShapeCount("ellipse", equals=9),                                          # 0 ★
        ], weight=0.25, critical=[0]),

        # critical: 8 petals arranged radially + circular centre + structural integrity
        AlignmentRubric([
            RadialDistributionExcludeCentral(layer_type="ellipse", n=8, tolerance_deg=15.0),  # 0 ★ "arranged radially"
            LayerAllCircular(layer_type="ellipse", tolerance=8.0),                    # 1 ★ "circle ... ellipse" (all round, not oval)
            LayerSizeAtLeast(layer_type="ellipse", min_w=20.0, min_h=20.0),           # 2 ★ non-degenerate
            LayerInsideFrame(layer_type="ellipse"),                                   # 3 ★ "Inside a frame"
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=9),                # 4 ★ all 9 in one frame
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=4.0),  # 5 ★ fits in frame
            LayerRotationEquals(layer_type="ellipse", degrees=0.0, tolerance=2.0),    # 6 ★ no rotation
            NoLayerFlipped(layer_type="ellipse"),                                     # 7 ★ no flips
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=2.0),      # 8 ★ frame not rotated
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        # critical: solid fills + 8 distinct petal colors + yellow center — prompt-explicit
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                   # 0 ★
            DistinctSolidColors(minimum=8, tolerance=0.05),                           # 1 ★ "Each petal is a different color"
            CentermostLayerHasColor(layer_type="ellipse",                             # 2 ★ "yellow center circle"
                                    expected_rgb={"r": 1.0, "g": 0.9, "b": 0.2},
                                    tolerance=0.20),
            LayerVisible(layer_type="ellipse", min_opacity=0.5, min_alpha=0.5),       # 3 ★ visible
            FillCountAtMost(layer_type="ellipse", max_count=1),                       # 4 ★ no stacked fills
            FillOpacityAtLeast(layer_type="ellipse", min_opacity=0.5),                # 5 ★ near-invisible catch
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5]),

        # critical: ellipse tool used — prompt-explicit
        EventRubric([
            ToolUsed("ellipse"),                                                      # 0 ★ "Click Ellipse tool"
            EventTypeCount("create_ellipse", equals=9),                               # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
