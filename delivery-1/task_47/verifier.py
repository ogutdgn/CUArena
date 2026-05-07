"""
Task 47 — Sunburst stamp badge (SIMPLIFIED Medium → Easy).

8-point warm-orange star + smaller centered cream circle on top.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals
from verifier.checks.geometry_checks import LayerBoundsInside, LayerCenteredOnLayer, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

WARM_ORANGE = {"r": 1.0, "g": 0.50, "b": 0.10}
CREAM       = {"r": 1.0, "g": 0.95, "b": 0.80}

task = Task(
    id="task_47_sunburst_badge",
    description="8-point warm-orange star + smaller centered cream circle on top.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("star",    equals=1),
            StarPointsEquals(points=8),
            ShapeCount("ellipse", equals=1),
        ], weight=0.25),

        AlignmentRubric([
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=8.0),
            LayerBoundsInside(inner_type="ellipse", outer_type="star", tolerance=4.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("star",    kind="solid"),
            FillTypeIs("ellipse", kind="solid"),
            SolidColorEquals(layer_type="star",    expected_rgb=WARM_ORANGE, tolerance=0.20),
            SolidColorEquals(layer_type="ellipse", expected_rgb=CREAM,       tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("star"),
            ToolUsed("ellipse"),
            EventTypeCount("create_star",    equals=1),
            EventTypeCount("create_ellipse", equals=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
