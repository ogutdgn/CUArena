"""
Task 36 — Tilted vintage frame (in-scope replacement, no image fill).

Outer rectangle (white) tilted ~5°, with a drop shadow, plus a smaller inner
artwork rectangle inside it. Both share x-center; inner shifted up so the
bottom margin is thicker (caption area).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayerBoundsInside, LayerRotationEquals
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.effect_checks import DropShadowExists
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

WHITE = {"r": 1.0, "g": 1.0, "b": 1.0}

task = Task(
    id="task_36_polaroid",
    description="2 rectangles (outer white, tilted ~5°, with drop shadow) + smaller inner artwork rect.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
        ], weight=0.2),

        AlignmentRubric([
            LayerBoundsInside(inner_type="rectangle", outer_type="rectangle", tolerance=8.0),
            LayerRotationEquals(layer_type="rectangle", degrees=5.0, tolerance=3.0),
        ], weight=0.2),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            SolidColorEquals(layer_type="rectangle", expected_rgb=WHITE, tolerance=0.15),
        ], weight=0.2),

        EffectRubric([
            DropShadowExists("rectangle"),
        ], weight=0.2),

        EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=2),
        ], weight=0.2),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
