"""
Task 48 — Spiderweb pattern (SIMPLIFIED Medium → Easy).

Navy frame + 4 white radial lines (rotated 90° apart) + 2 concentric stroked
hexagons (white stroke).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast, PolygonSidesEquals
from verifier.checks.geometry_checks import LayersConcentric, LayersEvenlyRotated
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals, LayerHasNoFill
from verifier.checks.stroke_checks import StrokeExists, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast

NAVY  = {"r": 0.05, "g": 0.10, "b": 0.45}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_48_spiderweb",
    description="Navy frame + 4 white radial lines (90° apart) + 2 concentric white-stroked hexagons.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("frame",   minimum=1),
            ShapeCountAtLeast("line",    minimum=4),
            ShapeCount("polygon", equals=2),
            PolygonSidesEquals(sides=6),
        ], weight=0.25),

        AlignmentRubric([
            LayerHasNoFill(layer_type="polygon"),
            LayersEvenlyRotated(layer_type="line", n=4, step_deg=90.0, tolerance_deg=10.0),
            LayersConcentric(layer_type="polygon", tolerance=10.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("frame", kind="solid"),
            SolidColorEquals(layer_type="frame", expected_rgb=NAVY, tolerance=0.30),
            StrokeExists("line"),
            StrokeExists("polygon"),
            StrokeColorEquals("line", expected_rgb=WHITE, tolerance=0.20),
            StrokeColorEquals("polygon", expected_rgb=WHITE, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("line"),
            ToolUsed("polygon"),
            EventTypeCountAtLeast("create_line", minimum=4),
            EventTypeCount("create_polygon", equals=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
