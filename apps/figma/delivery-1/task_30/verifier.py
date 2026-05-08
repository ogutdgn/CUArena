"""
Task 30 — Vertical stripe wallpaper (IN SCOPE).

6 vertical stripe rectangles alternating deep-blue / cream, filling a 600×600 frame.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersAligned, LayersStacked,
    LayerAspectRatioGreaterThan, LayersAlternatingColors,
    LayerRotationEquals, AllLayerBoundsInside, LayerSizeAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, LayersHaveColorOrder, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible,
)
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

DEEP_BLUE = {"r": 0.10, "g": 0.20, "b": 0.55}
CREAM     = {"r": 1.00, "g": 0.95, "b": 0.80}

task = Task(
    id="task_30_stripe_wallpaper",
    description="6 vertical stripes alternating deep-blue/cream filling a frame.",
    rubrics=[
        # critical: 6 stripes inside a frame
        FundamentalsRubric([
            ShapeCount("rectangle", equals=6),                                  # 0 ★ prompt: "6 ... vertical rectangle stripes"
            ShapeCountAtLeast("frame", minimum=1),                              # 1 ★ prompt: "Inside a 600x600 frame"
        ], weight=0.2, critical=[0, 1]),

        # critical: same-size, vertical, stacked, alternating
        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=8.0),         # 0 ★ prompt: "6 same-size vertical rectangle stripes"
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=12.0),  # 1 y-aligned
            LayersStacked(layer_type="rectangle", axis="x", gap_px=0.0, tolerance=12.0),  # 2 ★ prompt: "filling the frame width"
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="vertical"),  # 3 ★ prompt: "vertical ... stripes"
            LayersAlternatingColors(layer_type="rectangle", n_colors=2, sort_axis="x"),  # 4 ★ prompt: "alternating two colors"
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),       # 5 stripes upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),           # 6 frame upright
            NoLayerFlipped(layer_type="rectangle"),                                       # 7 not flipped
            LayerSizeAtLeast(layer_type="rectangle", min_w=10, min_h=100),                # 8 no degenerate stripes
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=10.0),  # 9 stripes inside frame
        ], weight=0.2, critical=[0, 2, 3, 4]),

        # critical: solid fills
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                           # 0 ★ every shape needs visible fill
            LayersHaveColorOrder(
                layer_type="rectangle",
                expected_rgbs=[DEEP_BLUE, CREAM, DEEP_BLUE, CREAM, DEEP_BLUE, CREAM],
                sort_axis="x",
                tolerance=0.25,
            ),                                                                   # 1
            FillCountAtMost(layer_type="rectangle", max_count=1),               # 2 no stacked fills
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),        # 3 visible fill
            LayerVisible(layer_type="rectangle"),                               # 4 alpha + visibility
        ], weight=0.2, critical=[0]),

        # all stripes in same frame (structural)
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="rectangle", minimum=6),        # 0 ★ all stripes share parent frame
        ], weight=0.2, critical=[0]),

        # rectangle tool used
        EventRubric([
            ToolUsed("rectangle"),                                              # 0
            EventTypeCount("create_rectangle", equals=6),                       # 1
        ], weight=0.2, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
