"""
Task 28 — Photo placeholder mockup (in-scope replacement, no image fill).

1 large rectangle (placeholder) + 2 diagonal lines drawn from corner to corner forming an X-cross.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LinesOnDiagonal
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_28_edited_photo",
    description="Large rectangle placeholder + 2 diagonal lines crossing through it.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCount("line",      equals=2),
        ], weight=0.25),

        AlignmentRubric([
            LinesOnDiagonal(rect_type="rectangle", line_type="line", tolerance=12.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("line"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_line",      equals=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
