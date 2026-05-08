"""
Task 34 — 4-fold symmetric snowflake (SIMPLIFIED Medium → Easy).

Navy frame + 4 white line branches rotated 90° each around the center.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayersEvenlyRotated, LayersConcentric, AllLayerBoundsInside,
    LayerSizeAtLeast, FrameCountAtMost, LayersSameDimensions, LayerRotationEquals,
    LinesShareEndpoint,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeColorEquals, StrokeExists, StrokeWeightEquals,
    AllStrokeColorEquals, AllStrokeExists, AllLayerStrokeVisible,
)
from verifier.checks.property_checks import LayerVisible, NoLayerFlipped
from verifier.checks.structure_checks import (
    LayerInsideFrame, LayerGroupAllInSameFrame, ChildCountAtLeast,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

NAVY  = {"r": 0.05, "g": 0.10, "b": 0.45}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_34_snowflake",
    description="Navy frame + 4 white line branches rotated 90° apart for 4-fold symmetry.",
    rubrics=[
        # critical: prompt mandates 4 line branches and a frame
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),  # 0 ★ "frame"
            ShapeCount("line", equals=4),           # 1 ★ "4 ... branches"
        ], weight=0.2, critical=[0, 1]),

        # critical: prompt mandates 90°-apart rotation, lines concentric (4-fold
        # symmetry around center), lines inside frame, non-degenerate, not flipped.
        AlignmentRubric([
            LayersEvenlyRotated(layer_type="line", n=4, step_deg=90.0, tolerance_deg=10.0),  # 0 ★ "rotated 90° apart"
            LayersConcentric(layer_type="line", tolerance=20.0),                              # 1 ★ "around the center"
            LayersSameDimensions(layer_type="line", tolerance=5.0),                           # 2 ★ same branch length
            AllLayerBoundsInside(inner_type="line", outer_type="frame", tolerance=4.0),       # 3 ★ branches inside frame
            LayerSizeAtLeast(layer_type="line", min_w=20, min_h=1),                           # 4 ★ no degenerate lines
            NoLayerFlipped(layer_type="line"),                                                # 5 ★ branches not flipped
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),                # 6 ★ frame upright
            LinesShareEndpoint(layer_type="line", minimum=4, tolerance=12.0),                 # 7 ★ all 4 branches meet at the center (true endpoint, not bbox)
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7]),

        # critical: navy frame + white branches are prompt-explicit, all visible
        ColorRubric([
            AllFillTypeIs("frame", kind="solid"),                                       # 0 ★
            SolidColorEquals(layer_type="frame", expected_rgb=NAVY, tolerance=0.30),    # 1 ★ "navy frame"
            AllStrokeExists("line"),                                                    # 2 ★ all branches have visible stroke
            AllStrokeColorEquals(layer_type="line", expected_rgb=WHITE, tolerance=0.20),# 3 ★ "white line branches" (every line)
            AllLayerStrokeVisible("line", min_alpha=0.5, min_weight=0.5),               # 4 ★ no transparent / 0-weight strokes
            FillCountAtMost("frame", max_count=1),                                      # 5 ★ no stacked frame fills
            FillOpacityAtLeast("frame", min_opacity=0.5),                               # 6 ★ visible frame
            LayerVisible("frame"),                                                      # 7 ★ visible frame layer
            LayerVisible("line"),                                                       # 8 ★ branches visible (no opacity=0)
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8]),

        # critical: shapes must all live in one frame (catches split-frame designs)
        StructureRubric([
            LayerInsideFrame("line"),                                       # 0 ★ branches in a frame
            LayerGroupAllInSameFrame(layer_type="line", minimum=4),         # 1 ★ all 4 in same frame
            ChildCountAtLeast("frame", minimum=4),                          # 2 ★ frame holds all branches
            FrameCountAtMost(maximum=1),                                    # 3 ★ exactly 1 top-level frame
        ], weight=0.2, critical=[0, 1, 2, 3]),

        # critical: must use line tool
        EventRubric([
            ToolUsed("line"),                       # 0 ★
            EventTypeCount("create_line", equals=4),# 1
        ], weight=0.2, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
