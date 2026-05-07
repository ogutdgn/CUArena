"""
Task 09 — 12-color swatch grid (in-scope replacement).

12 same-size squares arranged in a 4x3 grid, each filled a different color.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, LayersInGrid
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_09_brand_palette",
    description="4x3 grid of 12 same-size squares, each filled a different color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=12),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersInGrid(layer_type="rectangle", rows=3, cols=4, tolerance=10.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=12, tolerance=0.05),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=12),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
