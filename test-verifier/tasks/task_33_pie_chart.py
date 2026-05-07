"""
Task 33 — 3-section pie chart (SIMPLIFIED Medium → Easy).

Teal base circle + 2 rotated triangle wedges layered on top in different colors.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayerIsCircular, LayerOnTopOf
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

TEAL = {"r": 0.0, "g": 0.6, "b": 0.6}

task = Task(
    id="task_33_pie_chart",
    description="Teal base circle + 2 colored triangle wedges layered on top.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=1),
            ShapeCount("polygon", equals=2),
        ], weight=0.25),

        AlignmentRubric([
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
            LayerOnTopOf(type_a="polygon", type_b="ellipse"),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            FillTypeIs("polygon", kind="solid"),
            SolidColorEquals(layer_type="ellipse", expected_rgb=TEAL, tolerance=0.25),
            DistinctSolidColors(minimum=3, tolerance=0.10),  # teal + 2 wedge colors
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_ellipse", equals=1),
            EventTypeCount("create_polygon", equals=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
