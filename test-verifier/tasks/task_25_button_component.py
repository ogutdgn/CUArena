"""
Task 25 — Identical button row (in-scope replacement, no components).

3 identical 160×40 rectangles placed side-by-side, all same size and same color.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, LayersAligned, LayerSizeEquals, LayersStacked
from verifier.checks.fill_checks   import FillTypeIs, LayersAllSameColor
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_25_button_component",
    description="3 identical 160×40 rectangles in a horizontal row, all same color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=3),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayerSizeEquals(layer_type="rectangle", width=160, height=40, tolerance=4.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=3.0),
            LayersStacked(layer_type="rectangle", axis="x", gap_px=12.0, tolerance=12.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            LayersAllSameColor(layer_type="rectangle", tolerance=0.05),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=3),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
