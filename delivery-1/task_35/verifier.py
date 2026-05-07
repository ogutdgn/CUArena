"""
Task 35 — 2x2 honeycomb pattern (SIMPLIFIED Medium → Easy).

4 yellow hexagons (polygon, 6 sides) arranged in a 2×2 offset honeycomb tiling,
each with a 1px black stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import LayersSameDimensions, OffsetGridLayout
from verifier.checks.fill_checks   import AllSolidColorEquals
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

YELLOW = {"r": 1.0, "g": 0.85, "b": 0.2}
BLACK  = {"r": 0.0, "g": 0.0,  "b": 0.0}

task = Task(
    id="task_35_honeycomb",
    description="2×2 honeycomb of 4 yellow hexagons (6 sides each) with 1px black strokes.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon", equals=4),
            PolygonSidesEquals(sides=6),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=2.0),
            OffsetGridLayout(layer_type="polygon", rows=2, cols=2, tolerance=15.0),
        ], weight=0.25),

        ColorRubric([
            AllSolidColorEquals(layer_type="polygon", expected_rgb=YELLOW, tolerance=0.20),
            StrokeExists("polygon"),
            StrokeWeightEquals("polygon", weight=1.0, tolerance=1.0),
            StrokeColorEquals("polygon", expected_rgb=BLACK, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("polygon"),
            EventTypeCount("create_polygon", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
