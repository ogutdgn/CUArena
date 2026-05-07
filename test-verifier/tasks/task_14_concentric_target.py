"""
Task 14 — Concentric ring target / dartboard (IN SCOPE).

4 concentric circles, alternating red/white outermost-to-center,
all centered on each other, each with a 4px black stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayerBoundsInside, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, LayersHaveColorOrder
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

RED   = {"r": 0.9, "g": 0.15, "b": 0.15}
WHITE = {"r": 1.0, "g": 1.0,  "b": 1.0}
BLACK = {"r": 0.0, "g": 0.0,  "b": 0.0}

task = Task(
    id="task_14_concentric_target",
    description="4 concentric ellipses alternating red/white outermost→center, each with 4px black stroke.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),
        ], weight=0.25),

        AlignmentRubric([
            LayersConcentric(layer_type="ellipse", tolerance=2.0),
            LayerBoundsInside(inner_type="ellipse", outer_type="ellipse", tolerance=2.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            LayersHaveColorOrder(
                layer_type="ellipse",
                expected_rgbs=[RED, WHITE, RED, WHITE],
                sort_axis="size",
                tolerance=0.20,
            ),
            StrokeExists("ellipse"),
            StrokeWeightEquals("ellipse", weight=4.0, tolerance=1.0),
            StrokeColorEquals("ellipse", expected_rgb=BLACK, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
