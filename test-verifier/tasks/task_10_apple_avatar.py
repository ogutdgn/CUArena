"""
Task 10 — Concentric squares (in-scope replacement).

4 nested squares of decreasing size, alternating two colors, all sharing the same center.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayerBoundsInside
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_10_apple_avatar",
    description="4 nested squares of decreasing size, alternating two colors, sharing center.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),
        ], weight=0.25),

        AlignmentRubric([
            LayersConcentric(layer_type="rectangle", tolerance=3.0),
            LayerBoundsInside(inner_type="rectangle", outer_type="rectangle", tolerance=2.0),
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
