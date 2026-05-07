"""
Task 27 — Neumorphic button (in-scope replacement, no inner shadow).

A 200×200 light-gray rounded rectangle with two paired drop shadows
(highlight + shadow), creating a soft pressed look.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayerSizeEquals
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.effect_checks import DropShadowExists, EffectCount
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

LIGHT_GRAY = {"r": 0.88, "g": 0.90, "b": 0.93}

task = Task(
    id="task_27_neumorphic_button",
    description="200×200 light-gray rounded rectangle with two paired drop shadows.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
        ], weight=0.2),

        AlignmentRubric([
            LayerSizeEquals(layer_type="rectangle", width=200, height=200, tolerance=10.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=16.0),
        ], weight=0.2),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            SolidColorEquals(layer_type="rectangle", expected_rgb=LIGHT_GRAY, tolerance=0.15),
        ], weight=0.2),

        EffectRubric([
            DropShadowExists("rectangle"),
            EffectCount(layer_type="rectangle", equals=2),  # 2 paired shadows
        ], weight=0.2),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=1),
        ], weight=0.2),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
