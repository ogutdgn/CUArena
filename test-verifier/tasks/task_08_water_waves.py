"""
Task 08 — Layered water waves (IN SCOPE).

Two pen-tool wave paths with bezier handles, in different blues, with 4px stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, DistinctStrokeColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_08_water_waves",
    description="Two pen-tool S-curve waves with bezier handles, distinct blue strokes (4px each).",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=2),
        ], weight=0.34),

        ColorRubric([
            StrokeExists("vector"),
            StrokeWeightEquals("vector", weight=4.0, tolerance=1.5),
            DistinctStrokeColors(minimum=2, tolerance=0.05),
        ], weight=0.33),

        EventRubric([
            ToolUsed("pen"),
            EventTypeCountAtLeast("create_vector", minimum=2),
        ], weight=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
