"""
Task 15 — Cloud silhouette (in-scope replacement, no boolean union).

4 overlapping ellipses, all white fill with 1px light-gray stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersOverlap, LayerSizeAtLeast,
    AllLayerBoundsInside, LayerRotationEquals, LayersAtDistinctPositions,
    AllLayerWidthFraction, LayersAllShareEdge,
)
from verifier.checks.fill_checks   import (
    AllSolidColorEquals, AllFillTypeIs, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    AllStrokeExists, AllStrokeColorEquals, AllStrokeWeightWithinTolerance,
)
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

WHITE      = {"r": 1.0, "g": 1.0, "b": 1.0}
LIGHT_GRAY = {"r": 0.85, "g": 0.85, "b": 0.85}

task = Task(
    id="task_15_cloud_union",
    description="4 overlapping white ellipses with 1px light-gray strokes forming a cloud silhouette.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),                                            # 0 ★ prompt: "4 overlapping white ellipses"
        ], weight=0.2, critical=[0]),

        AlignmentRubric([
            LayersAllShareEdge(layer_type="ellipse", edge="bottom", tolerance=40.0),    # 0 ★ prompt: "Their bottoms roughly share a horizontal line"
            LayersOverlap(type_a="ellipse", type_b="ellipse"),                          # 1 ★ prompt: "4 overlapping ... ellipses"
            LayerSizeAtLeast(layer_type="ellipse", min_w=20, min_h=20),                 # 2 no degenerate

            LayersAtDistinctPositions(layer_type="ellipse", min_distinct=3,             # 5 at least 3 distinct centers
                                       tolerance=20.0),
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",            # 6 ellipses sane size vs frame
                                  min_frac=0.04, max_frac=0.50),
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),        # 7 ellipses upright (implicit)
        ], weight=0.2, critical=[0, 1]),

        ColorRubric([
            AllSolidColorEquals(layer_type="ellipse", expected_rgb=WHITE,               # 0 ★ prompt: "all with the same white fill"
                                tolerance=0.28),
            AllFillTypeIs("ellipse", kind="solid"),                                     # 1 every shape needs visible fill
            FillCountAtMost("ellipse", max_count=1),                                    # 2 no stacked fills
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                             # 3 visible fills
            LayerVisible("ellipse"),                                                    # 4 alpha + visible + opacity
            NoLayerFlipped(layer_type="ellipse"),                                       # 5 no flip
            AllStrokeExists("ellipse"),                                                 # 6 prompt does not require strokes; demoted
            AllStrokeWeightWithinTolerance("ellipse", target_weight=1.0,                # 7 each ellipse stroke ~1px (not in prompt)
                                            tolerance=2.5),
            AllStrokeColorEquals("ellipse", expected_rgb=LIGHT_GRAY, tolerance=0.28),   # 8 each ellipse stroke light-gray (not in prompt)
        ], weight=0.2, critical=[0]),

        StructureRubric([

            ChildCountAtLeast("frame", minimum=4),                                      # 1 implicit
        ], weight=0.2, critical=[]),

        EventRubric([
            ToolUsed("ellipse"),                                                        # 0 prompt mentions tool but keyboard-shortcut OK
            EventTypeCount("create_ellipse", equals=4),
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
