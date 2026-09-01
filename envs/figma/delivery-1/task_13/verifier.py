"""
Task 13 — Cross-hatch hashtag (in-scope replacement).

2 vertical lines + 2 horizontal lines forming a # symbol.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color     import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.event     import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import (
    LayersHaveRotations, LayersOverlap, LayerSizeAtLeast,
    AllLayerBoundsInside, LayerRotationEquals, LayersAtDistinctPositions,
)
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible, LayerRendersStrokeOrFill
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks import ToolUsed, EventTypeCount
task = Task(
    id="task_13_night_sky",
    description="2 vertical + 2 horizontal lines crossing to form a # (hashtag) symbol.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("line", equals=4),                                               # 0 ★ prompt: "4 lines"
        ], weight=0.2, critical=[0]),

        AlignmentRubric([
            LayersHaveRotations(layer_type="line", expected=[0, 90], count_per=2,       # 0 ★ prompt: "2 vertical + 2 horizontal"
                                tolerance_deg=10.0),
            LayersOverlap(type_a="line", type_b="line"),                                # 1 ★ prompt: "forming a hashtag (#) shape"
            LayerSizeAtLeast(layer_type="line", min_w=20, min_h=0),                     # 2 no degenerate / pixel lines
            LayersAtDistinctPositions(layer_type="line", min_distinct=4, tolerance=25.0), # 5 no piled-at-one-point
        ], weight=0.2, critical=[0, 1]),

        ColorRubric([
            LayerVisible("line"),                                                       # 0 visible fill (when fills present)
            LayerRendersStrokeOrFill("line"),                                           # 1 lines must render (stroke or fill, implicit from "draw")
            NoLayerFlipped(layer_type="line"),                                          # 2 no mirror/flip
        ], weight=0.2, critical=[]),

        StructureRubric([
            ChildCountAtLeast("frame", minimum=4),                                      # 1 all 4 lines in one frame (implicit)
        ], weight=0.2, critical=[]),

        EventRubric([
            ToolUsed("line"),                                                           # 0 prompt mentions tool but keyboard-shortcut OK
            EventTypeCount("create_line", equals=4),
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
