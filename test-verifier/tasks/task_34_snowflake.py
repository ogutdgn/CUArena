"""
Task 34 — 4-fold symmetric snowflake (SIMPLIFIED Medium → Easy).

Navy frame + 4 white line branches rotated 90° each around the center.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayersEvenlyRotated
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.stroke_checks import StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

NAVY  = {"r": 0.05, "g": 0.10, "b": 0.45}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_34_snowflake",
    description="Navy frame + 4 white line branches rotated 90° apart for 4-fold symmetry.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("line", equals=4),
        ], weight=0.25),

        AlignmentRubric([
            LayersEvenlyRotated(layer_type="line", n=4, step_deg=90.0, tolerance_deg=10.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("frame", kind="solid"),
            SolidColorEquals(layer_type="frame", expected_rgb=NAVY, tolerance=0.30),
            StrokeColorEquals(layer_type="line", expected_rgb=WHITE, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("line"),
            EventTypeCount("create_line", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
