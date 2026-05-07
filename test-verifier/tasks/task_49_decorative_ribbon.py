"""
Task 49 — Tied ribbon shape (in-scope replacement, no gradient/outline-stroke).

1 pen-tool S-curve drawn with a thick (12px) dashed stroke acting as the ribbon.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeIsDashed
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_49_decorative_ribbon",
    description="1 pen-tool S-curve with a thick (12px) dashed stroke acting as the ribbon.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=1),
        ], weight=0.34),

        ColorRubric([
            StrokeExists("vector"),
            StrokeWeightEquals("vector", weight=12.0, tolerance=2.0),
            StrokeIsDashed("vector"),
        ], weight=0.33),

        EventRubric([
            ToolUsed("pen"),
            EventTypeCountAtLeast("create_vector", minimum=1),
        ], weight=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
