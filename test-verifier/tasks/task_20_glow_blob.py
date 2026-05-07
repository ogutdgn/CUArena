"""
Task 20 — Glow blob backdrop (IN SCOPE).

Dark navy frame + 2 overlapping blurred circles (magenta + cyan).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayersOverlap, LayerIsCircular
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals, DistinctSolidColors
from verifier.checks.effect_checks import LayerBlurExists, BlurRadiusEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

NAVY = {"r": 0.05, "g": 0.10, "b": 0.45}

task = Task(
    id="task_20_glow_blob",
    description="Dark navy frame + 2 overlapping blurred circles (distinct fills).",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("ellipse", equals=2),
        ], weight=0.2),

        AlignmentRubric([
            LayersOverlap(type_a="ellipse", type_b="ellipse"),
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),
        ], weight=0.2),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            FillTypeIs("frame",   kind="solid"),
            SolidColorEquals(layer_type="frame", expected_rgb=NAVY, tolerance=0.30),
            DistinctSolidColors(minimum=3, tolerance=0.10),  # navy frame + 2 distinct circles
        ], weight=0.2),

        EffectRubric([
            LayerBlurExists("ellipse"),
            BlurRadiusEquals(layer_type="ellipse", radius=80.0, tolerance=20.0),
        ], weight=0.2),

        EventRubric([
            ToolUsed("frame"),
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=2),
        ], weight=0.2),
    ],
    efficiency=EfficiencyRubric(target_turns=22),
)
