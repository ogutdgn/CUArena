"""
Task 29 — Polka dot grid (IN SCOPE).

Off-white frame + 4 same-color circles in a 2×2 grid, aligned via Tidy up
(align_layers / distribute_layers events).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayersSameDimensions, LayersInGrid, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, LayersAllSameColor, SolidColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, AlignToolUsed

OFF_WHITE = {"r": 0.97, "g": 0.95, "b": 0.92}

task = Task(
    id="task_29_polka_dot_grid",
    description="Off-white frame + 4 same-color circles in a 2×2 grid via Tidy up.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),
            ShapeCountAtLeast("frame", minimum=1),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="ellipse", tolerance=2.0),
            LayersInGrid(layer_type="ellipse", rows=2, cols=2, tolerance=10.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            LayersAllSameColor(layer_type="ellipse", tolerance=0.05),
            SolidColorEquals(layer_type="frame", expected_rgb=OFF_WHITE, tolerance=0.15),
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=4),
            AlignToolUsed(),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=16),
)
