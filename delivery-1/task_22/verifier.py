"""
Task 22 — Tag pill row (in-scope replacement, no auto-layout).

4 same-size rounded rectangles (radius 999) placed side-by-side in a row
with a small gap, each a different pastel fill.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.property     import PropertyRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersAligned, LayersStacked, LayerSizeAtLeast,
    LayerRotationEquals, AllLayerBoundsInside, LayerAspectRatioGreaterThan,
)
from verifier.checks.fill_checks   import AllFillTypeIs, DistinctSolidColors
from verifier.checks.property_checks import (
    CornerRadiusAtLeast, LayerVisible, NoLayerFlipped,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_22_tag_pills",
    description="4 same-size rounded pills (radius ≥24) in a horizontal row, different pastel fills.",
    rubrics=[
        # critical: exactly 4 rectangles
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),                                    # 0 ★ "4"
        ], weight=0.20, critical=[0]),

        # critical: same-size, horizontal row, rounded pills, non-degenerate, on-frame
        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=3.0),          # 0 ★ "same-size"
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=5.0),# 1 ★ "same y-baseline"
            LayersStacked(layer_type="rectangle", axis="x", gap_px=8.0, tolerance=4.0),  # 2 ★ "row w/ small gap"
            CornerRadiusAtLeast(layer_type="rectangle", min_value=24.0),          # 3 ★ "rounded pills"
            LayerSizeAtLeast(layer_type="rectangle", min_w=40.0, min_h=20.0),     # 4 ★ non-degenerate
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=8.0),                                  # 5 ★ inside frame
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=1.5,
                                        axis="horizontal"),                       # 6 ★ pill aspect (wider than tall)
        ], weight=0.25, critical=[0, 1, 2, 3, 4, 5, 6]),

        # critical: solid fills + distinct pastels + actually visible
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                             # 0 ★
            DistinctSolidColors(minimum=4, tolerance=0.05),                       # 1 ★ "different pastel"
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5), # 2 ★ visible
        ], weight=0.25, critical=[0, 1, 2]),

        # critical: pills must look like pills (unrotated, unflipped)
        PropertyRubric([
            NoLayerFlipped(layer_type="rectangle"),                               # 0 ★ no scaleX/Y=-1
            LayerRotationEquals(layer_type="rectangle", degrees=0.0,
                                tolerance=2.0),                                   # 1 ★ unrotated
        ], weight=0.10, critical=[0, 1]),

        # critical: rectangle tool used
        EventRubric([
            ToolUsed("rectangle"),                                                # 0 ★
            EventTypeCount("create_rectangle", equals=4),                         # 1
        ], weight=0.20, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
