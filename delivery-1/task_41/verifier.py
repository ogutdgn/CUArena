"""
Task 41 — Search bar (SIMPLIFIED Medium → Easy).

320×48 rounded light-gray bar + magnifying-glass icon (small stroked circle +
diagonal line) + 1 placeholder dot.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerIsCircular, LayerSizeEquals
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast

LIGHT_GRAY = {"r": 0.95, "g": 0.95, "b": 0.95}

task = Task(
    id="task_41_search_bar",
    description="320×48 rounded light-gray bar + small magnifier (stroked circle + line) + 1 dot.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCountAtLeast("ellipse", minimum=2),
            ShapeCountAtLeast("line", minimum=1),
        ], weight=0.25),

        AlignmentRubric([
            LayerSizeEquals(layer_type="rectangle", width=320, height=48, tolerance=12.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=20.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            SolidColorEquals(layer_type="rectangle", expected_rgb=LIGHT_GRAY, tolerance=0.15),
            StrokeExists("ellipse"),
            StrokeWeightEquals("ellipse", weight=2.0, tolerance=1.0),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            ToolUsed("line"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCountAtLeast("create_ellipse", minimum=2),
            EventTypeCountAtLeast("create_line", minimum=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
