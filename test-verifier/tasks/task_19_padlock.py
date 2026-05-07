"""
Task 19 — Padlock icon (IN SCOPE).

Rectangle body (rounded corner radius 12, dark gray) + pen-drawn U-shaped
shackle (14px stroke) above + small black keyhole circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerBoundsInside, LayersOverlap, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals
from verifier.checks.property_checks import CornerRadiusEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

DARK_GRAY = {"r": 0.30, "g": 0.30, "b": 0.30}
BLACK     = {"r": 0.0,  "g": 0.0,  "b": 0.0}

task = Task(
    id="task_19_padlock",
    description="Rounded rectangle body (radius 12, dark gray) + pen U-shackle (14px stroke) + black keyhole circle.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("rectangle", minimum=1),
            ShapeCountAtLeast("vector", minimum=1),
            ShapeCountAtLeast("ellipse", minimum=1),
        ], weight=0.25),

        AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="rectangle", tolerance=4.0),
            LayersOverlap(type_a="vector", type_b="rectangle"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
            CornerRadiusEquals(layer_type="rectangle", radius=12.0, tolerance=4.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            SolidColorEquals(layer_type="rectangle", expected_rgb=DARK_GRAY, tolerance=0.25),
            SolidColorEquals(layer_type="ellipse",   expected_rgb=BLACK,     tolerance=0.20),
            StrokeExists("vector"),
            StrokeWeightEquals("vector", weight=14.0, tolerance=2.0),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("pen"),
            ToolUsed("ellipse"),
            EventTypeCountAtLeast("create_rectangle", minimum=1),
            EventTypeCountAtLeast("create_vector", minimum=1),
            EventTypeCountAtLeast("create_ellipse", minimum=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
