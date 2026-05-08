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
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayerBoundsInside, LayerEdgesAligned, LayerSizeAtLeast,
    AllLayerBoundsInside, LayerRotationEquals, LayerCenteredOnLayer,
    LayerIsCircular, LayerAspectRatioGreaterThan, CrossTypeAreaRatioAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.effect_checks import DropShadowExists, VisibleDropShadowExists
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, NoLayerFlipped, LayerVisible,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.structure_checks import LayerInsideFrame

GREEN = {"r": 0.20, "g": 0.78, "b": 0.35}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_40_toggle_switch",
    description="Green pill rectangle + white circle thumb on the right with a small drop shadow.",
    rubrics=[
        # critical: prompt mandates 1 pill + 1 thumb
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),                         # 0 ★ prompt: "green pill"
            ShapeCount("ellipse",   equals=1),                         # 1 ★ prompt: "white circle thumb"
            LayerSizeAtLeast(layer_type="rectangle", min_w=20, min_h=10),  # 2 no degenerate pill
            LayerSizeAtLeast(layer_type="ellipse",   min_w=8,  min_h=8),   # 3 no 1×1 thumb
            NoLayerFlipped(layer_type="rectangle"),                    # 4 no scaleX=-1
            NoLayerFlipped(layer_type="ellipse"),                      # 5 no scaleX=-1
        ], weight=0.16, critical=[0, 1]),

        # critical: thumb inside pill, large corner radius, right-edge positioning
        AlignmentRubric([
            LayerBoundsInside(inner_type="ellipse", outer_type="rectangle", tolerance=10.0),  # 0 ★ prompt: "thumb ... 2px from the right edge" (inside pill)
            CornerRadiusAtLeast(layer_type="rectangle", min_value=15.0),                     # 1 ★ prompt: "radius 999"
            LayerEdgesAligned(type_a="ellipse", edge_a="right",                              # 2 ★ prompt: "2px from the right edge"
                              type_b="rectangle", edge_b="right", tolerance=15.0),
            LayerRotationEquals(layer_type="rectangle", degrees=0.0, tolerance=5.0),         # 3 pill upright
            LayerRotationEquals(layer_type="frame",     degrees=0.0, tolerance=5.0),         # 4 frame upright
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=8.0), # 5 pill in frame
            AllLayerBoundsInside(inner_type="ellipse",   outer_type="frame", tolerance=8.0), # 6 thumb in frame
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                            # 7 ★ prompt: "white CIRCLE thumb"
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=1.2, axis="horizontal"),# 8 pill wider than tall
            LayerCenteredOnLayer(type_a="ellipse", type_b="rectangle",                        # 9 thumb y-centered on pill
                                  tolerance=15.0, axis="y"),
            CrossTypeAreaRatioAtLeast(big_type="frame", small_type="rectangle",              # 10 pill smaller than frame
                                       min_ratio=10.0),
        ], weight=0.20, critical=[0, 1, 2, 7]),

        # critical: green pill + white thumb are prompt-explicit
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                         # 0 ★ visible fill type
            AllFillTypeIs("ellipse",   kind="solid"),                                         # 1 every shape needs solid fill
            SolidColorEquals(layer_type="rectangle", expected_rgb=GREEN, tolerance=0.18),     # 2 ★ prompt: "green pill"
            SolidColorEquals(layer_type="ellipse",   expected_rgb=WHITE, tolerance=0.10),     # 3 ★ prompt: "white circle"
            FillCountAtMost(layer_type="rectangle", max_count=1),                             # 4 no stacked fills
            FillCountAtMost(layer_type="ellipse",   max_count=1),                             # 5 no stacked fills
            LayerVisible(layer_type="rectangle"),                                             # 6 pill visible
            LayerVisible(layer_type="ellipse"),                                               # 7 thumb visible
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),                      # 8 visible fill
            FillOpacityAtLeast(layer_type="ellipse",   min_opacity=0.5),                      # 9 visible fill
        ], weight=0.20, critical=[0, 2, 3]),

        # effect: drop shadow not in simplified prompt — soft only
        EffectRubric([
            DropShadowExists("ellipse"),                                                      # 0 thorough-desc bonus
            VisibleDropShadowExists("ellipse"),                                               # 1 thorough-desc bonus
        ], weight=0.12, critical=[]),

        # structure: shapes inside a frame
        StructureRubric([
            LayerInsideFrame(layer_type="rectangle"),                                          # 0 ★ inside frame
            LayerInsideFrame(layer_type="ellipse"),                                            # 1 thumb inside frame
        ], weight=0.10, critical=[0]),

        # event: tool-used checks kept soft per playbook
        EventRubric([
            ToolUsed("rectangle"),                            # 0
            ToolUsed("ellipse"),                              # 1
            EventTypeCount("create_rectangle", equals=1),     # 2
            EventTypeCount("create_ellipse",   equals=1),     # 3
        ], weight=0.16, critical=[]),

        # property: no stacked fills on pill
        FundamentalsRubric([
            FillCountAtMost(layer_type="rectangle", max_count=1),                              # 0 no stacked fills
        ], weight=0.06, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
