"""
Task 13 — Cross-hatch hashtag (in-scope replacement).

2 vertical lines + 2 horizontal lines forming a # symbol.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayersHaveRotations
from verifier.checks.event_checks import ToolUsed, EventTypeCount
task = Task(
    id="task_13_night_sky",
    description="2 vertical + 2 horizontal lines crossing to form a # (hashtag) symbol.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("line", equals=4),
        ], weight=0.34),

        AlignmentRubric([
            LayersHaveRotations(layer_type="line", expected=[0, 90], count_per=2, tolerance_deg=8.0),
        ], weight=0.33),

        EventRubric([
            ToolUsed("line"),
            EventTypeCount("create_line", equals=4),
        ], weight=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
