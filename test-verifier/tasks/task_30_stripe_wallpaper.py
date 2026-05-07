"""
Task 30 — Vertical stripe wallpaper (IN SCOPE).

6 vertical stripe rectangles alternating deep-blue / cream, filling a 600×600 frame.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersAligned, LayersStacked,
    LayerAspectRatioGreaterThan, LayersAlternatingColors,
)
from verifier.checks.fill_checks   import FillTypeIs, LayersHaveColorOrder
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

DEEP_BLUE = {"r": 0.10, "g": 0.20, "b": 0.55}
CREAM     = {"r": 1.00, "g": 0.95, "b": 0.80}

task = Task(
    id="task_30_stripe_wallpaper",
    description="6 vertical stripes alternating deep-blue/cream filling a frame.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=6),
            ShapeCountAtLeast("frame", minimum=1),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=2.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),
            LayersStacked(layer_type="rectangle", axis="x", gap_px=0.0, tolerance=8.0),
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="vertical"),
            LayersAlternatingColors(layer_type="rectangle", n_colors=2, sort_axis="x"),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            LayersHaveColorOrder(
                layer_type="rectangle",
                expected_rgbs=[DEEP_BLUE, CREAM, DEEP_BLUE, CREAM, DEEP_BLUE, CREAM],
                sort_axis="x",
                tolerance=0.25,
            ),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=6),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
