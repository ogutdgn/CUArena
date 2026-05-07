"""
Task 06 — Gold burst (in-scope replacement, no boolean exclude).

8 lines radiating from a single center point at 45° intervals, gold stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayersEvenlyRotated
from verifier.checks.stroke_checks import StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

GOLD = {"r": 0.85, "g": 0.65, "b": 0.13}

task = Task(
    id="task_06_gold_star_exclude",
    description="8 lines radiating from a center at 45° intervals, with gold strokes.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("line", equals=8),
        ], weight=0.25),

        AlignmentRubric([
            LayersConcentric(layer_type="line", tolerance=10.0),
            LayersEvenlyRotated(layer_type="line", n=8, step_deg=45.0, tolerance_deg=8.0),
        ], weight=0.25),

        ColorRubric([
            StrokeColorEquals(layer_type="line", expected_rgb=GOLD, tolerance=0.25),
        ], weight=0.25),

        EventRubric([
            ToolUsed("line"),
            EventTypeCount("create_line", equals=8),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
