"""
Task 04 — Color hexagon ring (in-scope replacement).

6 squares arranged in a hexagonal ring, each filled a different rainbow color
(red, yellow, green, cyan, blue, magenta).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, RadialDistribution, LayerIsSquare
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_04_color_wheel",
    description="6 same-size squares arranged in a hexagonal ring, each filled a different rainbow color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=6),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),
            RadialDistribution(layer_type="rectangle", n=6, tolerance_deg=10.0),
            LayerIsSquare(layer_type="rectangle", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=6, tolerance=0.05),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=6),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
