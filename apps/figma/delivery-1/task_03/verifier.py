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
            ShapeCount("ellipse", equals=9),                                          # 0 ★ prompt: "1 yellow center circle and ... 8 elliptical petals"
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            RadialDistributionExcludeCentral(layer_type="ellipse", n=8, tolerance_deg=15.0),  # 0 ★ prompt: "arranged radially"
            LayerAllCircular(layer_type="ellipse", tolerance=8.0),                    # 1
            LayerSizeAtLeast(layer_type="ellipse", min_w=20.0, min_h=20.0),           # 2
            LayerInsideFrame(layer_type="ellipse"),                                   # 3 ★ prompt: "Inside a frame"
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=9),                # 4
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=10.0),  # 5
            LayerRotationEquals(layer_type="ellipse", degrees=0.0, tolerance=5.0),    # 6
            NoLayerFlipped(layer_type="ellipse"),                                     # 7
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=5.0),      # 8
        ], weight=0.25, critical=[0, 3]),

        # critical: solid fills + 8 distinct petal colors + yellow center — prompt-explicit
        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                   # 0 ★ prompt: every shape filled with color
            DistinctSolidColors(minimum=8, tolerance=0.12),                           # 1 ★ prompt: "Each petal is a different color"
            CentermostLayerHasColor(layer_type="ellipse",                             # 2 ★ prompt: "yellow center circle"
                                    expected_rgb={"r": 1.0, "g": 0.9, "b": 0.2},
                                    tolerance=0.28),
            LayerVisible(layer_type="ellipse", min_opacity=0.5, min_alpha=0.5),       # 3
            FillCountAtMost(layer_type="ellipse", max_count=1),                       # 4
            FillOpacityAtLeast(layer_type="ellipse", min_opacity=0.5),                # 5
        ], weight=0.25, critical=[0, 1, 2]),

        # critical: ellipse tool used — prompt-explicit
        EventRubric([
            ToolUsed("ellipse"),                                                      # 0 ★ prompt: "Click Ellipse tool"
            EventTypeCount("create_ellipse", equals=9),                               # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
