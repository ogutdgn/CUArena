"""
Task 12 — Card row (in-scope replacement).

4 same-size rectangles arranged in a horizontal row with consistent spacing,
all sharing the same y baseline.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, LayersAligned
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_12_shadowed_cards",
    description="4 same-size rectangles in a horizontal row, sharing the same y baseline.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
