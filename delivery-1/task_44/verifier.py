"""
Task 44 — Avatar with status badge (in-scope replacement, no image fill).

Large avatar circle + smaller green status badge circle with 2px white stroke,
overlapping at the bottom-right.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersOverlap, LayerOnTopOf, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors, SolidColorEquals
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

GREEN = {"r": 0.06, "g": 0.72, "b": 0.50}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_44_avatar_status",
    description="1 avatar circle + 1 smaller green status circle with 2px white stroke at bottom-right.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=2),
        ], weight=0.25),

        AlignmentRubric([
            LayersOverlap(type_a="ellipse", type_b="ellipse"),
            LayerOnTopOf(type_a="ellipse", type_b="ellipse"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.10),
            SolidColorEquals(layer_type="ellipse", expected_rgb=GREEN, tolerance=0.25),
            StrokeExists("ellipse"),
            StrokeWeightEquals("ellipse", weight=2.0, tolerance=1.0),
            StrokeColorEquals("ellipse", expected_rgb=WHITE, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
