"""
Task 46 — Histogram bars (SIMPLIFIED Medium → Easy).

5 thin vertical rectangles of varying heights, side-by-side with consistent gap,
all sharing a common bottom baseline.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersStacked, LayerEdgesAligned, LayersAllShareEdge
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_46_audio_waveform",
    description="5 vertical bars of varying heights, side-by-side, sharing a bottom baseline.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),
        ], weight=0.25),

        AlignmentRubric([
            LayersStacked(layer_type="rectangle", axis="x", gap_px=4.0, tolerance=8.0),
            LayersAllShareEdge(layer_type="rectangle", edge="bottom", tolerance=6.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.10),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=5),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
