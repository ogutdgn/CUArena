"""
Task 06 — Asterisk burst (in-scope replacement).

8 lines radiating from a single center point at 45° intervals, gold stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LinesRadialFromSharedEndpoint
from verifier.checks.stroke_checks import StrokeColorEquals, StrokeExists
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

GOLD = {"r": 0.85, "g": 0.65, "b": 0.13}

task = Task(
    id="task_06_gold_star_exclude",
    description="8 lines radiating from a center point at 45° intervals.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("line", equals=8),                                                       # 0 ★ prompt: "8 lines"
        ], weight=0.22, critical=[0]),

        AlignmentRubric([
            LinesRadialFromSharedEndpoint(n=8,
                                          center_tolerance_px=20.0,
                                          angle_tolerance_deg=12.0,
                                          min_length_px=10.0,
                                          length_tolerance_px=80.0),                            # 0 ★ prompt: "from a center point at 45° intervals"
        ], weight=0.48, critical=[0]),

        ColorRubric([
            StrokeExists(layer_type="line"),                                                    # 0 ★ prompt: "All lines the same color"
            StrokeColorEquals(layer_type="line", expected_rgb=GOLD, tolerance=0.28),            # 1
        ], weight=0.15, critical=[0]),

        EventRubric([
            ToolUsed("line"),                                                                   # 0 ★ prompt: "Click Line tool"
            EventTypeCountAtLeast("create_line", minimum=8),                                    # 1
        ], weight=0.15, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
