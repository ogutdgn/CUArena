"""
Task 01 verifier (two-story house) — end-state only, strict 1.0 contract.

QA contract for this task:
1) Correct end-state must score 1.0
2) Improper end-state must score < 1.0
3) Correct + extra trash objects must score < 1.0

This verifier intentionally ignores process/tool/event logs.
"""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersAligned,
    LayersFlankLayer,
    LayersSameDimensions,
    LayerIsCircular,
    SmallerLayerInsideLarger,
    LayerCenteredOnLayer,
    FrameSizeEquals,
    AllLayerBoundsInside,
    LayerAreaRatioAtLeast,
)
from verifier.checks.fill_checks import AllFillTypeIs, DistinctSolidColors
from verifier.checks.structure_checks import (
    LayerInsideFrame,
    ChildCount,
    LayerTotalCount,
    NoUnexpectedLayerTypes,
)
from verifier.checks.property_checks import LayerVisible


task = Task(
    id="house_task_end_state_strict",
    description=(
        "Build a simple house inside a 1280x832 frame: "
        "2 rectangles (body + door), 1 triangle roof, 2 round windows, "
        "with distinct fills and no extra objects."
    ),

    # End-state only. 4 rubrics × 0.25 = base max 1.0
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
            ShapeCount("ellipse", equals=2),
            ShapeCount("polygon", equals=1),
            PolygonSidesEquals(sides=3),
        ], weight=0.25, critical=[0, 1, 2, 3]),

        AlignmentRubric([
            # 2 round windows with same size on either side of the door.
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=25.0),
            LayersSameDimensions(layer_type="ellipse", tolerance=25.0),
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),
            LayersFlankLayer(flanker_type="ellipse", pivot_type="rectangle", axis="x", tolerance=20.0),
            # Door is on the body.
            SmallerLayerInsideLarger(layer_type="rectangle", tolerance=12.0),
            # Roof is centered over body.
            LayerCenteredOnLayer(type_a="polygon", type_b="rectangle", axis="x", tolerance=20.0),
            # Everything remains inside frame.
            FrameSizeEquals(width=1280, height=832, tolerance=25.0),
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=10.0),
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=10.0),
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame", tolerance=10.0),
            # Body must remain meaningfully larger than the door.
            LayerAreaRatioAtLeast(layer_type="rectangle", min_ratio=2.0),
        ], weight=0.25, critical=[2, 3, 4, 5, 6]),

        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),
            AllFillTypeIs("polygon", kind="solid"),
            AllFillTypeIs("ellipse", kind="solid"),
            DistinctSolidColors(minimum=4, tolerance=0.12),
            LayerVisible("rectangle"),
            LayerVisible("polygon"),
            LayerVisible("ellipse"),
        ], weight=0.25, critical=[0, 1, 2, 3]),

        StructureRubric([
            LayerInsideFrame("rectangle"),
            LayerInsideFrame("polygon"),
            LayerInsideFrame("ellipse"),
            # Exactly one frame holding exactly the 5 expected house shapes.
            ChildCount("frame", equals=5),
            # Reject any unexpected primitive types even if counts are manipulated.
            NoUnexpectedLayerTypes(allowed_types=["rectangle", "ellipse", "polygon"]),
            # No extra layers anywhere (frame + 5 shapes = 6 total).
            LayerTotalCount(equals=6),
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5]),
    ],

    # End-state-only scoring: disable turn-count penalty.
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
