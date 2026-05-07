"""
Task 22 — Tag pill row (in-scope replacement, no auto-layout).

4 same-size rounded rectangles (radius 999) placed side-by-side in a row
with a small gap, each a different pastel fill.
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
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_22_tag_pills",
    description="4 same-size rounded pills (radius ≥24) in a horizontal row, different pastel fills.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
            LayersStacked(layer_type="rectangle", axis="x", gap_px=8.0, tolerance=8.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=24.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=4, tolerance=0.05),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
