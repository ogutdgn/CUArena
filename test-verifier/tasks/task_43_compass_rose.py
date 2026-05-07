"""
Task 43 — Compass rose (IN SCOPE).

Sand-colored circle + 4 triangles arranged 90° apart (cardinal directions, distinct colors)
+ small gold center pivot circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, LayersEvenlyRotated, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_43_compass_rose",
    description="Sand circle + 4 N/E/S/W triangles (90° apart, distinct colors) + gold center pivot.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=2),
            ShapeCount("polygon", equals=4),
        ], weight=0.25),

        AlignmentRubric([
            LayersSameDimensions(layer_type="polygon", tolerance=3.0),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=10.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("polygon", kind="solid"),
            FillTypeIs("ellipse", kind="solid"),
            DistinctSolidColors(minimum=4, tolerance=0.10),  # sand + gold + ≥2 triangle hues (red N + gray others)
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_ellipse", equals=2),
            EventTypeCount("create_polygon", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
