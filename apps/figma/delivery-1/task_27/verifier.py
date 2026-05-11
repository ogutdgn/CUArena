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
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayerSizeEquals, LayerRotationEquals, AllLayerBoundsInside,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals,
)
from verifier.checks.effect_checks import (
    DropShadowExists, EffectCount, DropShadowCountAtLeast, PairedDropShadowsOpposite,
)
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, CornerRadiusFractionAtMost, NoLayerFlipped,
)
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

LIGHT_GRAY = {"r": 0.88, "g": 0.90, "b": 0.93}

task = Task(
    id="task_27_neumorphic_button",
    description="200×200 light-gray rounded rectangle with two paired drop shadows.",
    rubrics=[
        # critical: exactly 1 rectangle
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),                                  # 0 ★ prompt: "a single 200×200 light-gray rounded rectangle"
        ], weight=0.2, critical=[0]),

        # critical: 200x200 + rounded
        AlignmentRubric([
            LayerSizeEquals(layer_type="rectangle", width=200, height=200, tolerance=25.0),  # 0 ★ prompt: "200×200"
            CornerRadiusAtLeast(layer_type="rectangle", min_value=16.0),        # 1 ★ prompt: "rounded rectangle"
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),   # 2 no full circle
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),  # 3 upright

            NoLayerFlipped(layer_type="rectangle"),                             # 5 not mirrored

        ], weight=0.2, critical=[0, 1]),

        # critical: light-gray solid fill
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                           # 0 solid fill required
            SolidColorEquals(layer_type="rectangle", expected_rgb=LIGHT_GRAY, tolerance=0.25),  # 1 ★ prompt: "light-gray"
        ], weight=0.2, critical=[1]),

        # critical: paired drop shadows (the defining feature of neumorphism)
        EffectRubric([
            DropShadowExists("rectangle"),                                      # 0 drop shadow present
            EffectCount(layer_type="rectangle", equals=2),                      # 1 ★ prompt: "two paired (opposing) drop shadows"
            DropShadowCountAtLeast(layer_type="rectangle", minimum=2),          # 2 ≥2 visible drop shadows
            PairedDropShadowsOpposite(layer_type="rectangle", min_offset=2.0),  # 3 ★ prompt: "opposing drop shadows"
        ], weight=0.2, critical=[1, 3]),

        # rectangle inside a frame (structure)
        StructureRubric([

        ], weight=0.1, critical=[]),

        # rectangle tool used
        EventRubric([
            ToolUsed("rectangle"),                                              # 0
            EventTypeCount("create_rectangle", equals=1),                       # 1
        ], weight=0.1, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
