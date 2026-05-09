"""
Task 32 — 4-blade pinwheel (IN SCOPE).

4 triangles rotated radially (alternating two colors) + small center pivot circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersSameDimensions, RadialDistribution, LayersEvenlyRotated,
    LayerIsCircular, LayersAlternatingColors, AllLayerBoundsInside,
    LayerSizeAtLeast, LayerSmallerThanLayer, LayerInFrontOf,
    AllLayersAreCircular, FrameCountAtMost,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors,
)
from verifier.checks.property_checks import NoLayerFlipped
from verifier.checks.structure_checks import (
    LayerInsideFrame, LayerGroupAllInSameFrame, ChildCountAtLeast,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_32_pinwheel",
    description="4 triangles rotated 90° apart, alternating two colors, around a small center circle.",
    rubrics=[
        # critical: prompt mandates 4 triangles + 1 center circle
        FundamentalsRubric([
            ShapeCount("polygon", equals=4),         # 0 ★ prompt: "4 triangles"
            ShapeCount("ellipse", equals=1),         # 1 ★ prompt: "small center circle"
            ShapeCountAtLeast("frame", minimum=1),   # 2 ★ prompt: "Inside a frame"
            PolygonSidesEquals(sides=3),             # 3 ★ prompt: "triangles"
        ], weight=0.2, critical=[0, 1, 3]),

        # critical: prompt mandates radial 90° rotation, round center, small pivot.
        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=8.0),                       # 0
            RadialDistribution(layer_type="polygon", n=4, tolerance_deg=15.0),                # 1 ★ prompt: "arranged radially"
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=10.0), # 2 ★ prompt: "rotation +90°"
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                             # 3 ★ prompt: "small center circle"
            AllLayersAreCircular(layer_type="ellipse", tolerance=8.0),                        # 4
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame", tolerance=10.0),    # 5
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=10.0),    # 6
            LayerSizeAtLeast(layer_type="polygon", min_w=10, min_h=10),                       # 7
            LayerSizeAtLeast(layer_type="ellipse", min_w=8, min_h=8),                         # 8
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="polygon",              # 9 ★ prompt: "small center circle"
                                  max_frac=0.85),
            LayerInFrontOf(type_a="ellipse", type_b="polygon"),                               # 10
            NoLayerFlipped(layer_type="polygon"),                                             # 11
        ], weight=0.2, critical=[1, 2, 3, 9]),

        # critical: prompt mandates 2 alternating colors radially
        ColorRubric([
            AllFillTypeIs("polygon", kind="solid"),                                                          # 0 solid fills required
            AllFillTypeIs("ellipse", kind="solid"),                                                          # 1
            DistinctSolidColors(minimum=2, tolerance=0.15),                                                  # 2 ★ prompt: "alternating two colors"
            LayersAlternatingColors(layer_type="polygon", n_colors=2, sort_axis="angle", tolerance=0.15),    # 3 ★ prompt: "Pick color A. ... color B. ... color A. ... color B."
        ], weight=0.2, critical=[2, 3]),

        # critical: shapes must all live in one frame (catches split-frame designs)
        StructureRubric([
            LayerInsideFrame("polygon"),                                # 0 ★ prompt: "Inside a frame"
            LayerInsideFrame("ellipse"),                                # 1
            LayerGroupAllInSameFrame(layer_type="polygon", minimum=4),  # 2
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=1),  # 3
            ChildCountAtLeast("frame", minimum=5),                      # 4 4 triangles + 1 circle inside one frame
            FrameCountAtMost(maximum=1),                                # 5
        ], weight=0.2, critical=[0]),

        # critical: must use polygon tool
        EventRubric([
            ToolUsed("polygon"),                       # 0
            EventTypeCount("create_polygon", equals=4),# 1
            EventTypeCount("create_ellipse", equals=1),# 2
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
