"""
Task 45 — Layered geometric emblem (IN SCOPE).

Deep-blue 8-point star + smaller centered yellow circle on top.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals
from verifier.checks.geometry_checks import LayerBoundsInside, LayerCenteredOnLayer, LayerOnTopOf, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

DEEP_BLUE = {"r": 0.10, "g": 0.20, "b": 0.60}
YELLOW    = {"r": 1.0,  "g": 0.85, "b": 0.20}

task = Task(
    id="task_45_geometric_emblem",
    description="Deep-blue 8-point star + smaller yellow circle centered on top.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("star",    equals=1),
            StarPointsEquals(points=8),
            ShapeCount("ellipse", equals=1),
        ], weight=0.25),

        AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="star", tolerance=4.0),
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=8.0),
            LayerOnTopOf(type_a="ellipse", type_b="star"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("star",    kind="solid"),
            FillTypeIs("ellipse", kind="solid"),
            SolidColorEquals(layer_type="star",    expected_rgb=DEEP_BLUE, tolerance=0.25),
            SolidColorEquals(layer_type="ellipse", expected_rgb=YELLOW,    tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("star"),
            ToolUsed("ellipse"),
            EventTypeCount("create_star",    equals=1),
            EventTypeCount("create_ellipse", equals=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
