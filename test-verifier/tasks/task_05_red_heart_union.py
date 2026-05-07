"""
Task 05 — Plus-sign emblem (in-scope replacement).

2 perpendicular rectangles crossed at center to form a + shape.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersAligned, LayersHaveAspectMix
from verifier.checks.fill_checks   import FillTypeIs, AllSolidColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_05_red_heart_union",
    description="2 perpendicular rectangles crossed at center forming a plus sign, both red fill.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
        ], weight=0.25),

        AlignmentRubric([
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=5.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
            LayersHaveAspectMix(layer_type="rectangle",
                                horizontal_count=1, vertical_count=1, ratio=2.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            AllSolidColorEquals(layer_type="rectangle",
                                expected_rgb={"r": 1.0, "g": 0.1, "b": 0.1},
                                tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
