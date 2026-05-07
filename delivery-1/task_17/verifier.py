"""
Task 17 — Hourglass shape (in-scope replacement, no boolean).

2 triangles point-to-point at the center + 2 horizontal rectangle caps (top and bottom).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersAligned, LayersHaveRotations
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_17_play_button",
    description="2 triangles point-to-point + 2 horizontal rectangle caps top and bottom.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon",   equals=2),
            ShapeCount("rectangle", equals=2),
        ], weight=0.25),

        AlignmentRubric([
            LayersAligned(layer_type="polygon",   axis="center_x", tolerance=5.0),
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=5.0),
            LayersHaveRotations(layer_type="polygon", expected=[0, 180], count_per=1, tolerance_deg=8.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("polygon",   kind="solid"),
            FillTypeIs("rectangle", kind="solid"),
        ], weight=0.25),

        EventRubric([
            ToolUsed("polygon"),
            ToolUsed("rectangle"),
            EventTypeCount("create_polygon",   equals=2),
            EventTypeCount("create_rectangle", equals=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
