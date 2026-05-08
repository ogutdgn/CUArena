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
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.effect_checks import (
    DropShadowExists, EffectCount, DropShadowCountAtLeast, PairedDropShadowsOpposite,
)
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, CornerRadiusFractionAtMost, NoLayerFlipped, LayerVisible,
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
            ShapeCount("rectangle", equals=1),                                  # 0 ★ exactly 1
        ], weight=0.2, critical=[0]),

        # critical: 200x200 + rounded (prompt-explicit) + upright + not flipped + inside frame
        AlignmentRubric([
            LayerSizeEquals(layer_type="rectangle", width=200, height=200, tolerance=10.0),  # 0 ★ "200×200"
            CornerRadiusAtLeast(layer_type="rectangle", min_value=16.0),        # 1 ★ "rounded"
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.45),  # 2 ★ no full circle
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=2.0),  # 3 ★ upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),  # 4 ★ frame upright
            NoLayerFlipped(layer_type="rectangle"),                             # 5 ★ not mirrored
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=4.0),  # 6 ★ on-frame
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6]),

        # critical: light-gray solid fill (no stacked, visible, opacity)
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                           # 0 ★
            SolidColorEquals(layer_type="rectangle", expected_rgb=LIGHT_GRAY, tolerance=0.15),  # 1 ★ "light-gray"
            FillCountAtMost(layer_type="rectangle", max_count=1),               # 2 ★ no stacked fills
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),        # 3 ★ visible fill
            LayerVisible(layer_type="rectangle"),                               # 4 ★ alpha + visible
        ], weight=0.2, critical=[0, 1, 2, 3, 4]),

        # critical: paired drop shadows (the defining feature of neumorphism)
        EffectRubric([
            DropShadowExists("rectangle"),                                      # 0 ★ "drop shadows"
            EffectCount(layer_type="rectangle", equals=2),                      # 1 ★ "two paired"
            DropShadowCountAtLeast(layer_type="rectangle", minimum=2),          # 2 ★ both visible drop shadows
            PairedDropShadowsOpposite(layer_type="rectangle", min_offset=2.0),  # 3 ★ paired (highlight+shadow on opposite sides)
        ], weight=0.2, critical=[0, 1, 2, 3]),

        # rectangle inside a frame (structure)
        StructureRubric([
            LayerInsideFrame("rectangle"),                                      # 0 ★ in a frame
        ], weight=0.1, critical=[0]),

        # critical: rectangle tool used
        EventRubric([
            ToolUsed("rectangle"),                                              # 0 ★
            EventTypeCount("create_rectangle", equals=1),                       # 1
        ], weight=0.1, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
