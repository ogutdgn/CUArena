"""
Task 23 — Sidebar layout with constraints (IN SCOPE).

1 outer frame + 1 dark-gray sidebar rectangle on the left edge with
constraints: horizontal=left, vertical=stretch (top-to-bottom).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.property     import PropertyRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayerAspectRatioGreaterThan, LayerWidthFraction, AllLayerBoundsInside,
    LayerEdgesAligned, LayerRotationEquals, LayerSizeAtLeast,
)
from verifier.checks.fill_checks   import AllFillTypeIs, SolidColorEquals
from verifier.checks.property_checks import (
    ConstraintHorizontalEquals, ConstraintVerticalEquals,
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

DARK_GRAY = {"r": 0.30, "g": 0.30, "b": 0.30}

task = Task(
    id="task_23_stretchy_sidebar",
    description="Frame + dark-gray sidebar on left edge with constraints horizontal=left, vertical=stretch.",
    rubrics=[
        # critical: exactly 1 sidebar rectangle inside a frame
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),                              # 0 ★ outer frame
            ShapeCount("rectangle", equals=1),                                  # 1 ★ exactly 1
        ], weight=0.20, critical=[0, 1]),

        # critical: tall/narrow, left ~17%, constraints, anchored to frame's left edge
        AlignmentRubric([
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="vertical"),  # 0 ★ "tall narrow"
            LayerWidthFraction(inner_type="rectangle", parent_type="frame",
                               min_frac=0.08, max_frac=0.30),                   # 1 ★ "left 17%"
            ConstraintHorizontalEquals(layer_type="rectangle", value="left"),   # 2 ★ horizontal=left
            ConstraintVerticalEquals(layer_type="rectangle", value="stretch"),  # 3 ★ vertical=stretch
            LayerEdgesAligned(type_a="rectangle", edge_a="left",
                              type_b="frame", edge_b="left", tolerance=8.0),    # 4 ★ on left edge
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=8.0),                                # 5 ★ inside frame
            LayerSizeAtLeast(layer_type="rectangle", min_w=20.0, min_h=600.0),  # 6 ★ tall, full-height-ish
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5, 6]),

        # critical: dark-gray solid + visible
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                           # 0 ★
            SolidColorEquals(layer_type="rectangle", expected_rgb=DARK_GRAY, tolerance=0.20),  # 1 ★ "dark gray"
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),  # 2 ★ visible
        ], weight=0.20, critical=[0, 1, 2]),

        # critical: rectangle (not pill / not rotated / not mirrored)
        PropertyRubric([
            LayerRotationEquals(layer_type="rectangle", degrees=0.0,
                                tolerance=2.0),                                 # 0 ★ unrotated
            NoLayerFlipped(layer_type="rectangle"),                             # 1 ★ no scale gimmicks
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.3),   # 2 ★ rect-shaped not pill
        ], weight=0.15, critical=[0, 1, 2]),

        # critical: frame + rectangle tools used
        EventRubric([
            ToolUsed("frame"),                                                  # 0 ★
            ToolUsed("rectangle"),                                              # 1 ★
            EventTypeCount("create_rectangle", equals=1),                       # 2
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
