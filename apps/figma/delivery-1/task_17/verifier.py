"""
Task 17 — Hourglass shape (in-scope replacement, no boolean).

2 triangles point-to-point at the center + 2 horizontal rectangle caps (top and bottom).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersAligned, LayersHaveRotations, LayersStacked, LayerSizeAtLeast,
    AllLayerBoundsInside, LayerAspectRatioGreaterThan,
    LayerRotationEquals, FrameCountAtMost,
    LayersBracketAllOnAxis,
)
from verifier.checks.fill_checks   import AllFillTypeIs, FillCountAtMost
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import LayerInsideFrame, LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_17_play_button",
    description="2 triangles point-to-point + 2 horizontal rectangle caps top and bottom.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon",   equals=2),                                          # 0 ★ prompt: "2 triangles point-to-point"
            ShapeCount("rectangle", equals=2),                                          # 1 ★ prompt: "2 horizontal cap rectangles"
            PolygonSidesEquals(sides=3),                                                # 2 ★ prompt: "triangles" — 3 sides
        ], weight=0.20, critical=[0, 1, 2]),

        AlignmentRubric([
            LayersAligned(layer_type="polygon",   axis="center_x", tolerance=12.0),     # 0 ★ prompt: "All shapes share a center x"
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=12.0),     # 1 ★ prompt: "All shapes share a center x"
            LayersHaveRotations(layer_type="polygon", expected=[0, 180], count_per=1,   # 2 ★ prompt: "one pointing down, one pointing up"
                                tolerance_deg=10.0),
            LayersStacked(layer_type="polygon",   axis="y", gap_px=0.0, tolerance=12.0),# 3 ★ prompt: "point-to-point at the center"
            LayersBracketAllOnAxis(bracket_type="rectangle", inner_type="polygon",      # 4 ★ prompt: "caps at the top and bottom"
                                   axis="y", tolerance=4.0),
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),      # 5 caps must be horizontal
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0,              # 6 ★ prompt: "horizontal cap rectangles" (w > 2*h)
                                        axis="horizontal"),
        ], weight=0.20, critical=[0, 1, 2, 3, 4]),

        ColorRubric([
            AllFillTypeIs("polygon",   kind="solid"),                                   # 0 every shape needs a visible solid fill
            AllFillTypeIs("rectangle", kind="solid"),                                   # 1
            FillCountAtMost(layer_type="polygon",   max_count=1),                       # 2 stacked-fill workaround blocked
            FillCountAtMost(layer_type="rectangle", max_count=1),                       # 3
            LayerVisible(layer_type="polygon",   min_opacity=0.5, min_alpha=0.5),       # 4 triangles must render
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),       # 5 caps must render
        ], weight=0.20, critical=[]),

        StructureRubric([
            LayerInsideFrame(layer_type="polygon"),                                     # 0 triangles in a frame
            LayerInsideFrame(layer_type="rectangle"),                                   # 1 caps in same frame
            LayerGroupAllInSameFrame(layer_type="polygon",   minimum=2),                # 2 both triangles in same frame
            LayerGroupAllInSameFrame(layer_type="rectangle", minimum=2),                # 3 both caps in same frame
            AllLayerBoundsInside(inner_type="polygon",   outer_type="frame",            # 4 triangles must fit inside frame
                                 tolerance=10.0),
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",            # 5 caps must fit inside frame
                                 tolerance=10.0),
            LayerSizeAtLeast(layer_type="polygon",   min_w=15, min_h=15),               # 6 not 1×1 degenerate
            LayerSizeAtLeast(layer_type="rectangle", min_w=15, min_h=4),                # 7 not 1×1 degenerate
            NoLayerFlipped(layer_type="polygon"),                                       # 8 not flipped
            NoLayerFlipped(layer_type="rectangle"),                                     # 9 not flipped
            FrameCountAtMost(maximum=1),                                                # 10 one frame total (not split)
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),          # 11 frame not rotated
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),           # 12 caps not pills/circles
        ], weight=0.20, critical=[]),

        EventRubric([
            ToolUsed("polygon"),                                                        # 0 polygon tool used
            ToolUsed("rectangle"),                                                      # 1 rectangle tool used
            EventTypeCount("create_polygon",   equals=2),
            EventTypeCount("create_rectangle", equals=2),
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
