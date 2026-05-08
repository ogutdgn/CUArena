"""
Task 24 — Centered modal panel (in-scope replacement, no constraints).

Outer frame + white rounded rectangle visually centered inside it (via align)
with a drop shadow.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.property     import PropertyRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayerCenteredInFrame, LayerSizeAtLeast, LayerRotationEquals,
    AllLayerBoundsInside, LayerAspectRatioGreaterThan, LayerWidthFraction,
)
from verifier.checks.fill_checks   import AllFillTypeIs, AllSolidColorEquals
from verifier.checks.effect_checks import DropShadowExists, VisibleDropShadowExists
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, LayerVisible, NoLayerFlipped,
    CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, AlignToolUsed

WHITE = {"r": 1.0, "g": 1.0, "b": 1.0}

task = Task(
    id="task_24_centered_modal",
    description="Outer frame + white rounded rectangle centered inside it via align tool, with a drop shadow.",
    rubrics=[
        # critical: outer frame + 1 rectangle
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),                          # 0 ★ outer frame
            ShapeCount("rectangle", equals=1),                              # 1 ★ exactly 1
        ], weight=0.15, critical=[0, 1]),

        # critical: centered + rounded + non-degenerate + inside-frame
        AlignmentRubric([
            LayerCenteredInFrame(layer_type="rectangle", tolerance=12.0),   # 0 ★ "centered"
            CornerRadiusAtLeast(layer_type="rectangle", min_value=8.0),     # 1 ★ "rounded"
            LayerSizeAtLeast(layer_type="rectangle", min_w=80.0, min_h=60.0),  # 2 ★ non-degenerate
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=8.0),                            # 3 ★ inside frame
            LayerWidthFraction(inner_type="rectangle", parent_type="frame",
                               min_frac=0.10, max_frac=0.85),               # 4 ★ smaller than frame (modal not full)
        ], weight=0.20, critical=[0, 1, 2, 3, 4]),

        # critical: solid white + visible
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                       # 0 ★
            AllSolidColorEquals(layer_type="rectangle", expected_rgb=WHITE, tolerance=0.10),  # 1 ★ "white"
            LayerVisible(layer_type="rectangle", min_opacity=0.5,
                         min_alpha=0.5),                                    # 2 ★ visible
        ], weight=0.20, critical=[0, 1, 2]),

        # critical: drop shadow on modal — must be visible (not alpha=0 / hidden)
        EffectRubric([
            DropShadowExists("rectangle"),                                  # 0 ★ "drop shadow"
            VisibleDropShadowExists(layer_type="rectangle",
                                    min_alpha=0.05),                        # 1 ★ visible
        ], weight=0.15, critical=[0, 1]),

        # critical: rectangle (unrotated, unflipped, not pill)
        PropertyRubric([
            LayerRotationEquals(layer_type="rectangle", degrees=0.0,
                                tolerance=2.0),                             # 0 ★ unrotated
            NoLayerFlipped(layer_type="rectangle"),                         # 1 ★ no flips
            CornerRadiusFractionAtMost(layer_type="rectangle",
                                       max_frac=0.4),                       # 2 ★ rect-shaped (not full pill)
        ], weight=0.15, critical=[0, 1, 2]),

        # critical: rectangle tool + Align tool used (prompt explicit "using align tool")
        EventRubric([
            ToolUsed("rectangle"),                                          # 0 ★
            EventTypeCount("create_rectangle", equals=1),                   # 1
            AlignToolUsed(),                                                # 2 ★ "using align tool"
        ], weight=0.15, critical=[0, 2]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
