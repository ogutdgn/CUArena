"""
Task 05 — Plus-sign emblem (in-scope replacement).

2 perpendicular rectangles crossed at center to form a + shape.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersAligned, LayersHaveAspectMix, LayerSizeAtLeast, LayerRotationEquals,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, AllSolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_05_red_heart_union",
    description="2 perpendicular rectangles crossed at center forming a plus sign, both red fill.",
    rubrics=[
        # critical: exactly 2 rectangles — prompt-explicit
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),                                        # 0 ★ prompt: "2 rectangles"
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=12.0),   # 0 ★ prompt: "their center points aligned"
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=12.0),   # 1 ★ prompt: "their center points aligned"
            LayersHaveAspectMix(layer_type="rectangle",                               # 2 ★ prompt: "horizontal rectangle is wide and short; the vertical rectangle is narrow and tall"
                                horizontal_count=1, vertical_count=1, ratio=2.0),
            LayerSizeAtLeast(layer_type="rectangle", min_w=20.0, min_h=20.0),         # 3
            LayerRotationEquals(layer_type="rectangle", degrees=0.0, tolerance=5.0),  # 4
            NoLayerFlipped(layer_type="rectangle"),                                   # 5
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),         # 6
        ], weight=0.25, critical=[0, 1, 2]),

        # critical: solid fills + same color — prompt-explicit
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                 # 0 ★ prompt: solid fills
            AllSolidColorEquals(layer_type="rectangle",                               # 1 ★ prompt: "Pick same color for both"
                                expected_rgb={"r": 1.0, "g": 0.1, "b": 0.1},
                                tolerance=0.28),
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),     # 2
            FillCountAtMost(layer_type="rectangle", max_count=1),                     # 3
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),              # 4
        ], weight=0.25, critical=[0, 1]),

        # critical: rectangle tool used — prompt-explicit
        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCount("create_rectangle", equals=2),                             # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
