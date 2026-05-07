"""
Task 42 — Notification bell with badge (SIMPLIFIED Medium → Easy).

Pen-tool bell silhouette (yellow-gold) + small clapper circle + red badge with
2px white stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals, DistinctSolidColors
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

GOLD  = {"r": 1.0, "g": 0.80, "b": 0.10}
WHITE = {"r": 1.0, "g": 1.0,  "b": 1.0}

task = Task(
    id="task_42_bell_icon",
    description="Pen bell (yellow-gold) + clapper circle + red badge circle with 2px white stroke.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("vector",  minimum=1),
            ShapeCountAtLeast("ellipse", minimum=2),
        ], weight=0.25),

        AlignmentRubric([
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("vector",  kind="solid"),
            FillTypeIs("ellipse", kind="solid"),
            SolidColorEquals(layer_type="vector", expected_rgb=GOLD, tolerance=0.25),
            DistinctSolidColors(minimum=3, tolerance=0.10),  # gold + clapper + red badge
            StrokeExists("ellipse"),
            StrokeWeightEquals("ellipse", weight=2.0, tolerance=1.0),
            StrokeColorEquals("ellipse", expected_rgb=WHITE, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("pen"),
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_vector",  minimum=1),
            EventTypeCountAtLeast("create_ellipse", minimum=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
