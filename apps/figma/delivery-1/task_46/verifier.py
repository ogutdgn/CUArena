"""
Task 46 — Histogram bars (SIMPLIFIED Medium → Easy).

5 thin vertical rectangles of varying heights, side-by-side with consistent gap,
all sharing a common bottom baseline.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersStacked, LayersAllShareEdge, FrameSizeEquals,
    AllLayerBoundsInside, LayerSizeAtLeast, LayerRotationEquals,
    AllLayerWidthFraction, FrameCountAtMost, LayerAspectRatioGreaterThan,
    LayerHeightRangeAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.page_checks   import LayerOnPage

task = Task(
    id="task_46_audio_waveform",
    description="5 vertical bars of varying heights, side-by-side, sharing a bottom baseline.",
    rubrics=[
        # critical: exactly 5 rectangles required
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),    # 0 ★ prompt: "5 vertical bars"
        ], weight=0.20, critical=[0]),

        # critical: side-by-side stacking, shared baseline, varying heights, vertical
        AlignmentRubric([
            LayersStacked(layer_type="rectangle", axis="x", gap_px=4.0, tolerance=25.0),         # 0 ★ prompt: "side-by-side"
            LayersAllShareEdge(layer_type="rectangle", edge="bottom", tolerance=15.0),           # 1 ★ prompt: "sharing a bottom baseline"
            LayerHeightRangeAtLeast(layer_type="rectangle", min_range=20.0),                     # 2 ★ prompt: "varying heights"
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=1.0, axis="vertical"),     # 3 ★ prompt: "vertical bars"
            FrameSizeEquals(width=1280, height=832, tolerance=25.0),                             # 4 frame size

            LayerSizeAtLeast(layer_type="rectangle", min_w=2, min_h=10),                         # 6 no degenerate
            AllLayerWidthFraction(inner_type="rectangle", parent_type="frame",                   # 7 sane width
                                  min_frac=0.001, max_frac=0.30),
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),               # 8 bars upright
            NoLayerFlipped(layer_type="rectangle"),                                              # 9 no mirror
            FrameCountAtMost(maximum=1),                                                         # 10 exactly one frame
        ], weight=0.20, critical=[0, 1, 2, 3]),

        # color rubric: distinct colors not strictly mandated (varying heights, not hues)
        # but sane fills + visibility are.
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),               # 0 ★ every bar needs a visible fill
            DistinctSolidColors(minimum=2, tolerance=0.15),         # 1
            FillCountAtMost("rectangle", max_count=1),              # 2 no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),       # 3 visible
            LayerVisible("rectangle"),                              # 4 alpha+visible+opacity
        ], weight=0.20, critical=[0]),

        # structural: bars in same frame on page 0
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="rectangle", minimum=5),  # 0 all 5 bars in one frame
            LayerOnPage(layer_type="rectangle", page_index=0),            # 1 on page 0
        ], weight=0.20, critical=[0]),

        # critical: rectangle tool mandated
        EventRubric([
            ToolUsed("rectangle"),                              # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCount("create_rectangle", equals=5),       # 1
        ], weight=0.20, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
