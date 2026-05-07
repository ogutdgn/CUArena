"""
Task 40 — iOS toggle switch (IN SCOPE).

Green pill (rounded rectangle, radius ≥24, ~#34C759) + white circle thumb
positioned on the right with a small drop shadow.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayerBoundsInside, LayerEdgesAligned
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.effect_checks import DropShadowExists
from verifier.checks.property_checks import CornerRadiusAtLeast
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

GREEN = {"r": 0.20, "g": 0.78, "b": 0.35}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_40_toggle_switch",
    description="Green pill rectangle + white circle thumb on the right with a small drop shadow.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCount("ellipse",   equals=1),
        ], weight=0.2),

        AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="rectangle", tolerance=4.0),
            CornerRadiusAtLeast(layer_type="rectangle", min_value=24.0),
            LayerEdgesAligned(type_a="ellipse", edge_a="right",
                              type_b="rectangle", edge_b="right", tolerance=8.0),
        ], weight=0.2),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            FillTypeIs("ellipse",   kind="solid"),
            SolidColorEquals(layer_type="rectangle", expected_rgb=GREEN, tolerance=0.20),
            SolidColorEquals(layer_type="ellipse",   expected_rgb=WHITE, tolerance=0.10),
        ], weight=0.2),

        EffectRubric([
            DropShadowExists("ellipse"),
        ], weight=0.2),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_ellipse",   equals=1),
        ], weight=0.2),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
