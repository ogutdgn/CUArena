"""
Task 24 — Centered modal panel (in-scope replacement, no constraints).

Outer frame + white rounded rectangle visually centered inside it (via align)
with a drop shadow.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerCenteredInFrame
from verifier.checks.fill_checks   import FillTypeIs, AllSolidColorEquals
from verifier.checks.effect_checks import DropShadowExists
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, AlignToolUsed

WHITE = {"r": 1.0, "g": 1.0, "b": 1.0}

task = Task(
    id="task_24_centered_modal",
    description="Outer frame + white rounded rectangle centered inside it via align tool, with a drop shadow.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("rectangle", equals=1),
        ], weight=0.2),

        AlignmentRubric([
            LayerCenteredInFrame(layer_type="rectangle", tolerance=12.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=8.0),
        ], weight=0.2),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            AllSolidColorEquals(layer_type="rectangle", expected_rgb=WHITE, tolerance=0.10),
        ], weight=0.2),

        EffectRubric([
            DropShadowExists("rectangle"),
        ], weight=0.2),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=1),
            AlignToolUsed(),
        ], weight=0.2),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
