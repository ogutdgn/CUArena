"""
Task 21 — Vertical icon column (in-scope replacement, no auto-layout).

3 same-size rectangles stacked vertically with 16px gap, each a different color,
aligned on the same x center.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, LayersAligned, LayersStacked
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_21_button_stack",
    description="3 same-size rectangles stacked vertically (16px gap), different colors, aligned on x.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=3),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=5.0),
            LayersStacked(layer_type="rectangle", axis="y", gap_px=16.0, tolerance=8.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=3, tolerance=0.05),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=3),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
