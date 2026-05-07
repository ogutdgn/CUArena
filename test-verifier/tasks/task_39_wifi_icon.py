"""
Task 39 — Wifi signal icon (SIMPLIFIED Medium → Easy).

2 concentric pen-tool arcs (6px navy stroke) above a small navy filled circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast, EventTypeCount

NAVY = {"r": 0.05, "g": 0.10, "b": 0.45}

task = Task(
    id="task_39_wifi_icon",
    description="2 pen-tool arcs (6px navy stroke) above 1 small navy circle.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=2),
            ShapeCount("ellipse", equals=1),
        ], weight=0.34),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            SolidColorEquals(layer_type="ellipse", expected_rgb=NAVY, tolerance=0.30),
            StrokeExists("vector"),
            StrokeWeightEquals("vector", weight=6.0, tolerance=2.0),
            StrokeColorEquals("vector", expected_rgb=NAVY, tolerance=0.30),
        ], weight=0.33),

        EventRubric([
            ToolUsed("pen"),
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_vector", minimum=2),
            EventTypeCount("create_ellipse", equals=1),
        ], weight=0.33),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
