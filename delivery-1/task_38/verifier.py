"""
Task 38 — Battery indicator (IN SCOPE).

Rounded outer body rectangle (gray stroke) + small terminal rectangle on right
+ 3 colored level-bar rectangles inside.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersAligned
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.stroke_checks import StrokeExists
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_38_battery_indicator",
    description="Battery body (rounded, gray stroke) + terminal + 3 colored bars (5 rectangles total).",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),
        ], weight=0.25),

        AlignmentRubric([
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=40.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=4.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=3, tolerance=0.10),
            StrokeExists("rectangle"),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=5),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
