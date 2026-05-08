"""
Task 02 — Sunset stripe band (in-scope replacement).

5 horizontal rectangle bands stacked top-to-bottom in sunset colors:
deep purple → pink → orange → yellow → pale yellow.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersAligned, LayersStacked, LayerAspectRatioGreaterThan,
    AllLayerBoundsInside, LayerSizeAtLeast, LayerRotationEquals,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, LayersHaveColorOrder,
    FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import LayerInsideFrame, LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_02_sunset_gradient",
    description="5 horizontal rectangle bands in sunset colors (purple, pink, orange, yellow, pale yellow).",
    rubrics=[
        # critical: exact count of 5 — prompt-explicit
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),                                       # 0 ★ "5 ... bands"
        ], weight=0.25, critical=[0]),

        # critical: same width (same dimensions + center_x), stacked top-to-bottom,
        # horizontal aspect, inside frame — all prompt-explicit
        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),             # 0 ★ "same width and similar height"
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=3.0),   # 1 ★ same width centers
            LayersStacked(layer_type="rectangle", axis="y", gap_px=0.0, tolerance=4.0),  # 2 ★ "stack ... top-to-bottom" + "flush"
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="horizontal"),  # 3 ★ "horizontal rectangle"
            LayerInsideFrame("rectangle"),                                           # 4 ★ "inside ... a frame"
            LayerGroupAllInSameFrame("rectangle", minimum=5),                        # 5 ★ all 5 in one frame
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=4.0),  # 6 ★ bands fit
            LayerSizeAtLeast(layer_type="rectangle", min_w=80.0, min_h=20.0),        # 7 ★ non-degenerate
            LayerRotationEquals(layer_type="rectangle", degrees=0.0, tolerance=2.0), # 8 ★ unrotated
            NoLayerFlipped(layer_type="rectangle"),                                  # 9 ★ no flips
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.3),        # 10 ★ rect-shaped (not pill)
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=2.0),     # 11 ★ frame not rotated
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),

        # critical: solid fills + 5 distinct colors + sunset color order + visible — prompt-explicit
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                # 0 ★
            DistinctSolidColors(minimum=5, tolerance=0.05),                          # 1 ★ 5 sunset colors
            LayersHaveColorOrder(                                                    # 2 ★ purple→pink→orange→yellow→pale yellow
                layer_type="rectangle",
                expected_rgbs=[
                    {"r": 0.30, "g": 0.10, "b": 0.50},   # deep purple
                    {"r": 1.00, "g": 0.50, "b": 0.70},   # pink
                    {"r": 1.00, "g": 0.60, "b": 0.20},   # orange
                    {"r": 1.00, "g": 0.90, "b": 0.20},   # yellow
                    {"r": 1.00, "g": 1.00, "b": 0.70},   # pale yellow
                ],
                sort_axis="y",
                tolerance=0.20,
            ),
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),    # 3 ★ catches alpha=0/opacity=0
            FillCountAtMost(layer_type="rectangle", max_count=1),                    # 4 ★ catches stacked fills
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),             # 5 ★ catches near-invisible
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5]),

        # critical: rectangle tool used — prompt-explicit
        EventRubric([
            ToolUsed("rectangle"),                                                   # 0 ★ "Click Rectangle tool"
            EventTypeCount("create_rectangle", equals=5),                            # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
