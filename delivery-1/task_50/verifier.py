"""
Task 50 — Star inside square (in-scope replacement, no image fill/mask).

1 large square + 1 5-point star centered on top, contrasting fills,
4px white stroke around the star (substitute for the masked-region border).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals
from verifier.checks.geometry_checks import LayerBoundsInside, LayerCenteredOnLayer
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

WHITE = {"r": 1.0, "g": 1.0, "b": 1.0}

task = Task(
    id="task_50_album_cover",
    description="1 large square + 1 5-point star centered on top, contrasting fills, 4px white stroke on star.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCount("star",      equals=1),
            StarPointsEquals(points=5),
        ], weight=0.25),

        AlignmentRubric([
            LayerBoundsInside(inner_type="star", outer_type="rectangle", tolerance=4.0),
            LayerCenteredOnLayer(type_a="star", type_b="rectangle", tolerance=10.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            FillTypeIs("star",      kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.10),
            StrokeExists("star"),
            StrokeWeightEquals("star", weight=4.0, tolerance=1.0),
            StrokeColorEquals("star", expected_rgb=WHITE, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("star"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_star",      equals=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
