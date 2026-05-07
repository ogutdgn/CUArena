"""
Task 37 — Yellow sticky note (IN SCOPE).

Yellow square (rotated ~3°) + drop shadow + pen-tool corner fold + 3 horizontal lines.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerBoundsInside, LayerRotationEquals
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.effect_checks import DropShadowExists
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast

YELLOW = {"r": 1.0, "g": 0.92, "b": 0.6}

task = Task(
    id="task_37_sticky_note",
    description="Yellow square (rotated ~3°) + drop shadow + pen-tool fold + 3 horizontal lines.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCountAtLeast("vector", minimum=1),
            ShapeCountAtLeast("line", minimum=3),
        ], weight=0.2),

        AlignmentRubric([
            LayerBoundsInside(inner_type="vector", outer_type="rectangle", tolerance=4.0),
            LayerRotationEquals(layer_type="rectangle", degrees=3.0, tolerance=2.0),
        ], weight=0.2),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            SolidColorEquals(layer_type="rectangle", expected_rgb=YELLOW, tolerance=0.20),
        ], weight=0.2),

        EffectRubric([
            DropShadowExists("rectangle"),
        ], weight=0.2),

        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("pen"),
            ToolUsed("line"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCountAtLeast("create_line", minimum=3),
        ], weight=0.2),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
