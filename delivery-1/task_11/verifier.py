"""
Task 11 — Triangle pyramid stack (in-scope replacement).

3 triangles of decreasing size all centered together (largest at back, smallest at front),
alternating two colors, forming a layered pyramid look.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayerBoundsInside
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_11_pressed_button",
    description="3 triangles of decreasing size centered together, alternating two colors.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon", equals=3),
        ], weight=0.25),

        AlignmentRubric([
            LayersConcentric(layer_type="polygon", tolerance=5.0),
            LayerBoundsInside(inner_type="polygon", outer_type="polygon", tolerance=2.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("polygon", kind="solid"),
        ], weight=0.25),

        EventRubric([
            ToolUsed("polygon"),
            EventTypeCount("create_polygon", equals=3),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
