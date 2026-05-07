"""
Task 16 — Speech bubble visual (in-scope replacement, no boolean).

Rounded rectangle (light gray) + small triangle tail (same fill), both with
a 2px dark-gray stroke. Body and tail overlap to form a speech bubble.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersOverlap
from verifier.checks.fill_checks   import AllSolidColorEquals, SameColorAcrossTypes
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

LIGHT_GRAY = {"r": 0.85, "g": 0.85, "b": 0.85}
DARK_GRAY  = {"r": 0.30, "g": 0.30, "b": 0.30}

task = Task(
    id="task_16_speech_bubble",
    description="Rounded rectangle bubble + small triangle tail, both light gray with 2px dark-gray stroke.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCount("polygon",   equals=1),
        ], weight=0.25),

        AlignmentRubric([
            LayersOverlap(type_a="rectangle", type_b="polygon"),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=8.0),
        ], weight=0.25),

        ColorRubric([
            AllSolidColorEquals(layer_type="rectangle", expected_rgb=LIGHT_GRAY, tolerance=0.20),
            AllSolidColorEquals(layer_type="polygon",   expected_rgb=LIGHT_GRAY, tolerance=0.20),
            SameColorAcrossTypes(types=["rectangle", "polygon"], tolerance=0.10),
            StrokeExists("rectangle"),
            StrokeWeightEquals("rectangle", weight=2.0, tolerance=1.0),
            StrokeColorEquals("rectangle", expected_rgb=DARK_GRAY, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("polygon"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_polygon",   equals=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
