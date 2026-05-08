"""
Task 25 — Identical button row (in-scope replacement, no components).

3 identical 160×40 rectangles placed side-by-side, all same size and same color.
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
    LayersSameDimensions, LayersAligned, LayerSizeEquals, LayersStacked,
    LayerSizeAtLeast, AllLayerBoundsInside, LayerRotationEquals,
)
from verifier.checks.fill_checks   import AllFillTypeIs, LayersAllSameColor
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

task = Task(
    id="task_25_button_component",
    description="3 identical 160×40 rectangles in a horizontal row, all same color.",
    rubrics=[
        # exactly 3 rectangles
        FundamentalsRubric([
            ShapeCount("rectangle", equals=3),                                  # 0 ★ prompt: "3 identical rectangles"
        ], weight=0.20, critical=[0]),

        # identical size, horizontal row, shared y-baseline
        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=8.0),         # 0 ★ prompt: "identical rectangles" / "same size"
            LayerSizeEquals(layer_type="rectangle", width=160, height=40, tolerance=12.0),  # 1
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=12.0),         # 2 ★ prompt: "same y-baseline"
            LayersStacked(layer_type="rectangle", axis="x", gap_px=12.0, tolerance=12.0),   # 3 ★ prompt: "horizontal row with consistent spacing"
            LayerSizeAtLeast(layer_type="rectangle", min_w=40.0, min_h=20.0),    # 4   non-degenerate
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",
                                 tolerance=10.0),                                # 5
        ], weight=0.25, critical=[0, 2, 3]),

        # same solid color + visible
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                           # 0 ★ every rect needs a visible solid fill
            LayersAllSameColor(layer_type="rectangle", tolerance=0.12),         # 1 ★ prompt: "same color"
            LayerVisible(layer_type="rectangle", min_opacity=0.5,
                         min_alpha=0.5),                                        # 2
        ], weight=0.20, critical=[0, 1]),

        # identical button shape (no rotation/flip gimmicks)
        PropertyRubric([
            LayerRotationEquals(layer_type="rectangle", degrees=0.0,
                                tolerance=5.0),                                 # 0   unrotated
            NoLayerFlipped(layer_type="rectangle"),                             # 1   no flips
        ], weight=0.10, critical=[]),

        # rectangle tool used
        EventRubric([
            ToolUsed("rectangle"),                                              # 0   tool used (agent may shortcut)
            EventTypeCount("create_rectangle", equals=3),                       # 1
        ], weight=0.25, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
