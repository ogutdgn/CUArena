"""
Task 06 — Gold burst (in-scope replacement, no boolean exclude).

8 lines radiating from a single center point at 45° intervals, gold stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayersEvenlyRotated, LayerSizeAtLeast
from verifier.checks.stroke_checks import (
    StrokeColorEquals, StrokeExists, StrokeWeightEquals,
    AllLayerStrokeVisible, AllStrokeColorEquals,
)
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

GOLD = {"r": 0.85, "g": 0.65, "b": 0.13}

task = Task(
    id="task_06_gold_star_exclude",
    description="8 lines radiating from a center at 45° intervals, with gold strokes.",
    rubrics=[
        # critical: exactly 8 lines — prompt-explicit
        FundamentalsRubric([
            ShapeCount("line", equals=8),                                             # 0 ★ "8 lines"
        ], weight=0.25, critical=[0]),

        # critical: from a center point + 45° intervals + non-degenerate + no flips — prompt-explicit
        AlignmentRubric([
            LayersConcentric(layer_type="line", tolerance=10.0),                      # 0 ★ "from a single center point"
            LayersEvenlyRotated(layer_type="line", n=8, step_deg=45.0, tolerance_deg=8.0),  # 1 ★ "45° intervals"
            LayerSizeAtLeast(layer_type="line", min_w=20.0, min_h=0.0),               # 2 ★ non-zero length
            NoLayerFlipped(layer_type="line"),                                        # 3 ★ no flips
        ], weight=0.25, critical=[0, 1, 2, 3]),

        # critical: stroke must exist + roughly gold + visible — prompt says "All lines the same color"
        # gold is verifier convention (loose tol).
        ColorRubric([
            StrokeColorEquals(layer_type="line", expected_rgb=GOLD, tolerance=0.25),  # 0 (loose tol — not critical)
            AllLayerStrokeVisible(layer_type="line", min_alpha=0.5, min_weight=0.5),  # 1 ★ all visible strokes
            AllStrokeColorEquals(layer_type="line", expected_rgb=GOLD, tolerance=0.30),# 2 ★ all-same gold
            LayerVisible(layer_type="line", min_opacity=0.5, min_alpha=0.0),          # 3 ★ layer visible (no fill needed)
        ], weight=0.25, critical=[1, 2, 3]),

        # critical: line tool used — prompt-explicit ("Use the line tool", "Click Line tool")
        EventRubric([
            ToolUsed("line"),                                                         # 0 ★ "Use the line tool"
            EventTypeCount("create_line", equals=8),                                  # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
