"""
Task 15 — Cloud silhouette (in-scope replacement, no boolean union).

4 overlapping ellipses, all white fill with 1px light-gray stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersAligned, LayersOverlap
from verifier.checks.fill_checks   import AllSolidColorEquals
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

WHITE      = {"r": 1.0, "g": 1.0, "b": 1.0}
LIGHT_GRAY = {"r": 0.85, "g": 0.85, "b": 0.85}

task = Task(
    id="task_15_cloud_union",
    description="4 overlapping white ellipses with 1px light-gray strokes forming a cloud silhouette.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=4),
        ], weight=0.25),

        AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=20.0),
            LayersOverlap(type_a="ellipse", type_b="ellipse"),
        ], weight=0.25),

        ColorRubric([
            AllSolidColorEquals(layer_type="ellipse", expected_rgb=WHITE, tolerance=0.10),
            StrokeExists("ellipse"),
            StrokeWeightEquals("ellipse", weight=1.0, tolerance=1.0),
            StrokeColorEquals("ellipse", expected_rgb=LIGHT_GRAY, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=4),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=14),
)
