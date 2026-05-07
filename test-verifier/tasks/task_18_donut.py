"""
Task 18 — Eye icon (in-scope replacement, no boolean).

3 nested ellipses sharing a center: outer (white sclera), middle (colored iris), inner (black pupil).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayerBoundsInside, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_18_donut",
    description="3 nested ellipses (sclera, iris, pupil) sharing a center.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=3),
        ], weight=0.25),

        AlignmentRubric([
            LayersConcentric(layer_type="ellipse", tolerance=3.0),
            LayerBoundsInside(inner_type="ellipse", outer_type="ellipse", tolerance=2.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=3),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
