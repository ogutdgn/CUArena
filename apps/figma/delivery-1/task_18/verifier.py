"""
Task 18 — Eye icon (in-scope replacement, no boolean).

3 nested ellipses sharing a center: outer (white sclera), middle (colored iris), inner (black pupil).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersConcentric, SmallerLayerInsideLarger, LayerIsCircular,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerAreaRatioAtLeast,
    AllLayersAreCircular, LayerRotationEquals, FrameCountAtMost,
    LayerSmallerThanLayer, LayersHaveDescendingArea,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, FillCountAtMost, DistinctSolidColors, LayersHaveColorOrder,
)
from verifier.checks.property_checks import LayerVisible, NoLayerFlipped
from verifier.checks.structure_checks import LayerInsideFrame, LayerGroupAllInSameFrame, LayerTotalCount
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_18_donut",
    description="3 nested ellipses (sclera, iris, pupil) sharing a center.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=3),                                            # 0 ★ prompt: "3 nested ellipses"
            LayerTotalCount(equals=4),                                                  # 1 3 ellipses + 1 frame = exactly 4 layers
        ], weight=0.20, critical=[0]),

        AlignmentRubric([
            LayersConcentric(layer_type="ellipse", tolerance=12.0),                     # 0 ★ prompt: "sharing a center"
            SmallerLayerInsideLarger(layer_type="ellipse", tolerance=10.0),             # 1 ★ prompt: "nested"
            AllLayersAreCircular(layer_type="ellipse", tolerance=8.0),                  # 2 ★ prompt: "ellipses" (circles for eye anatomy)
            LayersHaveDescendingArea(layer_type="ellipse", min_ratio=1.5,               # 3 sclera > iris > pupil (each step ≥1.5×)
                                     minimum_layers=2),
        ], weight=0.20, critical=[0, 1, 2]),

        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                     # 0 ★ every shape needs a visible solid fill
            FillCountAtMost(layer_type="ellipse", max_count=1),                         # 1 stacked-fill blocked
            LayerVisible(layer_type="ellipse", min_opacity=0.5, min_alpha=0.5),         # 2 ellipses must render
            DistinctSolidColors(minimum=3, tolerance=0.15),                             # 3 ★ prompt: "white", "colored", "black" (3 distinct)
            LayersHaveColorOrder(layer_type="ellipse",                                  # 4 largest=white, smallest=dark (eye anatomy)
                                 expected_rgbs=[
                                     {"r":1.0, "g":1.0, "b":1.0},   # sclera (largest)
                                     {"r":0.5, "g":0.5, "b":0.5},   # iris (middle, any tone)
                                     {"r":0.0, "g":0.0, "b":0.0},   # pupil (smallest)
                                 ],
                                 sort_axis="size", tolerance=0.50),
        ], weight=0.20, critical=[0, 3]),

        StructureRubric([
            LayerInsideFrame(layer_type="ellipse"),                                     # 0 ★ ellipses in a frame
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=3),                  # 1 all 3 in same frame
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",              # 2 ellipses must fit inside frame
                                 tolerance=10.0),
            LayerSizeAtLeast(layer_type="ellipse", min_w=10, min_h=10),                 # 3 not 1×1 degenerate
            NoLayerFlipped(layer_type="ellipse"),                                       # 4 not flipped
            FrameCountAtMost(maximum=1),                                                # 5 one frame total
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),          # 6 frame not rotated
        ], weight=0.20, critical=[0]),

        EventRubric([
            ToolUsed("ellipse"),                                                        # 0 ellipse tool used
            EventTypeCount("create_ellipse", equals=3),
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
