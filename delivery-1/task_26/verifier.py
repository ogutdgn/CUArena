"""
Task 26 — Brand color row (in-scope replacement, no variables).

5 same-size squares arranged in a horizontal row, each filled a different
brand color (1 primary + 4 supports).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, LayersAligned
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_26_color_variable_card",
    description="5 same-size squares in a horizontal row, each a different brand color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=5, tolerance=0.05),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=5),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
