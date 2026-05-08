"""
Task 20 — Glow blob backdrop (IN SCOPE).

Dark navy frame + 2 overlapping blurred circles (magenta + cyan).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersOverlap, LayerIsCircular, AllLayersAreCircular,
    AllLayerBoundsInside, LayerSizeAtLeast, FrameSizeEquals, FrameCountAtMost,
    LayerRotationEquals, LayersSameDimensions, LayersHaveDistinctCenters,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, DistinctSolidColors,
    FillCountAtMost,
)
from verifier.checks.effect_checks import (
    LayerBlurExists, BlurRadiusEquals, AllLayerBlurExists,
)
from verifier.checks.property_checks import LayerVisible, NoLayerFlipped
from verifier.checks.structure_checks import LayerInsideFrame, LayerGroupAllInSameFrame, LayerTotalCount
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

NAVY = {"r": 0.05, "g": 0.10, "b": 0.45}

task = Task(
    id="task_20_glow_blob",
    description="Dark navy frame + 2 overlapping blurred circles (distinct fills).",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),                                      # 0 * "dark navy frame"
            ShapeCount("ellipse", equals=2),                                            # 1 * "2 overlapping ... circles"
            LayerTotalCount(equals=3),                                                  # 2 * 1 frame + 2 ellipses (no extras)
        ], weight=0.20, critical=[0, 1, 2]),

        AlignmentRubric([
            LayersOverlap(type_a="ellipse", type_b="ellipse"),                          # 0 * "overlapping"
            AllLayersAreCircular(layer_type="ellipse", tolerance=3.0),                  # 1 * EVERY ellipse must be a circle
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=2.0),        # 2 * ellipses not rotated
            LayersHaveDistinctCenters(layer_type="ellipse", min_offset=20.0),           # 3 * ellipses partially (not fully) overlap
        ], weight=0.20, critical=[0, 1, 2, 3]),

        ColorRubric([
            AllFillTypeIs("ellipse", kind="solid"),                                     # 0 *
            AllFillTypeIs("frame",   kind="solid"),                                     # 1 *
            FillCountAtMost(layer_type="ellipse", max_count=1),                         # 2 *
            FillCountAtMost(layer_type="frame",   max_count=1),                         # 3 *
            SolidColorEquals(layer_type="frame", expected_rgb=NAVY, tolerance=0.30),    # 4 * "dark navy frame"
            DistinctSolidColors(minimum=3, tolerance=0.10),                             # 5 * "different bright colors"
            LayerVisible(layer_type="ellipse", min_opacity=0.5, min_alpha=0.5),         # 6 * ellipses visible
            LayerVisible(layer_type="frame",   min_opacity=0.5, min_alpha=0.5),         # 7 * frame visible
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7]),

        EffectRubric([
            AllLayerBlurExists(layer_type="ellipse"),                                   # 0 * BOTH ellipses have blur (not just one)
            BlurRadiusEquals(layer_type="ellipse", radius=80.0, tolerance=30.0),        # 1 * blur radius approx
        ], weight=0.10, critical=[0, 1]),

        StructureRubric([
            LayerInsideFrame(layer_type="ellipse"),                                     # 0 * ellipses in a frame
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=2),                  # 1 * both in same frame
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",              # 2 * ellipses fit inside frame
                                 tolerance=4.0),
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),                 # 3 * not 1×1 degenerate
            LayerSizeAtLeast(layer_type="frame",   min_w=200, min_h=200),               # 4 * frame sized for design (not 100×100)
            NoLayerFlipped(layer_type="ellipse"),                                       # 5 * not flipped
            FrameCountAtMost(maximum=1),                                                # 6 * one frame only
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),          # 7 * frame not rotated
            LayersSameDimensions(layer_type="ellipse", tolerance=20.0),                 # 8 * the 2 ellipses similar size
        ], weight=0.10, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        EventRubric([
            ToolUsed("frame"),                                                          # 0 * frame tool mandated
            ToolUsed("ellipse"),                                                        # 1 * ellipse tool mandated
            EventTypeCount("create_ellipse", equals=2),
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
