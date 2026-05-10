"""
Task 05 — Plus-sign emblem (in-scope replacement).

2 perpendicular rectangles crossed at center to form a + shape, both filled the same color.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersAligned, LayersHaveAspectMix
from verifier.checks.fill_checks   import LayersAllSameColor
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_05_red_heart_union",
    description="2 perpendicular rectangles crossed at center forming a plus sign, same color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),                                        # 0 ★ prompt: "2 perpendicular rectangles"
        ], weight=0.20, critical=[0]),

        AlignmentRubric([
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=12.0),   # 0 ★ prompt: "centered together"
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=12.0),   # 1 ★ prompt: "centered together"
            LayersHaveAspectMix(layer_type="rectangle",                               # 2 ★ prompt: "horizontal rectangle is wide and short; the vertical rectangle is narrow and tall"
                                horizontal_count=1, vertical_count=1, ratio=2.0),
        ], weight=0.40, critical=[0, 1, 2]),

        # "same color" — uniformity, no specific RGB
        ColorRubric([
            LayersAllSameColor(layer_type="rectangle", tolerance=0.12),               # 0 ★ prompt: "Pick same color for both"
        ], weight=0.30, critical=[0]),

        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCountAtLeast("create_rectangle", minimum=2),                     # 1
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
